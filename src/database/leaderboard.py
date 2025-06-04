"""
Leaderboard functionality for tracking and displaying user points.
"""

import sqlite3
import streamlit as st
from src.database.db import get_db_connection

def get_user_points(user_id: int) -> int:
    """
    Calculate total points earned by a user from completed problems.
    
    Args:
        user_id (int): The ID of the user to calculate points for.
        
    Returns:
        int: Total points earned by the user.
        
    Raises:
        sqlite3.Error: If there is an error querying the database.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(c.points)
            FROM problems p
            JOIN problem_categories pc ON p.id = pc.problem_id
            JOIN categories c ON pc.category_id = c.id
            WHERE p.claimed_by_user_id = ? AND p.status = 'Completed'
        ''', (user_id,))
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    except sqlite3.Error as e:
        st.error(f"Error calculating user points: {str(e)}")
        return 0
    finally:
        conn.close()

def get_leaderboard() -> list:
    """
    Get the current leaderboard with user rankings and points.
    
    Returns:
        list: List of tuples containing (username, points) sorted by points in descending order.
        
    Raises:
        sqlite3.Error: If there is an error querying the database.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.username, COALESCE(SUM(c.points), 0) as total_points
            FROM users u
            LEFT JOIN problems p ON u.id = p.claimed_by_user_id AND p.status = 'Completed'
            LEFT JOIN problem_categories pc ON p.id = pc.problem_id
            LEFT JOIN categories c ON pc.category_id = c.id
            GROUP BY u.id, u.username
            ORDER BY total_points DESC
        ''')
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching leaderboard: {str(e)}")
        return []
    finally:
        conn.close()

def display_leaderboard() -> None:
    """
    Display the leaderboard in the Streamlit interface.
    Shows a table with user rankings, usernames, and points.
    """
    leaderboard = get_leaderboard()
    
    if not leaderboard:
        st.info("No points have been earned yet.")
        return
        
    # Create a DataFrame-like structure for display
    data = {
        "Rank": range(1, len(leaderboard) + 1),
        "Username": [entry[0] for entry in leaderboard],
        "Points": [entry[1] for entry in leaderboard]
    }
    
    # Display the leaderboard
    st.subheader("🏆 Leaderboard")
    st.dataframe(
        data,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Username": st.column_config.TextColumn("Username", width="medium"),
            "Points": st.column_config.NumberColumn("Points", width="small")
        },
        hide_index=True
    ) 