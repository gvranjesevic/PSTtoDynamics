"""
Database Configuration Module
============================

Provides optimized SQLite database connections with WAL mode and performance settings.
"""

import sqlite3
import logging
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration and connection management."""
    
    @staticmethod
    def optimize_connection(conn: sqlite3.Connection) -> None:
        """
        Apply performance optimizations to SQLite connection.
        
        Args:
            conn: SQLite connection to optimize
        """
        try:
            # Enable WAL mode for better concurrency and crash safety
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Set synchronous mode to NORMAL for better performance
            conn.execute("PRAGMA synchronous=NORMAL")
            
            # Increase cache size (default is 2MB, set to 64MB)
            conn.execute("PRAGMA cache_size=-65536")
            
            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys=ON")
            
            # Set temp store to memory for better performance
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Optimize for faster writes
            conn.execute("PRAGMA wal_autocheckpoint=1000")
            
            logger.debug("Database connection optimized with WAL mode and performance settings")
            
        except sqlite3.Error as e:
            logger.error(f"Failed to optimize database connection: {e}")
            raise
    
    @staticmethod
    @contextmanager
    def get_optimized_connection(db_path: str):
        """
        Context manager for optimized SQLite connections.
        
        Args:
            db_path: Path to SQLite database file
            
        Yields:
            Optimized SQLite connection
        """
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            DatabaseConfig.optimize_connection(conn)
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def create_optimized_connection(db_path: str) -> sqlite3.Connection:
        """
        Create an optimized SQLite connection.
        
        Args:
            db_path: Path to SQLite database file
            
        Returns:
            Optimized SQLite connection
        """
        try:
            conn = sqlite3.connect(db_path)
            DatabaseConfig.optimize_connection(conn)
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to create optimized database connection: {e}")
            raise


def migrate_existing_databases():
    """
    Migrate existing databases to use WAL mode.
    This function should be called during application startup.
    """
    database_files = [
        "analytics.db",
        "sync_engine.db", 
        "optimization.db",
        "predictions.db"
    ]
    
    for db_file in database_files:
        try:
            with DatabaseConfig.get_optimized_connection(db_file) as conn:
                # Check current journal mode
                result = conn.execute("PRAGMA journal_mode").fetchone()
                current_mode = result[0] if result else "unknown"
                
                if current_mode.upper() != "WAL":
                    logger.info(f"Migrating {db_file} from {current_mode} to WAL mode")
                else:
                    logger.debug(f"Database {db_file} already using WAL mode")
                    
        except (sqlite3.Error, FileNotFoundError) as e:
            logger.warning(f"Could not migrate database {db_file}: {e}")


if __name__ == "__main__":
    # Test the database configuration
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db = tmp.name
    
    try:
        # Test optimized connection
        with DatabaseConfig.get_optimized_connection(test_db) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
            conn.execute("INSERT INTO test (data) VALUES (?)", ("test data",))
            conn.commit()
            
            # Verify WAL mode is enabled
            result = conn.execute("PRAGMA journal_mode").fetchone()
            print(f"Journal mode: {result[0]}")
            
            # Verify synchronous mode
            result = conn.execute("PRAGMA synchronous").fetchone()
            print(f"Synchronous mode: {result[0]}")
            
        print("Database configuration test completed successfully")
        
    finally:
        os.unlink(test_db) 