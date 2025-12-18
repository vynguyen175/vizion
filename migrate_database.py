"""
Database migration script to add ML columns to analysis_history table.
Run this once to update your existing database.
"""

import sqlite3
import os

db_path = "csv_analyzer.db"

if not os.path.exists(db_path):
    print("[ERROR] Database file not found!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(analysis_history)")
    columns = [column[1] for column in cursor.fetchall()]
    
    new_columns = [
        ('ml_task_type', 'TEXT'),
        ('target_column', 'TEXT'),
        ('model_type', 'TEXT'),
        ('accuracy', 'TEXT'),
        ('notebook_path', 'TEXT'),
        ('notebook_executed', 'TEXT')
    ]
    
    print("Checking existing columns...")
    print(f"Current columns: {columns}")
    print()
    
    for col_name, col_type in new_columns:
        if col_name not in columns:
            print(f"Adding column: {col_name} ({col_type})")
            cursor.execute(f"ALTER TABLE analysis_history ADD COLUMN {col_name} {col_type}")
            print(f"[SUCCESS] Added {col_name}")
        else:
            print(f"[SKIP] Column {col_name} already exists")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("[SUCCESS] Database migration completed successfully!")
    print("="*60)
    print("\nYou can now run: streamlit run app.py")
    
except Exception as e:
    print(f"[ERROR] Error during migration: {e}")
    print("\nIf you continue to have issues, you can:")
    print("1. Close Streamlit app completely")
    print("2. Rename csv_analyzer.db to csv_analyzer_old.db")
    print("3. Run the app again to create a fresh database")
