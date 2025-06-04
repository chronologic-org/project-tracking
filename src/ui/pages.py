import streamlit as st
import pandas as pd
from typing import List, Optional

from src.models.constants import PROJECT_TYPES, PROJECT_STATUSES, PROBLEM_STATUSES
from src.ui.components import display_dataframe, display_metrics

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
            selected_problem_data = problems_df[problems_df['id'] == selected_problem].iloc[0]
            
            if pd.isna(selected_problem_data['claimed_by']):
                if st.button("Claim Problem", key="claim_button"):
                    # TODO: Call claim_problem function
                    st.rerun()
            else:
                if st.button("Unclaim Problem", key="unclaim_button"):
                    # TODO: Call unclaim_problem function
                    st.rerun()
        else:
            st.warning("Please select a user from the sidebar to claim problems.") 