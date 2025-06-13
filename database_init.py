#!/usr/bin/env python3
"""
Database Initialization Script
=============================

Ensures all required database tables are created for the PST-to-Dynamics application.
This script should be run on first setup or when database schema changes.
"""

import sqlite3
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Handles initialization of all application databases."""
    
    def __init__(self):
        self.databases = {
            'analytics': 'analytics.db',
            'optimization': 'optimization.db', 
            'predictions': 'predictions.db',
            'phase3_analytics': 'Phase3_Analytics/analytics.db',
            'phase3_timeline': 'Phase3_Analytics/timeline_analysis.db',
            'phase3_sender': 'Phase3_Analytics/sender_analysis.db'
        }
        
    def initialize_all_databases(self) -> bool:
        """Initialize all application databases."""
        logger.info("🔧 Initializing all application databases...")
        
        success = True
        for db_name, db_path in self.databases.items():
            try:
                if self.initialize_database(db_name, db_path):
                    logger.info(f"✅ Initialized {db_name} database: {db_path}")
                else:
                    logger.error(f"❌ Failed to initialize {db_name} database")
                    success = False
            except Exception as e:
                logger.error(f"❌ Error initializing {db_name}: {e}")
                success = False
        
        return success
    
    def initialize_database(self, db_name: str, db_path: str) -> bool:
        """Initialize a specific database with its required tables."""
        try:
            # Create directory if needed
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Initialize tables based on database type
            if db_name == 'analytics':
                self._create_analytics_tables(cursor)
            elif db_name == 'optimization':
                self._create_optimization_tables(cursor)
            elif db_name == 'predictions':
                self._create_predictions_tables(cursor)
            elif db_name.startswith('phase3'):
                self._create_phase3_tables(cursor, db_name)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing database {db_path}: {e}")
            return False
    
    def _create_analytics_tables(self, cursor: sqlite3.Cursor):
        """Create tables for the main analytics database."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS import_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                total_emails INTEGER DEFAULT 0,
                successful_imports INTEGER DEFAULT 0,
                failed_imports INTEGER DEFAULT 0,
                skipped_emails INTEGER DEFAULT 0,
                processing_time_seconds REAL DEFAULT 0,
                pst_file_path TEXT,
                user_name TEXT,
                configuration TEXT,
                status TEXT DEFAULT 'active'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS batch_metrics (
                batch_id TEXT PRIMARY KEY,
                session_id TEXT,
                batch_number INTEGER,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                emails_processed INTEGER DEFAULT 0,
                processing_time_seconds REAL DEFAULT 0,
                memory_usage_mb REAL DEFAULT 0,
                cpu_usage_percent REAL DEFAULT 0,
                errors_count INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES import_sessions(session_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                FOREIGN KEY (session_id) REFERENCES import_sessions(session_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS error_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                email_subject TEXT,
                email_sender TEXT,
                stack_trace TEXT,
                FOREIGN KEY (session_id) REFERENCES import_sessions(session_id)
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
    
    def _create_optimization_tables(self, cursor: sqlite3.Cursor):
        """Create tables for the optimization database."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                context TEXT,
                recommendations TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS optimization_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                recommendation_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                estimated_improvement TEXT,
                implementation_effort TEXT,
                status TEXT DEFAULT 'pending'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS resource_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                prediction_type TEXT NOT NULL,
                target_date DATE,
                predicted_value REAL NOT NULL,
                confidence_score REAL,
                input_parameters TEXT,
                model_version TEXT,
                actual_value REAL
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
    
    def _create_predictions_tables(self, cursor: sqlite3.Cursor):
        """Create tables for the predictions database."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS timeline_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_email TEXT NOT NULL,
                prediction_date DATE NOT NULL,
                predicted_interaction_probability REAL,
                predicted_interaction_type TEXT,
                confidence_score REAL,
                model_features TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actual_outcome TEXT,
                accuracy_score REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sender_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email TEXT NOT NULL,
                forecast_period TEXT NOT NULL,
                predicted_email_count INTEGER,
                predicted_response_rate REAL,
                predicted_importance_score REAL,
                confidence_interval_low REAL,
                confidence_interval_high REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actual_count INTEGER,
                forecast_accuracy REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS business_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                insight_title TEXT NOT NULL,
                insight_description TEXT NOT NULL,
                insight_data TEXT,
                confidence_score REAL,
                business_impact TEXT,
                recommended_actions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS import_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pst_file_path TEXT NOT NULL,
                predicted_total_emails INTEGER,
                predicted_processing_time_minutes REAL,
                predicted_success_rate REAL,
                predicted_memory_usage_mb REAL,
                predicted_disk_space_mb REAL,
                model_confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actual_total_emails INTEGER,
                actual_processing_time_minutes REAL,
                prediction_accuracy REAL
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
    
    def _create_phase3_tables(self, cursor: sqlite3.Cursor, db_name: str):
        """Create tables for Phase 3 analytics databases."""
        if 'timeline' in db_name:
            self._create_timeline_tables(cursor)
        elif 'sender' in db_name:
            self._create_sender_tables(cursor)
        else:
            self._create_analytics_tables(cursor)  # Default analytics tables
    
    def _create_timeline_tables(self, cursor: sqlite3.Cursor):
        """Create timeline analysis tables."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS timeline_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date DATE NOT NULL,
                total_contacts INTEGER,
                contacts_with_gaps INTEGER,
                average_gap_days REAL,
                max_gap_days INTEGER,
                completeness_score REAL,
                analysis_metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS contact_timelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                contact_email TEXT NOT NULL,
                total_emails INTEGER,
                date_range_days INTEGER,
                largest_gap_days INTEGER,
                gap_periods TEXT,
                timeline_score REAL,
                risk_level TEXT,
                recommendations TEXT,
                FOREIGN KEY (analysis_id) REFERENCES timeline_analysis(id)
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
    
    def _create_sender_tables(self, cursor: sqlite3.Cursor):
        """Create sender analysis tables."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS sender_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date DATE NOT NULL,
                total_senders INTEGER,
                unique_domains INTEGER,
                analysis_period_days INTEGER,
                top_sender_threshold INTEGER,
                analysis_metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sender_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                sender_email TEXT NOT NULL,
                sender_name TEXT,
                email_count INTEGER,
                first_email_date DATE,
                last_email_date DATE,
                communication_frequency TEXT,
                sender_domain TEXT,
                importance_score REAL,
                relationship_strength TEXT,
                email_pattern TEXT,
                FOREIGN KEY (analysis_id) REFERENCES sender_analysis(id)
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
    
    def verify_database_integrity(self) -> Dict[str, bool]:
        """Verify that all databases are properly initialized."""
        results = {}
        
        for db_name, db_path in self.databases.items():
            try:
                if not os.path.exists(db_path):
                    results[db_name] = False
                    continue
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Each database should have at least one table
                results[db_name] = len(tables) > 0
                
                conn.close()
                
            except Exception as e:
                logger.error(f"Error verifying {db_name}: {e}")
                results[db_name] = False
        
        return results
    
    def get_database_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all databases."""
        stats = {}
        
        for db_name, db_path in self.databases.items():
            try:
                if not os.path.exists(db_path):
                    stats[db_name] = {'exists': False, 'size_kb': 0, 'tables': []}
                    continue
                
                file_size = os.path.getsize(db_path) / 1024  # KB
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                table_counts = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                
                conn.close()
                
                stats[db_name] = {
                    'exists': True,
                    'size_kb': round(file_size, 2),
                    'tables': tables,
                    'table_counts': table_counts
                }
                
            except Exception as e:
                logger.error(f"Error getting stats for {db_name}: {e}")
                stats[db_name] = {'exists': False, 'error': str(e)}
        
        return stats

def main():
    """Main function to initialize databases."""
    print("🔧 PST-to-Dynamics Database Initialization")
    print("=" * 50)
    
    initializer = DatabaseInitializer()
    
    # Initialize all databases
    if initializer.initialize_all_databases():
        print("✅ All databases initialized successfully!")
    else:
        print("❌ Some databases failed to initialize!")
        return False
    
    # Verify integrity
    print("\n🔍 Verifying database integrity...")
    integrity_results = initializer.verify_database_integrity()
    
    all_good = True
    for db_name, is_valid in integrity_results.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {db_name}: {'OK' if is_valid else 'FAILED'}")
        if not is_valid:
            all_good = False
    
    # Show statistics
    print("\n📊 Database Statistics:")
    stats = initializer.get_database_stats()
    
    for db_name, db_stats in stats.items():
        if db_stats.get('exists', False):
            tables = db_stats.get('tables', [])
            size = db_stats.get('size_kb', 0)
            print(f"  {db_name}: {len(tables)} tables, {size} KB")
        else:
            print(f"  {db_name}: Not found or error")
    
    print("\n🎉 Database initialization complete!")
    return all_good

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 