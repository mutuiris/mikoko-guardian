"""
Addy Weather Monitor Agent Package
"""
from .server import agent

# Make agent accessible at package level
__version__ = "3.0.0"
__all__ = ["agent"]