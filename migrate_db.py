"""
Database migration script to add new columns to existing products
Run this script to update your existing database with new category and min_stock_level fields
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = os.path.join('instance', 'inventory.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database with updated schema.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(product)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add category column if it doesn't exist
        if 'category' not in columns:
            cursor.execute("ALTER TABLE product ADD COLUMN category VARCHAR(50) DEFAULT 'General'")
            print("+ Added 'category' column to product table")
        else:
            print("+ 'category' column already exists")
        
        # Add min_stock_level column if it doesn't exist
        if 'min_stock_level' not in columns:
            cursor.execute("ALTER TABLE product ADD COLUMN min_stock_level INTEGER DEFAULT 5")
            print("+ Added 'min_stock_level' column to product table")
        else:
            print("+ 'min_stock_level' column already exists")
        
        # Update existing products with default values if they're NULL
        cursor.execute("UPDATE product SET category = 'General' WHERE category IS NULL")
        cursor.execute("UPDATE product SET min_stock_level = 5 WHERE min_stock_level IS NULL")
        
        conn.commit()
        print("+ Database migration completed successfully!")
        
    except Exception as e:
        print(f"- Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    migrate_database()
    print("Migration process finished.")
