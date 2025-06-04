import streamlit as st
import pandas as pd
from typing import List, Optional
import os
from dotenv import load_dotenv

from src.models.constants import PROJECT_TYPES, PROJECT_STATUSES, PROBLEM_STATUSES
from src.ui.components import display_dataframe, display_metrics
from src.database.categories import add_category, update_category_points
from src.database.problems import complete_problem, update_problem_status, claim_problem, unclaim_problem
from src.ai.project_analyzer import ProjectAnalyzer

# Load environment variables
load_dotenv()

def render_dashboard(projects_df: pd.DataFrame, problems_df: pd.DataFrame,
                    project_analyzer, recommendation_engine) -> None:
    """
    Render the dashboard with AI-powered insights.
    
    Args:
        projects_df (pd.DataFrame): DataFrame containing projects data
        problems_df (pd.DataFrame): DataFrame containing problems data
        project_analyzer: ProjectAnalyzer instance for AI analysis
        recommendation_engine: RecommendationEngine instance for AI recommendations
    """
    st.title("📊 Dashboard")
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Projects", len(projects_df))
    with col2:
        st.metric("Total Problems", len(problems_df))
    with col3:
        completed_problems = len(problems_df[problems_df['status'] == 'Completed'])
        st.metric("Completed Problems", completed_problems)
    
    # Add AI insights section
    st.subheader("🤖 AI Insights")
    
    # Get overall project analysis
    if not projects_df.empty:
        with st.spinner("Analyzing projects..."):
            # Get risk analysis for all projects
            st.subheader("Project Risk Analysis")
            for _, project in projects_df.iterrows():
                with st.expander(f"Analysis for {project['name']}"):
                    risk_analysis = project_analyzer.analyze_project_risks(project.to_dict())
                    st.write(risk_analysis)
    
    # Get resource allocation recommendations
    if not problems_df.empty:
        with st.spinner("Generating recommendations..."):
            st.subheader("Resource Allocation Recommendations")
            recommendations = recommendation_engine.recommend_resource_allocation(
                projects_df, problems_df, pd.DataFrame()
            )
            st.write(recommendations)
    
    # Display recent activity
    st.subheader("Recent Activity")
    
    # Recent projects
    st.write("Recent Projects")
    recent_projects = projects_df.sort_values('created_at', ascending=False).head(5)
    display_dataframe(recent_projects)
    
    # Recent problems
    st.write("Recent Problems")
    recent_problems = problems_df.sort_values('created_at', ascending=False).head(5)
    display_dataframe(recent_problems)

def render_projects_page(projects_df: pd.DataFrame, users_df: pd.DataFrame, 
                        project_analyzer, recommendation_engine, search_engine) -> None:
    """
    Render the projects management page with AI-powered features.
    
    Args:
        projects_df (pd.DataFrame): DataFrame containing projects data
        users_df (pd.DataFrame): DataFrame containing users data
        project_analyzer: ProjectAnalyzer instance for AI analysis
        recommendation_engine: RecommendationEngine instance for AI recommendations
        search_engine: SearchEngine instance for semantic search
    """
    st.title("🚧 Project Management")
    
    # Add AI-powered search
    st.subheader("🔍 AI-Powered Search")
    search_query = st.text_input("Search projects using natural language")
    if search_query:
        with st.spinner("Searching..."):
            search_results = search_engine.semantic_search(search_query, projects_df, pd.DataFrame())
            if search_results["projects"]:
                st.write("Found Projects:")
                for project in search_results["projects"]:
                    st.write(f"- {project['name']}: {project['description']}")
    
    # Create New Project Section
    st.subheader("Create New Project")
    with st.form("new_project_form"):
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Project Description")
        project_type = st.selectbox("Project Type", options=PROJECT_TYPES)
        project_status = st.selectbox("Project Status", options=PROJECT_STATUSES)
        
        submitted = st.form_submit_button("Create Project")
        if submitted:
            # Add project creation logic here
            st.success("Project created successfully!")
    
    # Display Projects
    st.subheader("All Projects")
    display_dataframe(projects_df)
    
    # Add AI analysis section
    st.subheader("🤖 AI Project Analysis")
    selected_project = st.selectbox(
        "Select a project for AI analysis",
        options=projects_df['name'].tolist()
    )
    
    if selected_project:
        project_data = projects_df[projects_df['name'] == selected_project].iloc[0].to_dict()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Analyze Project"):
                with st.spinner("Analyzing project..."):
                    # Get risk analysis
                    risk_analysis = project_analyzer.analyze_project_risks(project_data)
                    st.subheader("Risk Analysis")
                    st.write(risk_analysis)
        
        with col2:
            if st.button("Get Recommendations"):
                with st.spinner("Generating recommendations..."):
                    # Get project improvements
                    improvements = recommendation_engine.suggest_project_improvements(project_data, pd.DataFrame())
                    st.subheader("Project Improvements")
                    st.write(improvements)
                    
                    # Get team assignments
                    team_suggestions = recommendation_engine.suggest_team_assignments(project_data, users_df)
                    st.subheader("Team Assignment Suggestions")
                    st.write(team_suggestions)
    
    # Update Project Status Section
    st.subheader("Update Project Status")
    with st.form("update_project_form"):
        project_to_update = st.selectbox("Select Project", options=projects_df['name'].tolist())
        new_status = st.selectbox("New Status", options=PROJECT_STATUSES)
        
        update_submitted = st.form_submit_button("Update Status")
        if update_submitted:
            # Add status update logic here
            st.success("Project status updated successfully!")

def render_problems_page(problems_df: pd.DataFrame, projects_df: pd.DataFrame, 
                        categories_df: pd.DataFrame, task_manager, search_engine) -> None:
    """
    Render the problems management page with AI-powered features.
    
    Args:
        problems_df (pd.DataFrame): DataFrame containing problems data
        projects_df (pd.DataFrame): DataFrame containing projects data
        categories_df (pd.DataFrame): DataFrame containing categories data
        task_manager: TaskManager instance for AI task management
        search_engine: SearchEngine instance for semantic search
    """
    st.title("🔍 Problem Management")
    
    # Add AI-powered search
    st.subheader("🔍 AI-Powered Search")
    search_query = st.text_input("Search problems using natural language")
    if search_query:
        with st.spinner("Searching..."):
            search_results = search_engine.semantic_search(search_query, pd.DataFrame(), problems_df)
            if search_results["problems"]:
                st.write("Found Problems:")
                for problem in search_results["problems"]:
                    st.write(f"- {problem['name']}: {problem['description']}")
    
    # Create New Problem Section
    st.subheader("Create New Problem")
    with st.form("new_problem_form"):
        problem_name = st.text_input("Problem Name")
        problem_description = st.text_area("Problem Description")
        project_id = st.selectbox("Associated Project", options=projects_df['name'].tolist())
        problem_status = st.selectbox("Problem Status", options=PROBLEM_STATUSES)
        
        submitted = st.form_submit_button("Create Problem")
        if submitted:
            # Add problem creation logic here
            st.success("Problem created successfully!")
    
    # Display Problems
    st.subheader("All Problems")
    display_dataframe(problems_df)
    
    # Add AI task management section
    st.subheader("🤖 AI Task Management")
    selected_problem = st.selectbox(
        "Select a problem for AI analysis",
        options=problems_df['name'].tolist()
    )
    
    if selected_problem:
        problem_data = problems_df[problems_df['name'] == selected_problem].iloc[0].to_dict()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Analyze Task"):
                with st.spinner("Analyzing task..."):
                    # Get task estimation
                    estimation = task_manager.estimate_task_completion(problem_data)
                    st.subheader("Task Estimation")
                    st.write(estimation)
        
        with col2:
            if st.button("Analyze Dependencies"):
                with st.spinner("Analyzing dependencies..."):
                    # Get task dependencies
                    dependencies = task_manager.analyze_dependencies([problem_data])
                    st.subheader("Task Dependencies")
                    st.write(dependencies)
    
    # Update Problem Status Section
    st.subheader("Update Problem Status")
    with st.form("update_problem_form"):
        problem_to_update = st.selectbox("Select Problem", options=problems_df['name'].tolist())
        new_status = st.selectbox("New Status", options=PROBLEM_STATUSES)
        
        update_submitted = st.form_submit_button("Update Status")
        if update_submitted:
            # Add status update logic here
            st.success("Problem status updated successfully!")

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