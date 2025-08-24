#!/usr/bin/env python3
"""
Database Reset Script
This script will drop and recreate the database with the new schema.
Run this only when you want to reset all data.
"""

import os
import sqlite3
from app import app, db

def reset_database():
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("✓ All tables dropped")
            
            # Create all tables with new schema
            db.create_all()
            print("✓ New database schema created")
            
            print("\nDatabase has been reset successfully!")
            print("You can now run your Flask application with the new schema.")
            print("\nNew features:")
            print("- Each student gets a unique product instance")
            print("- Products are tracked as assigned/unassigned")
            print("- Assignment dates are recorded")
            
        except Exception as e:
            print(f"Error during database reset: {e}")
            print("Trying manual database file removal...")
            
            # Try to manually remove the database file
            db_path = "instance/inventory.db"
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    print("✓ Old database file removed")
                    
                    # Create new database
                    db.create_all()
                    print("✓ New database schema created")
                    print("\nDatabase has been reset successfully!")
                    
                except Exception as e2:
                    print(f"Error during manual reset: {e2}")
                    print("Please manually delete the 'instance/inventory.db' file and restart the application.")

def check_database_integrity():
    """Check if the database has integrity issues"""
    db_path = "instance/inventory.db"
    if not os.path.exists(db_path):
        print("No database file found.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_key_check")
        result = cursor.fetchall()
        
        if result:
            print("⚠️  Foreign key constraint violations found:")
            for row in result:
                print(f"   {row}")
            return False
        else:
            print("✓ Database integrity check passed")
            return True
            
    except Exception as e:
        print(f"Error checking database integrity: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Check if database file exists
    db_path = "instance/inventory.db"
    if os.path.exists(db_path):
        print(f"Found existing database at {db_path}")
        
        # Check database integrity first
        print("Checking database integrity...")
        if check_database_integrity():
            response = input("Database appears healthy. Do you still want to reset it? (y/N): ")
        else:
            print("Database has integrity issues. Resetting is recommended.")
            response = input("Do you want to reset the database? This will delete ALL data! (y/N): ")
        
        if response.lower() == 'y':
            reset_database()
        else:
            print("Database reset cancelled.")
    else:
        print("No existing database found. Creating new one...")
        reset_database()
