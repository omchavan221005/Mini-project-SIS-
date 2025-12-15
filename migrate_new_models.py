"""
Database migration script to add new models for enhanced SIS features
Run this script to update your database with User, Notification, and ActivityLog tables
"""

import sqlite3
import os
from datetime import datetime

def migrate_new_models():
    db_path = os.path.join('instance', 'inventory.db')
    
    if not os.path.exists(db_path):
        print("Database not found. New database will be created when app runs.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create User table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(120) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                email VARCHAR(120) UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        print("+ Created User table")
        
        # Create Notification table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                type VARCHAR(20) NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("+ Created Notification table")
        
        # Create ActivityLog table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("+ Created ActivityLog table")
        
        # Add new columns to Student table if they don't exist
        cursor.execute("PRAGMA table_info(student)")
        student_columns = [column[1] for column in cursor.fetchall()]
        
        if 'email' not in student_columns:
            cursor.execute("ALTER TABLE student ADD COLUMN email VARCHAR(120)")
            print("+ Added email column to Student table")
        
        if 'phone' not in student_columns:
            cursor.execute("ALTER TABLE student ADD COLUMN phone VARCHAR(15)")
            print("+ Added phone column to Student table")
        
        if 'return_date' not in student_columns:
            cursor.execute("ALTER TABLE student ADD COLUMN return_date DATE")
            print("+ Added return_date column to Student table")
        
        # Insert default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM user WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO user (username, password, role, email)
                VALUES ('admin', 'admin', 'admin', 'admin@sis.com')
            ''')
            print("+ Created default admin user")
        
        conn.commit()
        print("+ Database migration completed successfully!")
        
    except Exception as e:
        print(f"- Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting new models migration...")
    migrate_new_models()
    print("Migration process finished.")
