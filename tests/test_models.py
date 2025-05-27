"""Unit tests for data models."""

import pytest
from datetime import datetime

from src.composer_kit_mcp.components.models import (
    Component,
    ComponentExample,
    ComponentProp,
    ComponentRegistry,
)


class TestComponentProp:
    """Test cases for ComponentProp model."""

    def test_component_prop_creation(self):
        """Test creating a ComponentProp."""
        prop = ComponentProp(
            name="title",
            type="string",
            description="Component title",
            required=True,
            default="Default Title",
        )

        assert prop.name == "title"
        assert prop.type == "string"
        assert prop.description == "Component title"
        assert prop.required is True
        assert prop.default == "Default Title"

    def test_component_prop_optional_fields(self):
        """Test ComponentProp with optional fields."""
        prop = ComponentProp(
            name="optional_prop",
            type="boolean",
            description="Optional boolean prop",
        )

        assert prop.name == "optional_prop"
        assert prop.type == "boolean"
        assert prop.description == "Optional boolean prop"
        assert prop.required is False
        assert prop.default is None

    def test_component_prop_dict_conversion(self):
        """Test converting ComponentProp to dict."""
        prop = ComponentProp(
            name="test",
            type="string",
            description="Test prop",
            required=True,
        )

        prop_dict = prop.model_dump()
        assert prop_dict["name"] == "test"
        assert prop_dict["type"] == "string"
        assert prop_dict["description"] == "Test prop"
        assert prop_dict["required"] is True


class TestComponentExample:
    """Test cases for ComponentExample model."""

    def test_component_example_creation(self):
        """Test creating a ComponentExample."""
        example = ComponentExample(
            name="basic-example",
            description="Basic usage example",
            code="<Component />",
            file_path="examples/basic.tsx",
            category="example",
        )

        assert example.name == "basic-example"
        assert example.description == "Basic usage example"
        assert example.code == "<Component />"
        assert example.file_path == "examples/basic.tsx"
        assert example.category == "example"

    def test_component_example_optional_fields(self):
        """Test ComponentExample with optional fields."""
        example = ComponentExample(
            name="minimal",
            description="Minimal example",
            code="code",
            file_path="path",
        )

        assert example.name == "minimal"
        assert example.code == "code"
        assert example.file_path == "path"
        assert example.description == "Minimal example"
        assert example.category is None


class TestComponent:
    """Test cases for Component model."""

    @pytest.fixture
    def sample_component(self):
        """Create a sample component for testing."""
        return Component(
            name="test-component",
            display_name="Test Component",
            description="A test component",
            category="Test",
            source_code="component code",
            file_path="test/component.tsx",
            props=[
                ComponentProp(
                    name="title", type="string", description="Title prop", required=True
                ),
                ComponentProp(
                    name="optional",
                    type="boolean",
                    description="Optional prop",
                    required=False,
                ),
            ],
            examples=[
                ComponentExample(
                    name="basic",
                    description="Basic example",
                    code="example code",
                    file_path="examples/basic.tsx",
                )
            ],
            dependencies=["@composer-kit/ui"],
            installation_command="npm install @composer-kit/ui",
            documentation_url="https://github.com/celo-org/composer-kit",
            last_updated=datetime.now(),
        )

    def test_component_creation(self, sample_component):
        """Test creating a Component."""
        assert sample_component.name == "test-component"
        assert sample_component.display_name == "Test Component"
        assert sample_component.description == "A test component"
        assert sample_component.category == "Test"
        assert len(sample_component.props) == 2
        assert len(sample_component.examples) == 1
        assert len(sample_component.dependencies) == 1

    def test_component_optional_fields(self):
        """Test Component with minimal required fields."""
        component = Component(
            name="minimal",
            display_name="Minimal",
            description="Minimal component",
            category="Test",
            source_code="code",
            file_path="path",
            props=[],
            examples=[],
            dependencies=[],
            installation_command="install",
            documentation_url="url",
            last_updated=datetime.now(),
        )

        assert component.name == "minimal"
        assert len(component.props) == 0
        assert len(component.examples) == 0
        assert len(component.dependencies) == 0

    def test_component_dict_conversion(self, sample_component):
        """Test converting Component to dict."""
        component_dict = sample_component.model_dump()

        assert component_dict["name"] == "test-component"
        assert component_dict["display_name"] == "Test Component"
        assert len(component_dict["props"]) == 2
        assert len(component_dict["examples"]) == 1
        assert isinstance(component_dict["last_updated"], datetime)


class TestComponentRegistry:
    """Test cases for ComponentRegistry model."""

    @pytest.fixture
    def sample_registry(self):
        """Create a sample registry for testing."""
        component1 = Component(
            name="component1",
            display_name="Component 1",
            description="First component",
            category="Core",
            source_code="code1",
            file_path="path1",
            props=[],
            examples=[],
            dependencies=[],
            installation_command="install",
            documentation_url="url",
            last_updated=datetime.now(),
        )

        component2 = Component(
            name="component2",
            display_name="Component 2",
            description="Second component with wallet functionality",
            category="Wallet",
            source_code="code2",
            file_path="path2",
            props=[],
            examples=[],
            dependencies=[],
            installation_command="install",
            documentation_url="url",
            last_updated=datetime.now(),
        )

        registry = ComponentRegistry()
        registry.components = {
            "component1": component1,
            "component2": component2,
        }
        registry.categories = ["Core", "Wallet"]
        registry.last_updated = datetime.now()

        return registry

    def test_registry_creation(self):
        """Test creating an empty ComponentRegistry."""
        registry = ComponentRegistry()

        assert len(registry.components) == 0
        assert len(registry.categories) == 0
        assert registry.last_updated is None

    def test_get_component(self, sample_registry):
        """Test getting a component by name."""
        component = sample_registry.get_component("component1")
        assert component is not None
        assert component.name == "component1"

        # Test case insensitive
        component = sample_registry.get_component("COMPONENT1")
        assert component is not None
        assert component.name == "component1"

        # Test non-existent component
        component = sample_registry.get_component("nonexistent")
        assert component is None

    def test_search_components(self, sample_registry):
        """Test searching components."""
        # Search by name
        results = sample_registry.search_components("component1")
        assert len(results) == 1
        assert results[0].name == "component1"

        # Search by description
        results = sample_registry.search_components("wallet")
        assert len(results) == 1
        assert results[0].name == "component2"

        # Search by category
        results = sample_registry.search_components("Core")
        assert len(results) == 1
        assert results[0].name == "component1"

        # Case insensitive search
        results = sample_registry.search_components("WALLET")
        assert len(results) == 1

        # No matches
        results = sample_registry.search_components("nonexistent")
        assert len(results) == 0

    def test_get_components_by_category(self, sample_registry):
        """Test getting components by category."""
        # Exact category match
        results = sample_registry.get_components_by_category("Core")
        assert len(results) == 1
        assert results[0].name == "component1"

        # Case insensitive
        results = sample_registry.get_components_by_category("wallet")
        assert len(results) == 1
        assert results[0].name == "component2"

        # Non-existent category
        results = sample_registry.get_components_by_category("NonExistent")
        assert len(results) == 0

    def test_registry_dict_conversion(self, sample_registry):
        """Test converting ComponentRegistry to dict."""
        registry_dict = sample_registry.model_dump()

        assert "components" in registry_dict
        assert "categories" in registry_dict
        assert "last_updated" in registry_dict
        assert len(registry_dict["components"]) == 2
        assert len(registry_dict["categories"]) == 2

    def test_add_component_to_registry(self):
        """Test adding components to registry."""
        registry = ComponentRegistry()

        component = Component(
            name="new-component",
            display_name="New Component",
            description="A new component",
            category="New",
            source_code="code",
            file_path="path",
            props=[],
            examples=[],
            dependencies=[],
            installation_command="install",
            documentation_url="url",
            last_updated=datetime.now(),
        )

        registry.components["new-component"] = component
        registry.categories.append("New")

        assert len(registry.components) == 1
        assert "new-component" in registry.components
        assert "New" in registry.categories

    def test_empty_search(self, sample_registry):
        """Test search with empty query."""
        # Empty string should return no results
        results = sample_registry.search_components("")
        assert len(results) == 0

        # Test with whitespace only
        results = sample_registry.search_components("   ")
        assert len(results) == 0

    def test_partial_matches(self, sample_registry):
        """Test partial string matches in search."""
        # Partial name match
        results = sample_registry.search_components("comp")
        assert len(results) == 2  # Should match both components

        # Partial description match
        results = sample_registry.search_components("Second")
        assert len(results) == 1
        assert results[0].name == "component2"

    def test_multiple_category_search(self, sample_registry):
        """Test searching across multiple categories."""
        # Add another component in Core category
        component3 = Component(
            name="component3",
            display_name="Component 3",
            description="Third component",
            category="Core",
            source_code="code3",
            file_path="path3",
            props=[],
            examples=[],
            dependencies=[],
            installation_command="install",
            documentation_url="url",
            last_updated=datetime.now(),
        )

        sample_registry.components["component3"] = component3

        # Search should return both Core components
        results = sample_registry.get_components_by_category("Core")
        assert len(results) == 2
        component_names = [comp.name for comp in results]
        assert "component1" in component_names
        assert "component3" in component_names
