"""
AI module for project tracking application.
Provides AI/LLM capabilities for project analysis, task management, and user experience enhancement.
"""

from .project_analyzer import ProjectAnalyzer
from .task_manager import TaskManager
from .search_engine import SearchEngine
from .recommendation_engine import RecommendationEngine

__all__ = ['ProjectAnalyzer', 'TaskManager', 'SearchEngine', 'RecommendationEngine'] 