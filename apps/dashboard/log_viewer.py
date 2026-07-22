"""
Structured log viewer for Django application logs.
"""
import os
import re
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    timestamp: str
    level: str
    module: str
    message: str
    exception: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'exception': self.exception,
        }


class LogViewer:
    LOG_PATTERN = re.compile(
        r'^(?P<level>\w+)\s+'
        r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+'
        r'(?P<module>[\w.]+)\s+'
        r'(?P<message>.*)$'
    )
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(settings.BASE_DIR, 'logs', 'django.log')
    
    def get_entries(self, level=None, module=None, search=None, hours=24):
        entries = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        if not os.path.exists(self.log_file):
            return entries
        
        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                current_entry = None
                current_exception = []
                
                for line in f:
                    line = line.rstrip('\n')
                    match = self.LOG_PATTERN.match(line)
                    
                    if match:
                        if current_entry:
                            current_entry.exception = '\n'.join(current_exception)
                            entries.append(current_entry)
                        
                        ts_str = match.group('timestamp')
                        try:
                            entry_time = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S,%f')
                        except ValueError:
                            entry_time = datetime.now()
                        
                        if entry_time < cutoff:
                            current_entry = None
                            current_exception = []
                            continue
                        
                        entry_level = match.group('level')
                        if level and entry_level != level:
                            current_entry = None
                            current_exception = []
                            continue
                        
                        entry_module = match.group('module')
                        if module and module.lower() not in entry_module.lower():
                            current_entry = None
                            current_exception = []
                            continue
                        
                        message = match.group('message')
                        if search and search.lower() not in message.lower():
                            current_entry = None
                            current_exception = []
                            continue
                        
                        current_entry = LogEntry(
                            timestamp=ts_str,
                            level=entry_level,
                            module=entry_module,
                            message=message
                        )
                        current_exception = []
                        
                    elif current_entry:
                        current_exception.append(line)
                
                if current_entry:
                    current_entry.exception = '\n'.join(current_exception)
                    entries.append(current_entry)
                    
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
        
        return entries
    
    def get_stats(self, hours=24):
        entries = self.get_entries(hours=hours)
        total = len(entries)
        by_level = {}
        by_hour = {}
        exception_count = 0
        
        for entry in entries:
            by_level[entry.level] = by_level.get(entry.level, 0) + 1
            if entry.exception:
                exception_count += 1
            try:
                hour = entry.timestamp[:13]
                by_hour[hour] = by_hour.get(hour, 0) + 1
            except:
                pass
        
        error_count = by_level.get('ERROR', 0)
        error_rate = round((error_count / total * 100), 2) if total > 0 else 0
        
        return {
            'total': total,
            'by_level': by_level,
            'by_hour': by_hour,
            'exception_count': exception_count,
            'error_rate': error_rate,
        }


def get_log_viewer():
    return LogViewer()