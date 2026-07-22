"""
Structured error log viewer with filtering and analytics.
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    module: str
    message: str
    exception: Optional[str] = None
    request_path: Optional[str] = None
    user_id: Optional[int] = None
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'exception': self.exception,
            'request_path': self.request_path,
            'user_id': self.user_id,
        }


class LogViewer:
    """Parse and filter Django log files."""
    
    LOG_PATTERN = re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s'
        r'(?P<level>\w+)\s'
        r'(?P<module>[\w.]+):\s'
        r'(?P<message>.*)$'
    )
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    def get_log_files(self) -> List[Path]:
        """Get all log files sorted by date (newest first)."""
        if not self.log_dir.exists():
            return []
        files = sorted(self.log_dir.glob('*.log'), reverse=True)
        return files[:30]  # Last 30 days
    
    def parse_log_file(self, filepath: Path, limit: int = 1000) -> List[LogEntry]:
        """Parse a single log file into structured entries."""
        entries = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return []
        
        i = 0
        while i < len(lines) and len(entries) < limit:
            line = lines[i].strip()
            match = self.LOG_PATTERN.match(line)
            
            if match:
                entry = LogEntry(
                    timestamp=datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S,%f'),
                    level=match.group('level'),
                    module=match.group('module'),
                    message=match.group('message'),
                )
                
                # Capture exception traceback (following lines)
                exception_lines = []
                j = i + 1
                while j < len(lines) and not self.LOG_PATTERN.match(lines[j]):
                    exception_lines.append(lines[j].strip())
                    j += 1
                
                if exception_lines:
                    entry.exception = '\n'.join(exception_lines)
                
                entries.append(entry)
                i = j - 1
            
            i += 1
        
        return entries
    
    def get_entries(
        self,
        level: Optional[str] = None,
        module: Optional[str] = None,
        search: Optional[str] = None,
        hours: int = 24,
        limit: int = 500
    ) -> List[LogEntry]:
        """Get filtered log entries across all files."""
        cutoff = datetime.now() - timedelta(hours=hours)
        all_entries = []
        
        for log_file in self.get_log_files():
            entries = self.parse_log_file(log_file, limit=limit)
            for entry in entries:
                if entry.timestamp < cutoff:
                    continue
                if level and entry.level != level.upper():
                    continue
                if module and module not in entry.module:
                    continue
                if search and search.lower() not in entry.message.lower():
                    continue
                all_entries.append(entry)
        
        return sorted(all_entries, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def get_stats(self, hours: int = 24) -> Dict:
        """Get error statistics."""
        entries = self.get_entries(hours=hours, limit=10000)
        
        level_counts = {}
        module_counts = {}
        hourly_counts = {}
        
        for entry in entries:
            level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
            module_counts[entry.module] = module_counts.get(entry.module, 0) + 1
            
            hour_key = entry.timestamp.strftime('%H:00')
            hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1
        
        return {
            'total': len(entries),
            'by_level': level_counts,
            'by_module': dict(sorted(module_counts.items(), key=lambda x: -x[1])[:10]),
            'by_hour': hourly_counts,
            'error_rate': round((level_counts.get('ERROR', 0) / max(len(entries), 1)) * 100, 2),
        }


# Singleton
_log_viewer = None

def get_log_viewer() -> LogViewer:
    global _log_viewer
    if _log_viewer is None:
        _log_viewer = LogViewer()
    return _log_viewer