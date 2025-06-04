import streamlit as st
import pandas as pd

from src.database.db import init_db, get_db_connection
from src.auth.auth import authenticate_user, add_user, get_user_by_session
from src.ui.components import render_login_form, render_register_form, render_sidebar
from src.ui.pages import render_dashboard, render_projects_page, render_problems_page

# Initialize the database when the app starts
init_db()

# Set page configuration
st.set_page_config(layout="wide", page_title="Team Project & Problem Tracker")

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'session_token' not in st.session_state:
    st.session_state.session_token = None

# Authentication UI
if not st.session_state.authenticated:
    st.title("Login")
    
    # Login form
    login_submitted, username, password = render_login_form()
    if login_submitted:
        user_id = authenticate_user(username, password)
        if user_id:
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    # Registration form
    register_submitted, new_username, new_password = render_register_form()
    if register_submitted:
        add_user(new_username, new_password)
        st.success("Registration successful! Please login.")

else:
    # Get current user info
    conn = get_db_connection()
    try:
        users_df = pd.read_sql_query('SELECT id, username FROM users ORDER BY username', conn)
        current_user = users_df[users_df['id'] == st.session_state.user_id]['username'].iloc[0]
    except Exception as e:
        st.error(f"Error getting user info: {str(e)}")
        current_user = "Unknown"
    finally:
        conn.close()
    
    # Render sidebar and get selected page
    page = render_sidebar(current_user)
    
    # Get data for the selected page
    conn = get_db_connection()
    try:
        # Get all necessary data
        projects_df = pd.read_sql_query('''
            SELECT 
                p.id,
                p.name,
                p.description,
                p.type,
                p.status,
                p.created_at,
                p.completed_at,
                GROUP_CONCAT(u.username) as assigned_workers
            FROM projects p
            LEFT JOIN project_workers pw ON p.id = pw.project_id
            LEFT JOIN users u ON pw.user_id = u.id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        ''', conn)
        
        problems_df = pd.read_sql_query('''
            WITH claimed_users AS (
                SELECT 
                    p.id as problem_id,
                    u.username as claimed_by
                FROM problems p
                LEFT JOIN users u ON CAST(p.claimed_by_user_id AS INTEGER) = u.id
            )
            SELECT 
                p.id,
                p.name,
                p.description,
                p.status,
                p.created_at,
                p.completed_at,
                pr.name as project_name,
                cu.claimed_by,
                GROUP_CONCAT(c.name || ' (' || c.points || ' pts)') as categories,
                SUM(c.points) as total_points,
                CAST(p.claimed_by_user_id AS INTEGER) as claimed_by_user_id
            FROM problems p
            LEFT JOIN projects pr ON p.project_id = pr.id
            LEFT JOIN claimed_users cu ON p.id = cu.problem_id
            LEFT JOIN problem_categories pc ON p.id = pc.problem_id
            LEFT JOIN categories c ON pc.category_id = c.id
            GROUP BY p.id, p.name, p.description, p.status, p.created_at, p.completed_at, pr.name, cu.claimed_by, p.claimed_by_user_id
            ORDER BY p.created_at DESC
        ''', conn)
        
        categories_df = pd.read_sql_query('SELECT id, name, points FROM categories ORDER BY name', conn)
        
    except Exception as e:
        st.error(f"Error retrieving data: {str(e)}")
        projects_df = pd.DataFrame()
        problems_df = pd.DataFrame()
        categories_df = pd.DataFrame()
    finally:
        conn.close()
    
    # Render the selected page
    if page == "Dashboard":
        render_dashboard(projects_df, problems_df)
    elif page == "Projects":
        render_projects_page(projects_df, users_df)
    elif page == "Problems":
        render_problems_page(problems_df, projects_df, categories_df)
    # TODO: Add other pages (Categories, Users, Analytics) 