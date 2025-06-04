import streamlit as st
import pandas as pd
from typing import List, Optional

from src.models.constants import PROJECT_TYPES, PROJECT_STATUSES, PROBLEM_STATUSES
from src.ui.components import display_dataframe, display_metrics
from src.database.categories import add_category, update_category_points

def render_dashboard(projects_df: pd.DataFrame, problems_df: pd.DataFrame) -> None:
    """
    Render the dashboard page.
    
    Args:
        projects_df (pd.DataFrame): DataFrame containing project data.
        problems_df (pd.DataFrame): DataFrame containing problem data.
    """
    st.title("📊 Dashboard")
    
    # Open Projects Section
    st.header("Open Projects")
    open_projects = projects_df[projects_df['status'] == 'Open']
    display_dataframe(
        open_projects,
        columns=['name', 'type', 'assigned_workers', 'status']
    )
    
    # Open Problems Section
    st.header("Open Problems")
    open_problems = problems_df[problems_df['status'] == 'Open']
    display_dataframe(
        open_problems,
        columns=['name', 'project_name', 'claimed_by', 'categories', 'total_points', 'status']
    )

def render_projects_page(projects_df: pd.DataFrame, users_df: pd.DataFrame) -> None:
    """
    Render the projects management page.
    
    Args:
        projects_df (pd.DataFrame): DataFrame containing project data.
        users_df (pd.DataFrame): DataFrame containing user data.
    """
    st.title("🚧 Project Management")
    
    # Create New Project Section
    st.header("Create New Project")
    with st.form("new_project_form", clear_on_submit=True):
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Description")
        project_type = st.selectbox("Project Type", PROJECT_TYPES)
        
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
                # TODO: Call add_project function
                st.rerun()
            else:
                st.error("Project name cannot be empty.")
    
    # All Projects Section
    st.header("All Projects")
    display_dataframe(projects_df)
    
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
            # TODO: Call update_project_status function
            st.rerun()

def render_problems_page(problems_df: pd.DataFrame, projects_df: pd.DataFrame, categories_df: pd.DataFrame) -> None:
    """
    Render the problems management page.
    
    Args:
        problems_df (pd.DataFrame): DataFrame containing problem data.
        projects_df (pd.DataFrame): DataFrame containing project data.
        categories_df (pd.DataFrame): DataFrame containing category data.
    """
    st.title("🐞 Problem Management")
    
    # Create New Problem Section
    st.header("Create New Problem")
    with st.form("new_problem_form", clear_on_submit=True):
        problem_name = st.text_input("Problem Name")
        problem_description = st.text_area("Description")
        
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
                # TODO: Call add_problem function
                st.rerun()
            else:
                st.error("Problem name cannot be empty.")
    
    # All Problems Section
    st.header("All Problems")
    display_dataframe(
        problems_df,
        columns=['name', 'description', 'status', 'project_name', 'claimed_by', 'categories', 'total_points']
    )
    
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
            # TODO: Call update_problem_status function
            st.rerun()
    
    with col2:
        if st.session_state.user_id is not None:
            filtered_problems = problems_df[problems_df['id'] == selected_problem]
            if not filtered_problems.empty:
                selected_problem_data = filtered_problems.iloc[0]
                
                if pd.isna(selected_problem_data['claimed_by']):
                    if st.button("Claim Problem", key="claim_button"):
                        # TODO: Call claim_problem function
                        st.rerun()
                else:
                    if st.button("Unclaim Problem", key="unclaim_button"):
                        # TODO: Call unclaim_problem function
                        st.rerun()
            else:
                st.warning("Selected problem not found in the database.")
        else:
            st.warning("Please select a user from the sidebar to claim problems.")

def render_categories_page(categories_df: pd.DataFrame) -> None:
    """
    Render the categories management page.
    
    Args:
        categories_df (pd.DataFrame): DataFrame containing category data.
    """
    st.title("🏷️ Category Management")
    
    # Create New Category Section
    st.header("Create New Category")
    with st.form("new_category_form", clear_on_submit=True):
        category_name = st.text_input("Category Name")
        category_points = st.number_input("Points", min_value=1, value=1)
        
        if st.form_submit_button("Add Category"):
            if category_name.strip():
                add_category(category_name.strip(), category_points)
                st.rerun()
            else:
                st.error("Category name cannot be empty.")
    
    # All Categories Section
    st.header("All Categories")
    display_dataframe(
        categories_df,
        columns=['name', 'points']
    )
    
    # Update Category Section
    st.subheader("Update Category")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_category = st.selectbox(
            "Select Category",
            options=categories_df['id'].tolist(),
            format_func=lambda x: categories_df[categories_df['id'] == x]['name'].iloc[0]
        )
    
    with col2:
        new_points = st.number_input("New Points", min_value=1, value=1)
        if st.button("Update Points"):
            update_category_points(selected_category, new_points)
            st.rerun()

def render_users_page(users_df: pd.DataFrame, projects_df: pd.DataFrame, problems_df: pd.DataFrame) -> None:
    """
    Render the users management page.
    
    Args:
        users_df (pd.DataFrame): DataFrame containing user data.
        projects_df (pd.DataFrame): DataFrame containing project data.
        problems_df (pd.DataFrame): DataFrame containing problem data.
    """
    st.title("👥 User Management")
    
    # User List Section
    st.header("All Users")
    display_dataframe(
        users_df,
        columns=['username']
    )
    
    # User Activity Section
    st.header("User Activity")
    selected_user = st.selectbox(
        "Select User",
        options=users_df['id'].tolist(),
        format_func=lambda x: users_df[users_df['id'] == x]['username'].iloc[0]
    )
    
    if selected_user:
        # Get user's projects
        user_projects = projects_df[projects_df['assigned_workers'].str.contains(
            users_df[users_df['id'] == selected_user]['username'].iloc[0], 
            na=False
        )]
        
        # Get user's claimed problems
        user_problems = problems_df[problems_df['claimed_by_user_id'] == selected_user]
        
        # Display user's projects
        st.subheader("Assigned Projects")
        display_dataframe(
            user_projects,
            columns=['name', 'type', 'status']
        )
        
        # Display user's problems
        st.subheader("Claimed Problems")
        display_dataframe(
            user_problems,
            columns=['name', 'project_name', 'status', 'total_points']
        )

def render_analytics_page(projects_df: pd.DataFrame, problems_df: pd.DataFrame, categories_df: pd.DataFrame) -> None:
    """
    Render the analytics page.
    
    Args:
        projects_df (pd.DataFrame): DataFrame containing project data.
        problems_df (pd.DataFrame): DataFrame containing problem data.
        categories_df (pd.DataFrame): DataFrame containing category data.
    """
    st.title("📈 Analytics")
    
    # Project Analytics
    st.header("Project Analytics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_projects = len(projects_df)
        display_metrics("Total Projects", total_projects)
    
    with col2:
        open_projects = len(projects_df[projects_df['status'] == 'Open'])
        display_metrics("Open Projects", open_projects)
    
    with col3:
        completed_projects = len(projects_df[projects_df['status'] == 'Completed'])
        display_metrics("Completed Projects", completed_projects)
    
    # Project Type Distribution
    st.subheader("Project Type Distribution")
    if not projects_df.empty:
        project_type_counts = projects_df['type'].value_counts()
        st.bar_chart(project_type_counts)
    else:
        st.info("No project data available.")
    
    # Problem Analytics
    st.header("Problem Analytics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_problems = len(problems_df)
        display_metrics("Total Problems", total_problems)
    
    with col2:
        open_problems = len(problems_df[problems_df['status'] == 'Open'])
        display_metrics("Open Problems", open_problems)
    
    with col3:
        total_points = problems_df['total_points'].sum() if not problems_df.empty else 0
        display_metrics("Total Points", total_points)
    
    # Category Distribution
    st.subheader("Category Distribution")
    if not problems_df.empty and 'categories' in problems_df.columns:
        category_counts = {}
        for _, row in problems_df.iterrows():
            if pd.notna(row['categories']):
                categories = row['categories'].split(',')
                for category in categories:
                    category_name = category.split('(')[0].strip()
                    category_counts[category_name] = category_counts.get(category_name, 0) + 1
        
        if category_counts:
            st.bar_chart(category_counts)
        else:
            st.info("No category data available.")
    else:
        st.info("No problem data available.") 