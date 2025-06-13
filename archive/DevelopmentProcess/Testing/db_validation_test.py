#!/usr/bin/env python3
"""
Analytics Database Validation Test
==================================
"""

logger = logging.getLogger(__name__)

import sqlite3
import logging
import os

def validate_databases():
    logger.info("📊 Analytics Database Validation:")
    logger.debug("=" * 40)
    
    db_files = ['analytics.db', 'timeline_analysis.db', 'sender_analysis.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                logger.debug("  ✅ {db_file}: {len(tables)} tables - {tables}")
                
                # Count records in each table
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    logger.debug("     📁 {table}: {count} records")
                
                conn.close()
            except Exception as e:
                logger.debug("  ❌ {db_file}: Error - {e}")
        else:
            logger.debug("  ⚠️ {db_file}: Not found")
    
    # Check reports directory
    reports_dir = "reports"
    if os.path.exists(reports_dir):
        reports = [f for f in os.listdir(reports_dir) if f.endswith(('.json', '.txt'))]
        logger.debug("\n📋 Analytics Reports: {len(reports)} files")
        for report in reports[-3:]:  # Show last 3
            logger.debug("  📄 {report}")
    else:
        logger.debug("\n📋 Reports directory: Not found")

if __name__ == "__main__":
    validate_databases() 