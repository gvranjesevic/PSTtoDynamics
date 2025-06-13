#!/usr/bin/env python3
"""
Import Analytics Engine
======================

logger = logging.getLogger(__name__)

Phase 3.1 - Core analytics module for comprehensive import tracking and analysis.
Provides real-time metrics collection, performance analysis, and operational intelligence.

Features:
- Real-time import session tracking
- Performance metrics collection  
- Error pattern analysis
- Success rate monitoring
- Resource usage analytics
- Predictive import duration estimation
"""

import json
import logging
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import os
import sys

# Add parent directory to path for imports
sys.path.append('..')
import config

# Optional psutil for resource monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.debug("⚠️ psutil not available - resource monitoring disabled")


@dataclass
class ImportSession:
    """Represents a complete import session with all metrics."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_emails: int = 0
    processed_emails: int = 0
    successful_imports: int = 0
    failed_imports: int = 0
    duplicates_detected: int = 0
    contacts_created: int = 0
    contacts_found: int = 0
    batch_count: int = 0
    error_summary: Dict[str, int] = None
    performance_metrics: Dict[str, float] = None
    resource_usage: Dict[str, float] = None
    
    def __post_init__(self):
        if self.error_summary is None:
            self.error_summary = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.resource_usage is None:
            self.resource_usage = {}


@dataclass
class BatchMetrics:
    """Metrics for individual batch processing."""
    batch_id: str
    session_id: str
    batch_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    email_count: int = 0
    success_count: int = 0
    error_count: int = 0
    processing_time: float = 0.0
    emails_per_second: float = 0.0
    memory_usage_mb: float = 0.0


class AnalyticsDatabase:
    """Handles persistence of analytics data using SQLite."""
    
    def __init__(self, db_path: str = "Phase3_Analytics/analytics.db"):
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize the analytics database with required tables."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        cursor = self.connection.cursor()
        
        # Import sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_emails INTEGER DEFAULT 0,
                processed_emails INTEGER DEFAULT 0,
                successful_imports INTEGER DEFAULT 0,
                failed_imports INTEGER DEFAULT 0,
                duplicates_detected INTEGER DEFAULT 0,
                contacts_created INTEGER DEFAULT 0,
                contacts_found INTEGER DEFAULT 0,
                batch_count INTEGER DEFAULT 0,
                error_summary TEXT,
                performance_metrics TEXT,
                resource_usage TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Batch metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_metrics (
                batch_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                batch_number INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                email_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                processing_time REAL DEFAULT 0.0,
                emails_per_second REAL DEFAULT 0.0,
                memory_usage_mb REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES import_sessions (session_id)
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES import_sessions (session_id)
            )
        """)
        
        # Error tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                batch_id TEXT,
                error_type TEXT NOT NULL,
                error_message TEXT,
                error_count INTEGER DEFAULT 1,
                first_occurrence TEXT NOT NULL,
                last_occurrence TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES import_sessions (session_id)
            )
        """)
        
        self.connection.commit()
    
    def save_session(self, session: ImportSession):
        """Save or update an import session."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO import_sessions (
                session_id, start_time, end_time, total_emails, processed_emails,
                successful_imports, failed_imports, duplicates_detected,
                contacts_created, contacts_found, batch_count, error_summary,
                performance_metrics, resource_usage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.start_time.isoformat(),
            session.end_time.isoformat() if session.end_time else None,
            session.total_emails,
            session.processed_emails,
            session.successful_imports,
            session.failed_imports,
            session.duplicates_detected,
            session.contacts_created,
            session.contacts_found,
            session.batch_count,
            json.dumps(session.error_summary),
            json.dumps(session.performance_metrics),
            json.dumps(session.resource_usage)
        ))
        self.connection.commit()
    
    def save_batch_metrics(self, batch: BatchMetrics):
        """Save batch metrics."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO batch_metrics (
                batch_id, session_id, batch_number, start_time, end_time,
                email_count, success_count, error_count, processing_time,
                emails_per_second, memory_usage_mb
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch.batch_id,
            batch.session_id,
            batch.batch_number,
            batch.start_time.isoformat(),
            batch.end_time.isoformat() if batch.end_time else None,
            batch.email_count,
            batch.success_count,
            batch.error_count,
            batch.processing_time,
            batch.emails_per_second,
            batch.memory_usage_mb
        ))
        self.connection.commit()
    
    def get_session_history(self, limit: int = 50) -> List[Dict]:
        """Get recent import session history."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM import_sessions 
            ORDER BY start_time DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get performance summary for the last N days."""
        cursor = self.connection.cursor()
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(total_emails) as total_emails_processed,
                SUM(successful_imports) as total_successful,
                SUM(failed_imports) as total_failed,
                SUM(duplicates_detected) as total_duplicates,
                SUM(contacts_created) as total_contacts_created,
                AVG(CAST(json_extract(performance_metrics, '$.emails_per_minute') as REAL)) as avg_emails_per_minute,
                AVG(CAST(json_extract(performance_metrics, '$.total_duration_minutes') as REAL)) as avg_duration_minutes
            FROM import_sessions 
            WHERE start_time >= ? AND end_time IS NOT NULL
        """, (since_date,))
        
        result = cursor.fetchone()
        return dict(result) if result else {}


class ImportAnalytics:
    """Main analytics engine for import operations."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.current_session: Optional[ImportSession] = None
        self.current_batch: Optional[BatchMetrics] = None
        self.database = AnalyticsDatabase() if enabled else None
        self.session_lock = threading.Lock()
        self.start_memory = 0
        self.start_cpu_percent = 0
        
        # Performance tracking
        self.batch_times = []
        self.error_counts = defaultdict(int)
        self.email_processing_times = []
        
        logger.info("📊 Import Analytics Engine initialized" + (" (enabled)" if enabled else " (disabled)"))
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new import session."""
        if not self.enabled:
            return "analytics_disabled"
        
        with self.session_lock:
            if session_id is None:
                session_id = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_session = ImportSession(
                session_id=session_id,
                start_time=datetime.now()
            )
            
            # Capture initial system state
            if PSUTIL_AVAILABLE:
                try:
                    process = psutil.Process()
                    self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
                    self.start_cpu_percent = psutil.cpu_percent()
                except (Exception, AttributeError, TypeError, ValueError):
                    pass
            
            if self.database:
                self.database.save_session(self.current_session)
            
            logger.info("📊 Analytics session started: {session_id}")
            return session_id
    
    def end_session(self):
        """End the current import session."""
        if not self.enabled or not self.current_session:
            return
        
        with self.session_lock:
            self.current_session.end_time = datetime.now()
            
            # Calculate final metrics
            duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
            
            # Performance metrics
            if self.current_session.processed_emails > 0:
                emails_per_minute = (self.current_session.processed_emails / duration) * 60
                self.current_session.performance_metrics.update({
                    'total_duration_seconds': duration,
                    'total_duration_minutes': duration / 60,
                    'emails_per_second': self.current_session.processed_emails / duration,
                    'emails_per_minute': emails_per_minute,
                    'success_rate': self.current_session.successful_imports / self.current_session.processed_emails,
                    'duplicate_rate': self.current_session.duplicates_detected / self.current_session.processed_emails,
                    'average_batch_time': sum(self.batch_times) / len(self.batch_times) if self.batch_times else 0
                })
            
            # Resource usage metrics
            if PSUTIL_AVAILABLE:
                try:
                    process = psutil.Process()
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    self.current_session.resource_usage.update({
                        'peak_memory_mb': current_memory,
                        'memory_increase_mb': current_memory - self.start_memory,
                        'final_cpu_percent': psutil.cpu_percent()
                    })
                except (Exception, AttributeError, TypeError, ValueError):
                    pass
            
            if self.database:
                self.database.save_session(self.current_session)
            
            logger.info("📊 Analytics session completed: {self.current_session.session_id}")
            logger.debug("   📧 Processed: {self.current_session.processed_emails} emails")
            logger.debug("   ✅ Success rate: {self.current_session.performance_metrics.get('success_rate', 0):.1%}")
            logger.debug("   ⏱️ Duration: {duration/60:.1f} minutes")
            logger.debug("   ⚡ Speed: {self.current_session.performance_metrics.get('emails_per_minute', 0):.1f} emails/min")
    
    def start_batch(self, batch_number: int, email_count: int) -> str:
        """Start tracking a new batch."""
        if not self.enabled or not self.current_session:
            return "analytics_disabled"
        
        batch_id = f"{self.current_session.session_id}_batch_{batch_number}"
        
        self.current_batch = BatchMetrics(
            batch_id=batch_id,
            session_id=self.current_session.session_id,
            batch_number=batch_number,
            start_time=datetime.now(),
            email_count=email_count
        )
        
        # Capture memory usage at batch start
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                self.current_batch.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            except (Exception, AttributeError, TypeError, ValueError):
                pass
        
        return batch_id
    
    def end_batch(self, success_count: int, error_count: int = 0):
        """End the current batch and record metrics."""
        if not self.enabled or not self.current_batch:
            return
        
        self.current_batch.end_time = datetime.now()
        self.current_batch.success_count = success_count
        self.current_batch.error_count = error_count
        
        # Calculate processing metrics
        duration = (self.current_batch.end_time - self.current_batch.start_time).total_seconds()
        self.current_batch.processing_time = duration
        
        if duration > 0:
            self.current_batch.emails_per_second = self.current_batch.email_count / duration
        
        # Track for session-level analytics
        self.batch_times.append(duration)
        
        # Update session totals
        if self.current_session:
            self.current_session.batch_count += 1
            self.current_session.processed_emails += self.current_batch.email_count
            self.current_session.successful_imports += success_count
            self.current_session.failed_imports += error_count
        
        # Save batch metrics
        if self.database:
            self.database.save_batch_metrics(self.current_batch)
        
        logger.debug("   📦 Batch {self.current_batch.batch_number}: {success_count}/{self.current_batch.email_count} emails processed in {duration:.1f}s")
    
    def record_error(self, error_type: str, error_message: str = ""):
        """Record an error occurrence."""
        if not self.enabled or not self.current_session:
            return
        
        self.error_counts[error_type] += 1
        self.current_session.error_summary[error_type] = self.error_counts[error_type]
        
        # Log to database if available
        if self.database:
            cursor = self.database.connection.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO error_tracking (
                    session_id, batch_id, error_type, error_message,
                    first_occurrence, last_occurrence
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.current_session.session_id,
                self.current_batch.batch_id if self.current_batch else None,
                error_type,
                error_message,
                now,
                now
            ))
            self.database.connection.commit()
    
    def record_duplicate_detected(self):
        """Record a duplicate email detection."""
        if self.current_session:
            self.current_session.duplicates_detected += 1
    
    def record_contact_created(self):
        """Record a new contact creation."""
        if self.current_session:
            self.current_session.contacts_created += 1
    
    def record_contact_found(self):
        """Record an existing contact found."""
        if self.current_session:
            self.current_session.contacts_found += 1
    
    def set_total_emails(self, count: int):
        """Set the total expected email count for the session."""
        if self.current_session:
            self.current_session.total_emails = count
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        if not self.enabled or not self.current_session:
            return {"analytics_enabled": False}
        
        elapsed = (datetime.now() - self.current_session.start_time).total_seconds()
        
        stats = {
            "analytics_enabled": True,
            "session_id": self.current_session.session_id,
            "elapsed_time_minutes": elapsed / 60,
            "total_emails": self.current_session.total_emails,
            "processed_emails": self.current_session.processed_emails,
            "successful_imports": self.current_session.successful_imports,
            "failed_imports": self.current_session.failed_imports,
            "duplicates_detected": self.current_session.duplicates_detected,
            "contacts_created": self.current_session.contacts_created,
            "contacts_found": self.current_session.contacts_found,
            "batch_count": self.current_session.batch_count,
            "current_success_rate": (
                self.current_session.successful_imports / self.current_session.processed_emails
                if self.current_session.processed_emails > 0 else 0
            ),
            "estimated_completion_minutes": (
                (elapsed / self.current_session.processed_emails * self.current_session.total_emails - elapsed) / 60
                if self.current_session.processed_emails > 0 and self.current_session.total_emails > 0 else 0
            )
        }
        
        return stats
    
    def get_session_history(self, limit: int = 10) -> List[Dict]:
        """Get recent session history."""
        if not self.enabled or not self.database:
            return []
        
        return self.database.get_session_history(limit)
    
    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get performance summary for recent operations."""
        if not self.enabled or not self.database:
            return {"analytics_enabled": False}
        
        summary = self.database.get_performance_summary(days)
        summary["analytics_enabled"] = True
        summary["period_days"] = days
        
        return summary
    
    def export_analytics(self, format_type: str = "json") -> str:
        """Export analytics data in specified format."""
        if not self.enabled:
            return "Analytics disabled"
        
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "current_session": asdict(self.current_session) if self.current_session else None,
            "session_history": self.get_session_history(50),
            "performance_summary": self.get_performance_summary(30)
        }
        
        if format_type.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)


# Global analytics instance
analytics = ImportAnalytics(enabled=getattr(FeatureFlags, 'IMPORT_ANALYTICS', False))


def get_analytics() -> ImportAnalytics:
    """Get the global analytics instance."""
    return analytics


if __name__ == "__main__":
    # Test the analytics engine
    logger.debug("🧪 Testing Import Analytics Engine")
    
    # Create test analytics instance
    test_analytics = ImportAnalytics(enabled=True)
    
    # Simulate an import session
    session_id = test_analytics.start_session()
    test_analytics.set_total_emails(100)
    
    # Simulate batch processing
    for batch_num in range(1, 6):
        batch_id = test_analytics.start_batch(batch_num, 20)
        time.sleep(0.1)  # Simulate processing time
        test_analytics.end_batch(success_count=18, error_count=2)
        test_analytics.record_contact_created()
        test_analytics.record_duplicate_detected()
    
    # Add some errors
    test_analytics.record_error("authentication_failed", "Token expired")
    test_analytics.record_error("network_timeout", "Connection timeout")
    
    # End session
    test_analytics.end_session()
    
    # Display results
    logger.debug("\n📊 Test Results:")
    print(json.dumps(test_analytics.get_current_stats(), indent=2))
    
    logger.debug("\n📈 Performance Summary:")
    print(json.dumps(test_analytics.get_performance_summary(), indent=2))
    
    logger.debug("\n✅ Import Analytics Engine test completed!") 