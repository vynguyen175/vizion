"""
Database migration to add OAuth and notification support.
Adds new columns to the users table for OAuth providers and email notifications.
"""

import os
from sqlalchemy import create_engine, text
import streamlit as st

def migrate_database():
    """Add OAuth and notification columns to users table."""
    
    try:
        # Get database URL
        try:
            DATABASE_URL = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", "sqlite:///vizion.db"))
        except:
            DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vizion.db")
        
        # Create engine
        if DATABASE_URL.startswith("sqlite"):
            engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(DATABASE_URL)
        
        print("Connected to database:", DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if columns already exist
            if DATABASE_URL.startswith("sqlite"):
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
            else:  # PostgreSQL
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='users'"
                ))
                columns = [row[0] for row in result]
            
            print(f"Existing columns: {columns}")
            
            # Add new columns if they don't exist
            new_columns = {
                'oauth_provider': 'VARCHAR',
                'oauth_id': 'VARCHAR',
                'profile_picture': 'VARCHAR',
                'email_notifications': 'VARCHAR DEFAULT \'true\'',
                'last_notification_sent': 'TIMESTAMP'
            }
            
            for col_name, col_type in new_columns.items():
                if col_name not in columns:
                    try:
                        if DATABASE_URL.startswith("sqlite"):
                            # SQLite syntax
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                        else:
                            # PostgreSQL syntax
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        print(f"[OK] Added column: {col_name}")
                    except Exception as e:
                        print(f"[ERROR] Error adding {col_name}: {e}")
                else:
                    print(f"[SKIP] Column {col_name} already exists")
            
            # Update existing users to have oauth_provider = 'email'
            try:
                conn.execute(text(
                    "UPDATE users SET oauth_provider = 'email' "
                    "WHERE oauth_provider IS NULL"
                ))
                conn.commit()
                print("[OK] Updated existing users with oauth_provider='email'")
            except Exception as e:
                print(f"[ERROR] Error updating users: {e}")
            
            # Make password_hash nullable for OAuth users
            try:
                if DATABASE_URL.startswith("postgres"):
                    conn.execute(text(
                        "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL"
                    ))
                    conn.commit()
                    print("[OK] Made password_hash nullable")
            except Exception as e:
                print(f"Note: Could not make password_hash nullable: {e}")
        
        print("\n[SUCCESS] Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION - OAuth & Notifications Support")
    print("=" * 60)
    print()
    
    migrate_database()
