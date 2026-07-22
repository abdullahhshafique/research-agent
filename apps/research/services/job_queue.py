"""
In-memory job queue with ThreadPoolExecutor for background research processing.
Replaces synchronous view processing with true async execution.
"""

import threading
import queue
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    id: str
    query_id: int
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    stage: str = ""
    message: str = "Waiting in queue..."
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    cancelled: bool = False
    _listeners: list = field(default_factory=list, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def to_dict(self) -> dict:
        with self._lock:
            return {
                "id": self.id,
                "query_id": self.query_id,
                "status": self.status.value,
                "progress": self.progress,
                "stage": self.stage,
                "message": self.message,
                "error": self.error,
                "created_at": self.created_at,
                "started_at": self.started_at,
                "completed_at": self.completed_at,
                "cancelled": self.cancelled,
            }

    def update_progress(self, progress: int, stage: str, message: str):
        with self._lock:
            self.progress = progress
            self.stage = stage
            self.message = message
            self._notify_listeners()

    def add_listener(self, callback: Callable):
        with self._lock:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable):
        with self._lock:
            if callback in self._listeners:
                self._listeners.remove(callback)

    def _notify_listeners(self):
        for listener in self._listeners:
            try:
                listener(self.to_dict())
            except Exception as e:
                logger.error(f"Listener error: {e}")

    def refresh_from_queue(self):
        """Refresh job state from queue singleton."""
        queue_mgr = get_job_queue()
        refreshed = queue_mgr.get_job(self.id)
        if refreshed and refreshed is not self:
            with self._lock:
                self.status = refreshed.status
                self.progress = refreshed.progress
                self.stage = refreshed.stage
                self.message = refreshed.message
                self.error = refreshed.error
                self.result = refreshed.result
                self.completed_at = refreshed.completed_at


class ResearchJobQueue:
    """
    Singleton job queue manager for research processing.
    Uses ThreadPoolExecutor for worker threads.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, max_workers: int = 4):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_workers: int = 4):
        if self._initialized:
            return
        self._initialized = True

        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, Job] = {}
        self._queue = queue.Queue()
        self._shutdown = False
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        logger.info(f"ResearchJobQueue initialized with {max_workers} workers")

    def submit(self, query_id: int, func: Callable, *args, **kwargs) -> Job:
        """Submit a new research job to the queue."""
        job_id = str(uuid.uuid4())[:8]
        job = Job(
            id=job_id,
            query_id=query_id,
            func=func,
            args=args,
            kwargs=kwargs,
            status=JobStatus.QUEUED,
        )

        with self._lock:
            self.jobs[job_id] = job

        # Submit to thread pool
        future = self.executor.submit(self._run_job, job)
        job._future = future

        logger.info(f"Job {job_id} submitted for query {query_id}")
        return job

    def _run_job(self, job: Job):
        """Execute job with progress tracking and error handling."""
        if job.cancelled:
            job.status = JobStatus.CANCELLED
            return

        job.status = JobStatus.PROCESSING
        job.started_at = time.time()
        job.update_progress(0, "init", "Starting research...")

        try:
            # Inject progress callback into kwargs
            job.kwargs['_progress_callback'] = lambda p, s, m: job.update_progress(p, s, m)

            result = job.func(*job.args, **job.kwargs)
            job.result = result

            if not job.cancelled:
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.message = "Research complete!"
                job.completed_at = time.time()
                logger.info(f"Job {job.id} completed successfully")

        except Exception as e:
            if not job.cancelled:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = time.time()
                logger.error(f"Job {job.id} failed: {e}")

        finally:
            job._notify_listeners()

    def cancel(self, job_id: str) -> bool:
        """Cancel a pending or running job."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        with job._lock:
            if job.status in (JobStatus.PENDING, JobStatus.QUEUED, JobStatus.PROCESSING):
                job.cancelled = True
                job.status = JobStatus.CANCELLED
                job.message = "Cancelled by user"

                # Cancel future if possible
                if hasattr(job, '_future') and isinstance(job._future, Future):
                    job._future.cancel()

                logger.info(f"Job {job_id} cancelled")
                return True
        return False

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def get_job_by_query(self, query_id: int) -> Optional[Job]:
        for job in self.jobs.values():
            if job.query_id == query_id:
                return job
        return None

    def get_queue_status(self) -> dict:
        """Get current queue statistics."""
        statuses = [j.status for j in self.jobs.values()]
        return {
            "total_jobs": len(self.jobs),
            "pending": statuses.count(JobStatus.PENDING),
            "queued": statuses.count(JobStatus.QUEUED),
            "processing": statuses.count(JobStatus.PROCESSING),
            "completed": statuses.count(JobStatus.COMPLETED),
            "failed": statuses.count(JobStatus.FAILED),
            "cancelled": statuses.count(JobStatus.CANCELLED),
            "active_workers": len(self.executor._threads) if hasattr(self.executor, '_threads') else 'unknown',
            "max_workers": self.max_workers,
        }

    def get_all_jobs(self) -> list:
        """Get all jobs as dicts for monitoring."""
        return [j.to_dict() for j in self.jobs.values()]

    def _monitor_loop(self):
        """Background monitoring thread."""
        while not self._shutdown:
            time.sleep(5)
            self._cleanup_old_jobs()

    def _cleanup_old_jobs(self, keep: int = 100):
        """Remove oldest completed jobs to prevent memory bloat."""
        completed = [
            (jid, j) for jid, j in self.jobs.items()
            if j.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
        ]
        if len(completed) > keep:
            completed.sort(key=lambda x: x[1].completed_at or 0)
            for jid, _ in completed[:-keep]:
                del self.jobs[jid]

    def shutdown(self):
        """Graceful shutdown."""
        self._shutdown = True
        self.executor.shutdown(wait=True)
        logger.info("ResearchJobQueue shutdown complete")


# Module-level singleton accessor
def get_job_queue() -> ResearchJobQueue:
    return ResearchJobQueue()