import sqlite3
import streamlit as st
from typing import Optional

# Constants
DATABASE_NAME = "tracker.db"

def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: A connection to the SQLite database.
    """
    return sqlite3.connect(DATABASE_NAME)

def init_db() -> None:
    """
    Initialize the SQLite database with required tables if they don't exist.
    Creates tables for users, categories, projects, problems, and their relationships.
    Also adds completed_at columns to projects and problems tables if they don't exist.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Create users table with password and session_token
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                session_token TEXT,
                last_login TIMESTAMP
            )
        ''')
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                points INTEGER NOT NULL
            )
        ''')
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # Create problems table with explicit INTEGER type for claimed_by_user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'Open',
                project_id INTEGER,
                claimed_by_user_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (claimed_by_user_id) REFERENCES users(id)
            )
        ''')
        
        # Create junction tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problem_categories (
                problem_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                PRIMARY KEY (problem_id, category_id),
                FOREIGN KEY (problem_id) REFERENCES problems(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_workers (
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (project_id, user_id),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Add completed_at columns if they don't exist
        try:
            cursor.execute('ALTER TABLE projects ADD COLUMN completed_at TIMESTAMP')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            cursor.execute('ALTER TABLE problems ADD COLUMN completed_at TIMESTAMP')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {str(e)}")
    finally:
        conn.close()

def reset_database() -> None:
    """
    Reset the database by dropping all tables and reinitializing them.
    This should only be used when there are schema changes that need to be applied.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Drop all tables
        cursor.execute("DROP TABLE IF EXISTS problem_categories")
        cursor.execute("DROP TABLE IF EXISTS project_workers")
        cursor.execute("DROP TABLE IF EXISTS problems")
        cursor.execute("DROP TABLE IF EXISTS projects")
        cursor.execute("DROP TABLE IF EXISTS categories")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error resetting database: {str(e)}")
    finally:
        conn.close()
    
    # Reinitialize the database with the new schema
    init_db() 