"""Data models for Composer Kit components."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ComponentProp(BaseModel):
    """Model for component prop information."""

    name: str
    type: str
    description: str
    default: Optional[str] = None
    required: bool = False


class ComponentExample(BaseModel):
    """Model for component example."""

    name: str
    description: str
    code: str
    file_path: str
    category: Optional[str] = None


class Component(BaseModel):
    """Model for a Composer Kit component."""

    name: str
    display_name: str
    description: str
    category: str
    source_code: Optional[str] = None
    file_path: Optional[str] = None
    props: List[ComponentProp] = Field(default_factory=list)
    examples: List[ComponentExample] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    installation_command: Optional[str] = None
    documentation_url: Optional[str] = None
    last_updated: Optional[datetime] = None


class ComponentRegistry(BaseModel):
    """Registry of all available components."""

    components: Dict[str, Component] = Field(default_factory=dict)
    categories: List[str] = Field(default_factory=list)
    last_updated: Optional[datetime] = None

    def get_component(self, name: str) -> Optional[Component]:
        """Get component by name (case-insensitive)."""
        name_lower = name.lower()
        for comp_name, component in self.components.items():
            if (
                comp_name.lower() == name_lower
                or component.display_name.lower() == name_lower
            ):
                return component
        return None

    def search_components(self, query: str) -> List[Component]:
        """Search components by name or description."""
        query_lower = query.lower()
        results = []

        for component in self.components.values():
            if (
                query_lower in component.name.lower()
                or query_lower in component.display_name.lower()
                or query_lower in component.description.lower()
                or query_lower in component.category.lower()
            ):
                results.append(component)

        return results

    def get_components_by_category(self, category: str) -> List[Component]:
        """Get all components in a specific category."""
        return [
            component
            for component in self.components.values()
            if component.category.lower() == category.lower()
        ]


class GitHubFile(BaseModel):
    """Model for GitHub file information."""

    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: Optional[str] = None
    type: str  # "file" or "dir"
    content: Optional[str] = None
    encoding: Optional[str] = None


class GitHubDirectory(BaseModel):
    """Model for GitHub directory contents."""

    path: str
    files: List[GitHubFile] = Field(default_factory=list)
    directories: List[str] = Field(default_factory=list)
