"""Composer Kit MCP Server.

A Model Context Protocol server for Composer Kit UI components.
Provides access to component source code, examples, and documentation.
"""

__version__ = "0.1.0"
__author__ = "viral-sangani"
__email__ = "viral.sangani2011@gmail.com"

from .server import server

__all__ = ["server"]
