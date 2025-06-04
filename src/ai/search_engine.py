"""
Search engine module that provides AI-powered semantic search capabilities.
"""

from typing import List, Dict, Any
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import numpy as np

class SearchEngine:
    """
    Provides semantic search capabilities across projects and problems.
    
    Attributes:
        llm: The language model instance used for search
        embeddings: The embeddings model for semantic search
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the search engine with OpenAI API key.
        
        Args:
            api_key (str): OpenAI API key for accessing the language model
        """
        self.llm = OpenAI(temperature=0.7, openai_api_key=api_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    def semantic_search(self, query: str, projects_df: pd.DataFrame, problems_df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform semantic search across projects and problems.
        
        Args:
            query (str): Search query
            projects_df (pd.DataFrame): DataFrame containing projects data
            problems_df (pd.DataFrame): DataFrame containing problems data
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Search results for projects and problems
        """
        # Create text representations of projects and problems
        project_texts = [
            f"Project: {row['name']}\nDescription: {row['description']}\nStatus: {row['status']}"
            for _, row in projects_df.iterrows()
        ]
        problem_texts = [
            f"Problem: {row['name']}\nDescription: {row['description']}\nStatus: {row['status']}"
            for _, row in problems_df.iterrows()
        ]
        
        # Create embeddings for all texts
        all_texts = project_texts + problem_texts
        embeddings = self.embeddings.embed_documents(all_texts)
        
        # Create embeddings for the query
        query_embedding = self.embeddings.embed_query(query)
        
        # Calculate similarities
        similarities = [
            np.dot(query_embedding, doc_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))
            for doc_embedding in embeddings
        ]
        
        # Get top results
        top_indices = np.argsort(similarities)[-5:][::-1]
        
        results = {
            "projects": [],
            "problems": []
        }
        
        for idx in top_indices:
            if idx < len(project_texts):
                results["projects"].append(projects_df.iloc[idx].to_dict())
            else:
                problem_idx = idx - len(project_texts)
                results["problems"].append(problems_df.iloc[problem_idx].to_dict())
        
        return results
    
    def natural_language_query(self, query: str, projects_df: pd.DataFrame, problems_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process natural language queries and return structured results.
        
        Args:
            query (str): Natural language query
            projects_df (pd.DataFrame): DataFrame containing projects data
            problems_df (pd.DataFrame): DataFrame containing problems data
            
        Returns:
            Dict[str, Any]: Structured query results
        """
        prompt = PromptTemplate(
            input_variables=["query", "projects", "problems"],
            template="""
            Process the following natural language query and return relevant information:
            
            Query: {query}
            
            Available Projects:
            {projects}
            
            Available Problems:
            {problems}
            
            Return a structured response that directly answers the query.
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
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            query=query,
            projects=projects_text,
            problems=problems_text
        )
    
    def context_aware_search(self, query: str, context: Dict[str, Any], projects_df: pd.DataFrame, problems_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform context-aware search based on user's current context.
        
        Args:
            query (str): Search query
            context (Dict[str, Any]): Current user context (e.g., current project, role)
            projects_df (pd.DataFrame): DataFrame containing projects data
            problems_df (pd.DataFrame): DataFrame containing problems data
            
        Returns:
            Dict[str, Any]: Context-aware search results
        """
        prompt = PromptTemplate(
            input_variables=["query", "context", "projects", "problems"],
            template="""
            Based on the following context and query, find the most relevant information:
            
            Context:
            {context}
            
            Query: {query}
            
            Available Projects:
            {projects}
            
            Available Problems:
            {problems}
            
            Return the most relevant information considering the user's context.
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
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            query=query,
            context=str(context),
            projects=projects_text,
            problems=problems_text
        ) 