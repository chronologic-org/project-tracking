import hashlib
import secrets
import sqlite3
import streamlit as st
from typing import Optional
from src.database.db import get_db_connection

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password (str): The password to hash.
        
    Returns:
        str: The hashed password.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token() -> str:
    """
    Generate a random session token.
    
    Returns:
        str: A random session token.
    """
    return secrets.token_hex(32)

def authenticate_user(username: str, password: str) -> Optional[int]:
    """
    Authenticate a user and return their ID if successful.
    
    Args:
        username (str): The username to authenticate.
        password (str): The password to authenticate.
        
    Returns:
        Optional[int]: The user ID if authentication is successful, None otherwise.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute('''
            SELECT id FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            # Update session token and last login
            session_token = generate_session_token()
            cursor.execute('''
                UPDATE users 
                SET session_token = ?, last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (session_token, user_id))
            conn.commit()
            return user_id
        return None
    except sqlite3.Error as e:
        st.error(f"Error authenticating user: {str(e)}")
        return None
    finally:
        conn.close()

def add_user(username: str, password: str) -> None:
    """
    Add a new user to the users table.
    
    Args:
        username (str): The username of the new user.
        password (str): The password for the new user.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, last_login)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (username, password_hash))
        conn.commit()
        st.success(f"User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        st.warning(f"Username '{username}' already exists.")
    except sqlite3.Error as e:
        st.error(f"Error adding user: {str(e)}")
    finally:
        conn.close()

def get_user_by_session(session_token: str) -> Optional[int]:
    """
    Get user ID by session token.
    
    Args:
        session_token (str): The session token to look up.
        
    Returns:
        Optional[int]: The user ID if found, None otherwise.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_token = ?', (session_token,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        st.error(f"Error getting user by session: {str(e)}")
        return None
    finally:
        conn.close() 