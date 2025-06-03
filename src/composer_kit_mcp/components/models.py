"""Pydantic models for Composer Kit components."""

from pydantic import BaseModel, Field


class ComponentProp(BaseModel):
    """Model for a component prop."""

    name: str = Field(description="The name of the prop")
    type: str = Field(description="The TypeScript type of the prop")
    description: str = Field(description="Description of what the prop does")
    required: bool = Field(default=False, description="Whether the prop is required")
    default: str | None = Field(default=None, description="Default value if any")
    supports_className: bool = Field(default=True, description="Whether this prop supports className")


class ComponentExample(BaseModel):
    """Model for a component usage example."""

    title: str = Field(description="Title of the example")
    description: str = Field(description="Description of what the example demonstrates")
    code: str = Field(description="The example code")
    example_type: str = Field(default="basic", description="Type of example (basic, advanced, etc.)")


class Component(BaseModel):
    """Model for a Composer Kit component."""

    name: str = Field(description="The component name")
    category: str = Field(description="The category this component belongs to")
    description: str = Field(description="Brief description of the component")
    detailed_description: str | None = Field(default=None, description="Detailed description")
    props: list[ComponentProp] = Field(default_factory=list, description="List of component props")
    examples: list[ComponentExample] = Field(default_factory=list, description="Usage examples")
    import_path: str = Field(description="Import path for the component")
    subcomponents: list[str] = Field(default_factory=list, description="List of subcomponent names")
    supports_className: bool = Field(default=True, description="Whether this component supports className prop")


class InstallationGuide(BaseModel):
    """Model for installation instructions."""

    package_manager: str = Field(description="Package manager name")
    install_command: str = Field(description="Installation command")
    setup_code: str = Field(description="Setup code example")
    additional_steps: list[str] = Field(default_factory=list, description="Additional setup steps")


class ComponentSearchResult(BaseModel):
    """Model for component search results."""

    component: Component = Field(description="The matching component")
    relevance_score: float = Field(description="Relevance score for the search")
    matching_fields: list[str] = Field(description="Fields that matched the search query")


class ComponentsResponse(BaseModel):
    """Model for listing all components."""

    components: list[Component] = Field(description="List of all components")
    categories: list[str] = Field(description="List of all categories")
    total_count: int = Field(description="Total number of components")


# New models for Celo Composer support


class CeloComposerTemplate(BaseModel):
    """Model for a Celo Composer template."""

    name: str = Field(description="Template name")
    description: str = Field(description="Template description")
    use_cases: list[str] = Field(description="Common use cases for this template")
    features: list[str] = Field(description="Key features of this template")
    documentation_url: str | None = Field(default=None, description="Link to template documentation")


class CeloComposerFramework(BaseModel):
    """Model for a Celo Composer framework."""

    name: str = Field(description="Framework name")
    description: str = Field(description="Framework description")
    documentation_url: str = Field(description="Link to framework documentation")


class CeloComposerProject(BaseModel):
    """Model for a Celo Composer project configuration."""

    name: str = Field(description="Project name")
    owner: str = Field(description="Project owner name")
    include_hardhat: bool = Field(description="Whether to include Hardhat in the project")
    template: str = Field(description="Template to use (Minipay, Valora, or Social Connect)")
    description: str | None = Field(default=None, description="Project description")


class CeloComposerCommand(BaseModel):
    """Model for Celo Composer CLI commands."""

    command: str = Field(description="The CLI command to execute")
    description: str = Field(description="Description of what the command does")
    flags: dict[str, str] = Field(default_factory=dict, description="Available flags and their descriptions")


class CeloComposerGuide(BaseModel):
    """Model for Celo Composer usage guides."""

    title: str = Field(description="Guide title")
    description: str = Field(description="Guide description")
    steps: list[str] = Field(description="Step-by-step instructions")
    commands: list[str] = Field(default_factory=list, description="Commands to run")
    notes: list[str] = Field(default_factory=list, description="Additional notes and tips")
