"""Pydantic models for Composer Kit components."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ComponentProp(BaseModel):
    """Model for a component prop."""

    name: str = Field(description="The name of the prop")
    type: str = Field(description="The TypeScript type of the prop")
    description: str = Field(description="Description of what the prop does")
    required: bool = Field(default=False, description="Whether the prop is required")
    default: Optional[str] = Field(default=None, description="Default value if any")


class ComponentExample(BaseModel):
    """Model for a component usage example."""

    title: str = Field(description="Title of the example")
    description: str = Field(description="Description of what the example demonstrates")
    code: str = Field(description="The example code")
    example_type: str = Field(
        default="basic", description="Type of example (basic, advanced, etc.)"
    )


class Component(BaseModel):
    """Model for a Composer Kit component."""

    name: str = Field(description="The component name")
    category: str = Field(description="The category this component belongs to")
    description: str = Field(description="Brief description of the component")
    detailed_description: Optional[str] = Field(
        default=None, description="Detailed description"
    )
    props: List[ComponentProp] = Field(
        default_factory=list, description="List of component props"
    )
    examples: List[ComponentExample] = Field(
        default_factory=list, description="Usage examples"
    )
    import_path: str = Field(description="Import path for the component")
    subcomponents: List[str] = Field(
        default_factory=list, description="List of subcomponent names"
    )


class InstallationGuide(BaseModel):
    """Model for installation instructions."""

    package_manager: str = Field(description="Package manager name")
    install_command: str = Field(description="Installation command")
    setup_code: str = Field(description="Setup code example")
    additional_steps: List[str] = Field(
        default_factory=list, description="Additional setup steps"
    )


class ComponentSearchResult(BaseModel):
    """Model for component search results."""

    component: Component = Field(description="The matching component")
    relevance_score: float = Field(description="Relevance score for the search")
    matching_fields: List[str] = Field(
        description="Fields that matched the search query"
    )


class ComponentsResponse(BaseModel):
    """Model for listing all components."""

    components: List[Component] = Field(description="List of all components")
    categories: List[str] = Field(description="List of all categories")
    total_count: int = Field(description="Total number of components")
