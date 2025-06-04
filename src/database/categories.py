"""
Category management functions for the Team Project & Problem Tracker.
"""

import sqlite3
import streamlit as st
from src.database.db import get_db_connection

def add_category(name: str, points: int) -> None:
    """
    Add a new category to the categories table.
    
    Args:
        name (str): The name of the new category.
        points (int): The point value for the category.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name, points)
            VALUES (?, ?)
        ''', (name, points))
        conn.commit()
        st.success(f"Category '{name}' added successfully!")
    except sqlite3.IntegrityError:
        st.warning(f"Category '{name}' already exists.")
    except sqlite3.Error as e:
        st.error(f"Error adding category: {str(e)}")
    finally:
        conn.close()

def update_category_points(category_id: int, points: int) -> None:
    """
    Update the points value for a category.
    
    Args:
        category_id (int): The ID of the category to update.
        points (int): The new point value.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE categories 
            SET points = ?
            WHERE id = ?
        ''', (points, category_id))
        conn.commit()
        st.success("Category points updated successfully!")
    except sqlite3.Error as e:
        st.error(f"Error updating category points: {str(e)}")
    finally:
        conn.close() 