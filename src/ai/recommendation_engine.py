"""
Recommendation engine module that provides AI-powered recommendations for projects and tasks.
"""

from typing import List, Dict, Any
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class RecommendationEngine:
    """
    Provides AI-powered recommendations for project improvements and resource allocation.
    
    Attributes:
        llm: The language model instance used for recommendations
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the recommendation engine with OpenAI API key.
        
        Args:
            api_key (str): OpenAI API key for accessing the language model
        """
        self.llm = OpenAI(temperature=0.7, openai_api_key=api_key)
    
    def suggest_project_improvements(self, project_data: Dict[str, Any], problems_df: pd.DataFrame) -> List[str]:
        """
        Suggest improvements for a project based on its current state and problems.
        
        Args:
            project_data (Dict[str, Any]): Project information
            problems_df (pd.DataFrame): DataFrame containing problems data
            
        Returns:
            List[str]: List of suggested improvements
        """
        project_problems = problems_df[problems_df['project_id'] == project_data['id']]
        
        prompt = PromptTemplate(
            input_variables=["project", "problems"],
            template="""
            Based on the following project and its problems, suggest specific improvements:
            
            Project:
            Name: {project['name']}
            Description: {project['description']}
            Status: {project['status']}
            
            Problems:
            {problems}
            
            Provide specific, actionable recommendations for improving the project.
            """
        )
        
        problems_text = "\n".join([
            f"- {row['name']}: {row['status']}"
            for _, row in project_problems.iterrows()
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            project=project_data,
            problems=problems_text
        )
    
    def recommend_resource_allocation(self, projects_df: pd.DataFrame, problems_df: pd.DataFrame, users_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Recommend optimal resource allocation across projects and problems.
        
        Args:
            projects_df (pd.DataFrame): DataFrame containing projects data
            problems_df (pd.DataFrame): DataFrame containing problems data
            users_df (pd.DataFrame): DataFrame containing users data
            
        Returns:
            Dict[str, Any]: Resource allocation recommendations
        """
        prompt = PromptTemplate(
            input_variables=["projects", "problems", "users"],
            template="""
            Based on the following information, suggest optimal resource allocation:
            
            Projects:
            {projects}
            
            Problems:
            {problems}
            
            Available Users:
            {users}
            
            Provide recommendations for:
            1. Team member assignments
            2. Project priorities
            3. Resource distribution
            """
        )
        
        projects_text = "\n".join([
            f"- {row['name']}: {row['status']}"
            for _, row in projects_df.iterrows()
        ])
        
        problems_text = "\n".join([
            f"- {row['name']}: {row['status']}"
            for _, row in problems_df.iterrows()
        ])
        
        users_text = "\n".join([
            f"- {row['username']}"
            for _, row in users_df.iterrows()
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            projects=projects_text,
            problems=problems_text,
            users=users_text
        )
    
    def find_similar_items(self, item: Dict[str, Any], projects_df: pd.DataFrame, problems_df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find similar projects or problems based on content and context.
        
        Args:
            item (Dict[str, Any]): The item to find similarities for
            projects_df (pd.DataFrame): DataFrame containing projects data
            problems_df (pd.DataFrame): DataFrame containing problems data
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Similar projects and problems
        """
        prompt = PromptTemplate(
            input_variables=["item", "projects", "problems"],
            template="""
            Find items similar to the following:
            
            Item:
            Name: {item['name']}
            Description: {item['description']}
            
            Available Projects:
            {projects}
            
            Available Problems:
            {problems}
            
            Return a list of similar items with explanations of why they are similar.
            """
        )
        
        projects_text = "\n".join([
            f"- {row['name']}: {row['description']}"
            for _, row in projects_df.iterrows()
        ])
        
        problems_text = "\n".join([
            f"- {row['name']}: {row['description']}"
            for _, row in problems_df.iterrows()
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            item=item,
            projects=projects_text,
            problems=problems_text
        )
    
    def suggest_team_assignments(self, project_data: Dict[str, Any], users_df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Suggest optimal team assignments for a project.
        
        Args:
            project_data (Dict[str, Any]): Project information
            users_df (pd.DataFrame): DataFrame containing users data
            
        Returns:
            Dict[str, List[str]]: Suggested team assignments with roles
        """
        prompt = PromptTemplate(
            input_variables=["project", "users"],
            template="""
            Based on the following project and available users, suggest optimal team assignments:
            
            Project:
            Name: {project['name']}
            Description: {project['description']}
            
            Available Users:
            {users}
            
            Suggest team assignments including:
            1. Team members
            2. Roles
            3. Responsibilities
            """
        )
        
        users_text = "\n".join([
            f"- {row['username']}"
            for _, row in users_df.iterrows()
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            project=project_data,
            users=users_text
        ) 