"""
Project analyzer module that provides AI-powered analysis of projects and problems.
"""

from typing import List, Dict, Any
import pandas as pd
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class ProjectAnalyzer:
    """
    Analyzes projects and problems using AI to provide insights and recommendations.
    
    Attributes:
        llm: The language model instance used for analysis
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the project analyzer with OpenAI API key.
        
        Args:
            api_key (str): OpenAI API key for accessing the language model
        """
        self.llm = OpenAI(temperature=0.7, openai_api_key=api_key)
        
    def analyze_project_risks(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project risks based on project data and description.
        
        Args:
            project_data (Dict[str, Any]): Project information including name, description, and status
            
        Returns:
            Dict[str, Any]: Risk analysis including identified risks and recommendations
        """
        prompt = PromptTemplate(
            input_variables=["project_name", "project_description", "project_status"],
            template="""
            Analyze the following project for potential risks and provide recommendations:
            Project Name: {project_name}
            Description: {project_description}
            Status: {project_status}
            
            Provide a structured analysis with:
            1. Identified risks
            2. Risk level (High/Medium/Low)
            3. Recommendations for mitigation
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            project_name=project_data["name"],
            project_description=project_data["description"],
            project_status=project_data["status"]
        )
    
    def suggest_categories(self, problem_description: str) -> List[str]:
        """
        Suggest relevant categories for a problem based on its description.
        
        Args:
            problem_description (str): Description of the problem
            
        Returns:
            List[str]: List of suggested category names
        """
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            Based on the following problem description, suggest relevant categories:
            {description}
            
            Return only the category names, one per line.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        categories = chain.run(description=problem_description)
        return [cat.strip() for cat in categories.split('\n') if cat.strip()]
    
    def generate_project_summary(self, project_data: Dict[str, Any], problems_df: pd.DataFrame) -> str:
        """
        Generate a comprehensive summary of a project and its associated problems.
        
        Args:
            project_data (Dict[str, Any]): Project information
            problems_df (pd.DataFrame): DataFrame containing problems data
            
        Returns:
            str: Generated project summary
        """
        project_problems = problems_df[problems_df['project_id'] == project_data['id']]
        
        prompt = PromptTemplate(
            input_variables=["project_name", "project_description", "problems"],
            template="""
            Generate a comprehensive summary of the following project and its problems:
            
            Project: {project_name}
            Description: {project_description}
            
            Problems:
            {problems}
            
            Provide a concise summary highlighting key points, progress, and challenges.
            """
        )
        
        problems_text = "\n".join([
            f"- {row['name']}: {row['status']}"
            for _, row in project_problems.iterrows()
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            project_name=project_data["name"],
            project_description=project_data["description"],
            problems=problems_text
        ) 