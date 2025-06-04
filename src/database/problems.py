"""
Problem management functions for the Team Project & Problem Tracker.
"""

import sqlite3
import streamlit as st
from datetime import datetime
from src.database.db import get_db_connection

def complete_problem(problem_id: int, reference: str) -> None:
    """
    Mark a problem as completed and add a reference to what was accomplished.
    
    Args:
        problem_id (int): The ID of the problem to complete.
        reference (str): A reference to what was accomplished or the artifact.
        
    Raises:
        sqlite3.Error: If there is an error updating the database.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Update problem status and completed_at timestamp
        cursor.execute('''
            UPDATE problems 
            SET status = 'Completed',
                completed_at = CURRENT_TIMESTAMP,
                description = CASE 
                    WHEN description IS NULL OR description = '' 
                    THEN ? 
                    ELSE description || '\n\nReference: ' || ? 
                END
            WHERE id = ?
        ''', (reference, reference, problem_id))
        conn.commit()
        st.success("Problem marked as completed with reference added!")
    except sqlite3.Error as e:
        st.error(f"Error completing problem: {str(e)}")
    finally:
        conn.close()

def update_problem_status(problem_id: int, new_status: str) -> None:
    """
    Update the status of a problem.
    
    Args:
        problem_id (int): The ID of the problem to update.
        new_status (str): The new status to set.
        
    Raises:
        sqlite3.Error: If there is an error updating the database.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE problems 
            SET status = ?,
                completed_at = CASE 
                    WHEN ? = 'Completed' THEN CURRENT_TIMESTAMP 
                    ELSE completed_at 
                END
            WHERE id = ?
        ''', (new_status, new_status, problem_id))
        conn.commit()
        st.success(f"Problem status updated to {new_status}!")
    except sqlite3.Error as e:
        st.error(f"Error updating problem status: {str(e)}")
    finally:
        conn.close()

def claim_problem(problem_id: int, user_id: int) -> None:
    """
    Claim a problem for a user.
    
    Args:
        problem_id (int): The ID of the problem to claim.
        user_id (int): The ID of the user claiming the problem.
        
    Raises:
        sqlite3.Error: If there is an error updating the database.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE problems 
            SET claimed_by_user_id = ?,
                status = 'In Progress'
            WHERE id = ?
        ''', (user_id, problem_id))
        conn.commit()
        st.success("Problem claimed successfully!")
    except sqlite3.Error as e:
        st.error(f"Error claiming problem: {str(e)}")
    finally:
        conn.close()

def unclaim_problem(problem_id: int) -> None:
    """
    Unclaim a problem.
    
    Args:
        problem_id (int): The ID of the problem to unclaim.
        
    Raises:
        sqlite3.Error: If there is an error updating the database.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE problems 
            SET claimed_by_user_id = NULL,
                status = 'Open'
            WHERE id = ?
        ''', (problem_id,))
        conn.commit()
        st.success("Problem unclaimed successfully!")
    except sqlite3.Error as e:
        st.error(f"Error unclaiming problem: {str(e)}")
    finally:
        conn.close() 