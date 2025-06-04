"""
Task manager module that provides AI-powered task management capabilities.
"""

from typing import List, Dict, Any
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class TaskManager:
    """
    Manages tasks using AI to provide intelligent task management capabilities.
    
    Attributes:
        llm: The language model instance used for task management
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the task manager with OpenAI API key.
        
        Args:
            api_key (str): OpenAI API key for accessing the language model
        """
        self.llm = OpenAI(temperature=0.7, openai_api_key=api_key)
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize a list of tasks based on various factors.
        
        Args:
            tasks (List[Dict[str, Any]]): List of tasks with their details
            
        Returns:
            List[Dict[str, Any]]: Prioritized list of tasks
        """
        tasks_text = "\n".join([
            f"Task: {task['name']}\n"
            f"Description: {task['description']}\n"
            f"Status: {task['status']}\n"
            f"Created: {task['created_at']}\n"
            for task in tasks
        ])
        
        prompt = PromptTemplate(
            input_variables=["tasks"],
            template="""
            Prioritize the following tasks based on urgency, importance, and dependencies:
            
            {tasks}
            
            Return the tasks in order of priority, with a brief explanation for each ranking.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(tasks=tasks_text)
    
    def suggest_assignments(self, task: Dict[str, Any], users_df: pd.DataFrame) -> List[str]:
        """
        Suggest team members for task assignment based on their history and skills.
        
        Args:
            task (Dict[str, Any]): Task details
            users_df (pd.DataFrame): DataFrame containing user information
            
        Returns:
            List[str]: List of suggested usernames for task assignment
        """
        users_text = "\n".join([
            f"User: {row['username']}"
            for _, row in users_df.iterrows()
        ])
        
        prompt = PromptTemplate(
            input_variables=["task", "users"],
            template="""
            Based on the following task and available users, suggest the best team members for assignment:
            
            Task:
            Name: {task['name']}
            Description: {task['description']}
            
            Available Users:
            {users}
            
            Return a list of suggested usernames with brief explanations for each suggestion.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(task=task, users=users_text)
    
    def estimate_task_completion(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate task completion time and effort.
        
        Args:
            task (Dict[str, Any]): Task details
            
        Returns:
            Dict[str, Any]: Estimated completion time and effort level
        """
        prompt = PromptTemplate(
            input_variables=["task_name", "task_description"],
            template="""
            Estimate the completion time and effort level for the following task:
            
            Task Name: {task_name}
            Description: {task_description}
            
            Provide estimates for:
            1. Estimated completion time (in hours/days)
            2. Effort level (Low/Medium/High)
            3. Key factors affecting the estimate
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            task_name=task['name'],
            task_description=task['description']
        )
    
    def analyze_dependencies(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Analyze task dependencies and suggest optimal execution order.
        
        Args:
            tasks (List[Dict[str, Any]]): List of tasks to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping task names to their dependencies
        """
        tasks_text = "\n".join([
            f"Task: {task['name']}\n"
            f"Description: {task['description']}\n"
            for task in tasks
        ])
        
        prompt = PromptTemplate(
            input_variables=["tasks"],
            template="""
            Analyze the following tasks and identify dependencies between them:
            
            {tasks}
            
            For each task, list:
            1. Tasks that must be completed before this task
            2. Tasks that depend on this task
            3. Suggested execution order
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(tasks=tasks_text) 