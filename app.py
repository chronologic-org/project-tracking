import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Optional, Tuple

# Constants
DATABASE_NAME = "tracker.db"
PROJECT_TYPES = ['1-week', '2-week', '3-week', '4-week']
PROJECT_STATUSES = ['Open', 'In Progress', 'Completed']
PROBLEM_STATUSES = ['Open', 'In Progress', 'Completed']

def init_db() -> None:
    """
    Initialize the SQLite database with required tables if they don't exist.
    Creates tables for users, categories, projects, problems, and their relationships.
    Also adds completed_at columns to projects and problems tables if they don't exist.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
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

def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: A connection to the SQLite database.
    """
    return sqlite3.connect(DATABASE_NAME)

# Database Functions
def add_user(username: str) -> None:
    """
    Add a new user to the users table.
    
    Args:
        username (str): The username of the new user.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        st.success(f"User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        st.warning(f"Username '{username}' already exists.")
    except sqlite3.Error as e:
        st.error(f"Error adding user: {str(e)}")
    finally:
        conn.close()

def get_users() -> pd.DataFrame:
    """
    Retrieve all users from the database.
    
    Returns:
        pd.DataFrame: A DataFrame containing all users with columns id and username.
    """
    conn = get_db_connection()
    try:
        return pd.read_sql_query('SELECT id, username FROM users ORDER BY username', conn)
    except sqlite3.Error as e:
        st.error(f"Error retrieving users: {str(e)}")
        return pd.DataFrame(columns=['id', 'username'])
    finally:
        conn.close()

def add_category(name: str, points: int) -> None:
    """
    Add a new category to the categories table.
    
    Args:
        name (str): The name of the new category.
        points (int): The point value associated with the category.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (name, points) VALUES (?, ?)', (name, points))
        conn.commit()
        st.success(f"Category '{name}' added successfully!")
    except sqlite3.IntegrityError:
        st.warning(f"Category '{name}' already exists.")
    except sqlite3.Error as e:
        st.error(f"Error adding category: {str(e)}")
    finally:
        conn.close()

def get_categories() -> pd.DataFrame:
    """
    Retrieve all categories from the database.
    
    Returns:
        pd.DataFrame: A DataFrame containing all categories with columns id, name, and points.
    """
    conn = get_db_connection()
    try:
        return pd.read_sql_query('SELECT id, name, points FROM categories ORDER BY name', conn)
    except sqlite3.Error as e:
        st.error(f"Error retrieving categories: {str(e)}")
        return pd.DataFrame(columns=['id', 'name', 'points'])
    finally:
        conn.close()

def add_project(name: str, description: str, project_type: str, worker_ids: List[int]) -> None:
    """
    Add a new project and assign workers to it.
    
    Args:
        name (str): The name of the new project.
        description (str): The description of the project.
        project_type (str): The type of project (e.g., '1-week', '2-week').
        worker_ids (List[int]): List of user IDs to assign to the project.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, description, type)
            VALUES (?, ?, ?)
        ''', (name, description, project_type))
        
        project_id = cursor.lastrowid
        
        for worker_id in worker_ids:
            cursor.execute('''
                INSERT INTO project_workers (project_id, user_id)
                VALUES (?, ?)
            ''', (project_id, worker_id))
            
        conn.commit()
        st.success(f"Project '{name}' added successfully!")
    except sqlite3.Error as e:
        conn.rollback()
        st.error(f"Error adding project: {str(e)}")
    finally:
        conn.close()

def get_projects() -> pd.DataFrame:
    """
    Retrieve all projects with their assigned workers.
    
    Returns:
        pd.DataFrame: A DataFrame containing all projects with their details and assigned workers.
    """
    conn = get_db_connection()
    try:
        query = '''
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
        '''
        return pd.read_sql_query(query, conn)
    except sqlite3.Error as e:
        st.error(f"Error retrieving projects: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

def update_project_status(project_id: int, status: str) -> None:
    """
    Update the status of a project and set completed_at timestamp if completed.
    
    Args:
        project_id (int): The ID of the project to update.
        status (str): The new status of the project.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if status == 'Completed':
            cursor.execute('''
                UPDATE projects 
                SET status = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, project_id))
        else:
            cursor.execute('''
                UPDATE projects 
                SET status = ?, completed_at = NULL
                WHERE id = ?
            ''', (status, project_id))
        conn.commit()
        st.success("Project status updated successfully!")
    except sqlite3.Error as e:
        st.error(f"Error updating project status: {str(e)}")
    finally:
        conn.close()

def add_problem(name: str, description: str, project_id: Optional[int], claimed_by_user_id: Optional[int], category_ids: List[int]) -> None:
    """
    Add a new problem and assign categories to it.
    
    Args:
        name (str): The name of the new problem.
        description (str): The description of the problem.
        project_id (Optional[int]): The ID of the associated project, if any.
        claimed_by_user_id (Optional[int]): The ID of the user claiming the problem, if any.
        category_ids (List[int]): List of category IDs to assign to the problem.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO problems (name, description, project_id, claimed_by_user_id)
            VALUES (?, ?, ?, ?)
        ''', (name, description, project_id, claimed_by_user_id))
        
        problem_id = cursor.lastrowid
        
        for category_id in category_ids:
            cursor.execute('''
                INSERT INTO problem_categories (problem_id, category_id)
                VALUES (?, ?)
            ''', (problem_id, category_id))
            
        conn.commit()
        st.success(f"Problem '{name}' added successfully!")
    except sqlite3.Error as e:
        conn.rollback()
        st.error(f"Error adding problem: {str(e)}")
    finally:
        conn.close()

def get_problems() -> pd.DataFrame:
    """
    Retrieve all problems with their associated project, claimed user, and categories.
    
    Returns:
        pd.DataFrame: A DataFrame containing all problems with their details.
    """
    conn = get_db_connection()
    try:
        query = '''
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
        '''
        df = pd.read_sql_query(query, conn)
        # Convert claimed_by_user_id to integer
        df['claimed_by_user_id'] = pd.to_numeric(df['claimed_by_user_id'], errors='coerce')
        st.write("Debug: Retrieved problems data:", df[['id', 'name', 'claimed_by', 'claimed_by_user_id']].head())  # Debug log
        return df
    except sqlite3.Error as e:
        st.error(f"Error retrieving problems: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

def update_problem_status(problem_id: int, status: str) -> None:
    """
    Update the status of a problem and set completed_at timestamp if completed.
    
    Args:
        problem_id (int): The ID of the problem to update.
        status (str): The new status of the problem.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if status == 'Completed':
            cursor.execute('''
                UPDATE problems 
                SET status = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, problem_id))
        else:
            cursor.execute('''
                UPDATE problems 
                SET status = ?, completed_at = NULL
                WHERE id = ?
            ''', (status, problem_id))
        conn.commit()
        st.success("Problem status updated successfully!")
    except sqlite3.Error as e:
        st.error(f"Error updating problem status: {str(e)}")
    finally:
        conn.close()

def claim_problem(problem_id: int, user_id: int) -> None:
    """
    Claim a problem for a specific user and update its status to 'In Progress'.
    
    Args:
        problem_id (int): The ID of the problem to claim.
        user_id (int): The ID of the user claiming the problem.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # First check if the problem exists and is not already claimed
        cursor.execute('SELECT claimed_by_user_id FROM problems WHERE id = ?', (problem_id,))
        result = cursor.fetchone()
        if result is None:
            st.error("Problem not found")
            return
        if result[0] is not None and result[0] != 0:
            st.error("Problem is already claimed by another user")
            return
            
        # Begin transaction
        cursor.execute('BEGIN TRANSACTION')
        try:
            # Ensure user_id is an integer and not None or 0
            if user_id is None or user_id == 0:
                raise ValueError("Invalid user_id")
                
            # Update the problem with explicit type casting
            cursor.execute('''
                UPDATE problems 
                SET claimed_by_user_id = ?,
                    status = 'In Progress'
                WHERE id = ? AND (claimed_by_user_id IS NULL OR claimed_by_user_id = 0)
            ''', (int(user_id), int(problem_id)))
            
            # Verify the update was successful
            cursor.execute('SELECT claimed_by_user_id, status FROM problems WHERE id = ?', (problem_id,))
            verify_result = cursor.fetchone()
            
            if verify_result is None or verify_result[0] != user_id or verify_result[1] != 'In Progress':
                raise Exception("Update verification failed")
                
            conn.commit()
            st.success("Problem claimed successfully!")
        except Exception as e:
            conn.rollback()
            st.error(f"Failed to claim problem: {str(e)}")
            raise
    except sqlite3.Error as e:
        st.error(f"Error claiming problem: {str(e)}")
    finally:
        conn.close()

def unclaim_problem(problem_id: int) -> None:
    """
    Remove the claim on a problem and reset its status to 'Open'.
    
    Args:
        problem_id (int): The ID of the problem to unclaim.
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

def get_completed_projects_count() -> int:
    """
    Get the count of completed projects.
    
    Returns:
        int: The number of completed projects.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM projects WHERE status = ?', ('Completed',))
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        st.error(f"Error getting completed projects count: {str(e)}")
        return 0
    finally:
        conn.close()

def get_completed_problems_count() -> int:
    """
    Get the count of completed problems.
    
    Returns:
        int: The number of completed problems.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM problems WHERE status = ?', ('Completed',))
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        st.error(f"Error getting completed problems count: {str(e)}")
        return 0
    finally:
        conn.close()

def get_category_completion_data() -> pd.DataFrame:
    """
    Get completion statistics for each category.
    
    Returns:
        pd.DataFrame: A DataFrame containing category completion statistics.
    """
    conn = get_db_connection()
    try:
        query = '''
            SELECT 
                c.name as category_name,
                COUNT(DISTINCT p.id) as total_problems_in_category,
                COUNT(DISTINCT CASE WHEN p.status = 'Completed' THEN p.id END) as completed_problems_in_category
            FROM categories c
            LEFT JOIN problem_categories pc ON c.id = pc.category_id
            LEFT JOIN problems p ON pc.problem_id = p.id
            GROUP BY c.id, c.name
            ORDER BY c.name
        '''
        df = pd.read_sql_query(query, conn)
        df['completion_rate'] = (df['completed_problems_in_category'] / df['total_problems_in_category']).fillna(0)
        return df
    except sqlite3.Error as e:
        st.error(f"Error getting category completion data: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_problem_completion_times() -> pd.DataFrame:
    """
    Get completion time statistics for completed problems.
    
    Returns:
        pd.DataFrame: A DataFrame containing problem completion time statistics.
    """
    conn = get_db_connection()
    try:
        query = '''
            SELECT 
                name,
                created_at,
                completed_at
            FROM problems
            WHERE status = 'Completed'
            AND completed_at IS NOT NULL
            ORDER BY completed_at DESC
        '''
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['completed_at'] = pd.to_datetime(df['completed_at'])
            df['completion_duration_hours'] = (df['completed_at'] - df['created_at']).dt.total_seconds() / 3600
        return df
    except sqlite3.Error as e:
        st.error(f"Error getting problem completion times: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_project_status_breakdown() -> pd.DataFrame:
    """
    Get status breakdown by project type.
    
    Returns:
        pd.DataFrame: A DataFrame containing project status breakdown.
    """
    conn = get_db_connection()
    try:
        query = '''
            SELECT 
                type,
                status,
                COUNT(*) as count
            FROM projects
            GROUP BY type, status
            ORDER BY type, status
        '''
        return pd.read_sql_query(query, conn)
    except sqlite3.Error as e:
        st.error(f"Error getting project status breakdown: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_problem_status_by_user() -> pd.DataFrame:
    """
    Get problem status breakdown by user.
    
    Returns:
        pd.DataFrame: A DataFrame containing problem status breakdown by user.
    """
    conn = get_db_connection()
    try:
        query = '''
            SELECT 
                u.username as claimed_by,
                p.status,
                COUNT(*) as count
            FROM problems p
            LEFT JOIN users u ON p.claimed_by_user_id = u.id
            GROUP BY u.username, p.status
            ORDER BY u.username, p.status
        '''
        return pd.read_sql_query(query, conn)
    except sqlite3.Error as e:
        st.error(f"Error getting problem status by user: {str(e)}")
        return pd.DataFrame()
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

# Initialize the database when the app starts
init_db()

# Set page configuration
st.set_page_config(layout="wide", page_title="Team Project & Problem Tracker")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Projects", "Problems", "Categories", "Users", "Analytics"])

# Current User Selection
st.sidebar.header("Current User")
users_df = get_users()
if not users_df.empty:
    current_user = st.sidebar.selectbox("Select your username", users_df['username'])
    current_user_id = users_df[users_df['username'] == current_user]['id'].iloc[0]
else:
    st.sidebar.warning("No users available. Please add a user first.")
    current_user_id = None

# Add New User Section
with st.sidebar.expander("Add New User"):
    with st.form("new_user_form"):
        new_username = st.text_input("Username")
        if st.form_submit_button("Add User"):
            if new_username.strip():
                add_user(new_username)
                st.rerun()
            else:
                st.error("Username cannot be empty.") 

# Main content area based on page selection
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    # Open Projects Section
    st.header("Open Projects")
    projects_df = get_projects()
    open_projects = projects_df[projects_df['status'] == 'Open']
    if not open_projects.empty:
        st.dataframe(
            open_projects[['name', 'type', 'assigned_workers', 'status']],
            use_container_width=True
        )
    else:
        st.info("No open projects.")
    
    # Open Problems Section
    st.header("Open Problems")
    problems_df = get_problems()
    open_problems = problems_df[problems_df['status'] == 'Open']
    if not open_problems.empty:
        st.dataframe(
            open_problems[['name', 'project_name', 'claimed_by', 'categories', 'total_points', 'status']],
            use_container_width=True
        )
    else:
        st.info("No open problems.")

elif page == "Projects":
    st.title("🚧 Project Management")
    
    # Create New Project Section
    st.header("Create New Project")
    with st.form("new_project_form", clear_on_submit=True):
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Description")
        project_type = st.selectbox("Project Type", PROJECT_TYPES)
        
        # Get users for worker selection
        users_df = get_users()
        if not users_df.empty:
            worker_ids = st.multiselect(
                "Assign Team Members",
                options=users_df['id'].tolist(),
                format_func=lambda x: users_df[users_df['id'] == x]['username'].iloc[0]
            )
        else:
            st.warning("No users available. Please add users first.")
            worker_ids = []
        
        if st.form_submit_button("Add Project"):
            if project_name.strip():
                add_project(project_name, project_description, project_type, worker_ids)
                st.rerun()
            else:
                st.error("Project name cannot be empty.")
    
    # All Projects Section
    st.header("All Projects")
    projects_df = get_projects()
    if not projects_df.empty:
        st.dataframe(projects_df, use_container_width=True)
        
        # Update Project Status Section
        st.subheader("Update Project Status")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_project = st.selectbox(
                "Select Project",
                options=projects_df['id'].tolist(),
                format_func=lambda x: projects_df[projects_df['id'] == x]['name'].iloc[0]
            )
        
        with col2:
            new_status = st.selectbox("New Status", PROJECT_STATUSES)
            if st.button("Update Status"):
                update_project_status(selected_project, new_status)
                st.rerun()
    else:
        st.info("No projects available. Create a new project to get started.")

elif page == "Problems":
    st.title("🐞 Problem Management")
    
    # Create New Problem Section
    st.header("Create New Problem")
    with st.form("new_problem_form", clear_on_submit=True):
        problem_name = st.text_input("Problem Name")
        problem_description = st.text_area("Description")
        
        # Get projects for linking
        projects_df = get_projects()
        if not projects_df.empty:
            project_options = [None] + projects_df['id'].tolist()
            project_names = ["- None -"] + projects_df['name'].tolist()
            selected_project = st.selectbox(
                "Link to Project (Optional)",
                options=project_options,
                format_func=lambda x: project_names[project_options.index(x)] if x is not None else "- None -"
            )
        else:
            st.warning("No projects available. You can still create a problem without linking it to a project.")
            selected_project = None
        
        # Get categories for selection
        categories_df = get_categories()
        if not categories_df.empty:
            category_ids = st.multiselect(
                "Select Categories",
                options=categories_df['id'].tolist(),
                format_func=lambda x: f"{categories_df[categories_df['id'] == x]['name'].iloc[0]} ({categories_df[categories_df['id'] == x]['points'].iloc[0]} pts)"
            )
        else:
            st.warning("No categories available. Please add categories first.")
            category_ids = []
        
        if st.form_submit_button("Add Problem"):
            if problem_name.strip():
                add_problem(problem_name, problem_description, selected_project, None, category_ids)
                st.rerun()
            else:
                st.error("Problem name cannot be empty.")
    
    # All Problems Section
    st.header("All Problems")
    
    # Clear any cached data to ensure fresh data
    if 'problems_df' in st.session_state:
        del st.session_state['problems_df']
    
    # Get fresh problems data
    problems_df = get_problems()
    
    if not problems_df.empty:
        # Display the table with specific columns
        display_columns = ['name', 'description', 'status', 'project_name', 'claimed_by', 'categories', 'total_points']
        st.dataframe(problems_df[display_columns], use_container_width=True)
        
        # Update Problem Status / Claim / Unclaim Section
        st.subheader("Update Problem Status / Claim / Unclaim")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_problem = st.selectbox(
                "Select Problem",
                options=problems_df['id'].tolist(),
                format_func=lambda x: problems_df[problems_df['id'] == x]['name'].iloc[0]
            )
            
            new_status = st.selectbox("New Status", PROBLEM_STATUSES)
            if st.button("Update Status"):
                update_problem_status(selected_problem, new_status)
                st.rerun()
        
        with col2:
            if current_user_id is not None:
                selected_problem_data = problems_df[problems_df['id'] == selected_problem].iloc[0]
                
                if pd.isna(selected_problem_data['claimed_by']) or selected_problem_data['claimed_by'] != current_user:
                    if st.button("Claim Problem", key="claim_button"):
                        claim_problem(selected_problem, current_user_id)
                        st.rerun()
                else:
                    if st.button("Unclaim Problem", key="unclaim_button"):
                        unclaim_problem(selected_problem)
                        st.rerun()
            else:
                st.warning("Please select a user from the sidebar to claim problems.")
    else:
        st.info("No problems available. Create a new problem to get started.")

elif page == "Analytics":
    st.title("📈 Analytics & Insights")
    
    # Overall Progress Section
    st.header("Overall Progress")
    col1, col2 = st.columns(2)
    
    with col1:
        completed_projects = get_completed_projects_count()
        st.metric("Completed Projects", completed_projects)
    
    with col2:
        completed_problems = get_completed_problems_count()
        st.metric("Completed Problems", completed_problems)
    
    # Problem Completion by Category Section
    st.header("Problem Completion by Category")
    category_data = get_category_completion_data()
    if not category_data.empty:
        st.dataframe(category_data)
        
        # Create bar chart
        chart_data = category_data.melt(
            id_vars=['category_name'],
            value_vars=['total_problems_in_category', 'completed_problems_in_category'],
            var_name='Metric',
            value_name='Count'
        )
        st.bar_chart(chart_data, x='category_name', y='Count', color='Metric')
    else:
        st.info("No category completion data available.")
    
    # Problem Completion Times Section
    st.header("Problem Completion Times")
    completion_times = get_problem_completion_times()
    if not completion_times.empty:
        avg_completion_time = completion_times['completion_duration_hours'].mean()
        st.metric("Average Problem Completion Time", f"{avg_completion_time:.1f} hours")
        
        st.subheader("Distribution of Problem Completion Times (Hours)")
        st.hist_chart(completion_times['completion_duration_hours'])
        
        st.subheader("Problem Completion Details")
        st.dataframe(
            completion_times[['name', 'completion_duration_hours']]
            .sort_values('completion_duration_hours', ascending=False)
        )
    else:
        st.info("No problem completion time data available.")
    
    # Project Status Breakdown Section
    st.header("Project Status Breakdown")
    project_status = get_project_status_breakdown()
    if not project_status.empty:
        st.dataframe(project_status)
        
        # Create pivot table for chart
        pivot_data = project_status.pivot(
            index='type',
            columns='status',
            values='count'
        ).fillna(0)
        
        st.bar_chart(pivot_data)
    else:
        st.info("No project status data available.")
    
    # Problem Status by User Section
    st.header("Problem Status by Claimed User")
    problem_status = get_problem_status_by_user()
    if not problem_status.empty:
        st.dataframe(problem_status)
        
        # Create pivot table for chart
        pivot_data = problem_status.pivot(
            index='claimed_by',
            columns='status',
            values='count'
        ).fillna(0)
        
        st.bar_chart(pivot_data)
    else:
        st.info("No problem status by user data available.") 

elif page == "Categories":
    st.title("🏷️ Category Management")
    
    # Add New Category Section
    st.header("Add New Category")
    with st.form("new_category_form", clear_on_submit=True):
        category_name = st.text_input("Category Name")
        category_points = st.number_input("Points", min_value=1, value=1, step=1)
        
        if st.form_submit_button("Add Category"):
            if category_name.strip():
                add_category(category_name, category_points)
                st.rerun()
            else:
                st.error("Category name cannot be empty.")
    
    # All Categories Section
    st.header("All Categories")
    categories_df = get_categories()
    if not categories_df.empty:
        st.dataframe(categories_df, use_container_width=True)
    else:
        st.info("No categories available. Add a new category to get started.") 

elif page == "Users":
    st.title("👥 Users")
    
    # Get all users
    users_df = get_users()
    if not users_df.empty:
        # Display users table
        st.header("All Users")
        st.dataframe(users_df, use_container_width=True)
        
        # Get user details
        st.header("User Details")
        selected_user = st.selectbox(
            "Select User",
            options=users_df['id'].tolist(),
            format_func=lambda x: users_df[users_df['id'] == x]['username'].iloc[0]
        )
        
        if selected_user:
            # Get user's projects
            conn = get_db_connection()
            try:
                # Get projects for selected user
                user_projects = pd.read_sql_query('''
                    SELECT 
                        p.id,
                        p.name,
                        p.type,
                        p.status,
                        p.created_at,
                        p.completed_at
                    FROM projects p
                    JOIN project_workers pw ON p.id = pw.project_id
                    WHERE pw.user_id = ?
                    ORDER BY p.created_at DESC
                ''', conn, params=(selected_user,))
                
                if not user_projects.empty:
                    st.subheader("Assigned Projects")
                    st.dataframe(user_projects, use_container_width=True)
                else:
                    st.info("No projects assigned to this user.")
                
                # Get problems claimed by user
                user_problems = pd.read_sql_query('''
                    SELECT 
                        p.id,
                        p.name,
                        p.description,
                        p.status,
                        p.created_at,
                        p.completed_at,
                        pr.name as project_name
                    FROM problems p
                    LEFT JOIN projects pr ON p.project_id = pr.id
                    WHERE p.claimed_by_user_id = ?
                    ORDER BY p.created_at DESC
                ''', conn, params=(selected_user,))
                
                if not user_problems.empty:
                    st.subheader("Claimed Problems")
                    st.dataframe(user_problems, use_container_width=True)
                else:
                    st.info("No problems claimed by this user.")
                    
            except sqlite3.Error as e:
                st.error(f"Error retrieving user data: {str(e)}")
            finally:
                conn.close()
    else:
        st.info("No users available. Add users using the sidebar form.") 