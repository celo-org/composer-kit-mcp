"""Integration tests for MCP server tools."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.composer_kit_mcp.server import call_tool, list_tools
from src.composer_kit_mcp.components.models import (
    Component,
    ComponentExample,
    ComponentProp,
)
from mcp.types import TextContent


class TestMCPServerTools:
    """Test cases for MCP server tool integration."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component for testing."""
        return Component(
            name="test-component",
            display_name="Test Component",
            description="A test component for unit testing",
            category="Test Components",
            source_code="test source code",
            file_path="test/path.tsx",
            props=[
                ComponentProp(
                    name="title",
                    type="string",
                    description="Component title",
                    required=True,
                ),
                ComponentProp(
                    name="optional",
                    type="boolean",
                    description="Optional prop",
                    required=False,
                    default="false",
                ),
            ],
            examples=[
                ComponentExample(
                    name="test-basic",
                    description="Basic test example",
                    code="example code",
                    file_path="test/example.tsx",
                    category="example",
                )
            ],
            dependencies=["@composer-kit/ui"],
            installation_command="npm install @composer-kit/ui",
            documentation_url="https://github.com/celo-org/composer-kit",
            last_updated=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that all expected tools are listed."""
        tools = await list_tools()

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "list_components",
            "get_component",
            "get_component_example",
            "search_components",
            "get_component_props",
            "get_installation_guide",
            "get_components_by_category",
            "debug_github_access",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

        # Check that each tool has proper schema
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")

    @pytest.mark.asyncio
    async def test_list_components_tool(self, mock_component):
        """Test the list_components tool."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.list_components = AsyncMock(return_value=[mock_component])

            result = await call_tool("list_components", {})

            assert len(result) == 1
            assert isinstance(result[0], TextContent)

            data = json.loads(result[0].text)
            assert data["total_components"] == 1
            assert "Test Components" in data["categories"]
            assert len(data["components"]) == 1
            assert data["components"][0]["name"] == "test-component"

    @pytest.mark.asyncio
    async def test_list_components_empty(self):
        """Test list_components when no components are found."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.list_components = AsyncMock(return_value=[])

            result = await call_tool("list_components", {})

            data = json.loads(result[0].text)
            assert data["total_components"] == 0
            assert data["categories"] == {}
            assert data["components"] == []

    @pytest.mark.asyncio
    async def test_get_component_tool(self, mock_component):
        """Test the get_component tool."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=mock_component)

            result = await call_tool(
                "get_component", {"component_name": "test-component"}
            )

            assert len(result) == 1
            data = json.loads(result[0].text)

            assert data["component"]["name"] == "test-component"
            assert data["component"]["display_name"] == "Test Component"
            assert data["source_code"] == "test source code"
            assert len(data["props"]) == 2
            assert len(data["examples"]) == 1

    @pytest.mark.asyncio
    async def test_get_component_not_found(self):
        """Test get_component when component is not found."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=None)

            result = await call_tool("get_component", {"component_name": "nonexistent"})

            assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_component_missing_name(self):
        """Test get_component with missing component_name."""
        result = await call_tool("get_component", {})

        assert "component_name is required" in result[0].text

    @pytest.mark.asyncio
    async def test_get_component_example_tool(self, mock_component):
        """Test the get_component_example tool."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=mock_component)

            result = await call_tool(
                "get_component_example", {"component_name": "test-component"}
            )

            data = json.loads(result[0].text)
            assert data["component_name"] == "test-component"
            assert len(data["examples"]) == 1
            assert data["examples"][0]["name"] == "test-basic"

    @pytest.mark.asyncio
    async def test_get_component_example_with_type_filter(self, mock_component):
        """Test get_component_example with example type filter."""
        # Add another example
        mock_component.examples.append(
            ComponentExample(
                name="test-advanced",
                description="Advanced test example",
                code="advanced code",
                file_path="test/advanced.tsx",
                category="example",
            )
        )

        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=mock_component)

            result = await call_tool(
                "get_component_example",
                {"component_name": "test-component", "example_type": "basic"},
            )

            data = json.loads(result[0].text)
            assert len(data["examples"]) == 1
            assert data["examples"][0]["name"] == "test-basic"

    @pytest.mark.asyncio
    async def test_get_component_example_no_examples(self):
        """Test get_component_example when component has no examples."""
        mock_component = Component(
            name="no-examples",
            display_name="No Examples",
            description="Component without examples",
            category="Test",
            source_code="code",
            file_path="path",
            props=[],
            examples=[],  # No examples
            dependencies=[],
            installation_command="npm install",
            documentation_url="url",
            last_updated=datetime.now(),
        )

        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=mock_component)

            result = await call_tool(
                "get_component_example", {"component_name": "no-examples"}
            )

            assert "No examples found" in result[0].text

    @pytest.mark.asyncio
    async def test_search_components_tool(self, mock_component):
        """Test the search_components tool."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.search_components = AsyncMock(return_value=[mock_component])

            result = await call_tool("search_components", {"query": "test"})

            data = json.loads(result[0].text)
            assert data["query"] == "test"
            assert data["total_results"] == 1
            assert len(data["components"]) == 1

    @pytest.mark.asyncio
    async def test_search_components_missing_query(self):
        """Test search_components with missing query."""
        result = await call_tool("search_components", {})

        assert "query is required" in result[0].text

    @pytest.mark.asyncio
    async def test_get_component_props_tool(self, mock_component):
        """Test the get_component_props tool."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=mock_component)

            result = await call_tool(
                "get_component_props", {"component_name": "test-component"}
            )

            data = json.loads(result[0].text)
            assert data["component_name"] == "test-component"
            assert data["total_props"] == 2
            assert len(data["props"]) == 2

            # Check prop details
            prop_names = [prop["name"] for prop in data["props"]]
            assert "title" in prop_names
            assert "optional" in prop_names

    @pytest.mark.asyncio
    async def test_get_installation_guide_default(self):
        """Test get_installation_guide with default package manager."""
        result = await call_tool("get_installation_guide", {})

        data = json.loads(result[0].text)
        assert data["package_manager"] == "npm"
        assert (
            "npm install @composer-kit/ui"
            in data["installation_guide"]["install_command"]
        )

    @pytest.mark.asyncio
    async def test_get_installation_guide_yarn(self):
        """Test get_installation_guide with yarn."""
        result = await call_tool("get_installation_guide", {"package_manager": "yarn"})

        data = json.loads(result[0].text)
        assert data["package_manager"] == "yarn"
        assert (
            "yarn add @composer-kit/ui" in data["installation_guide"]["install_command"]
        )

    @pytest.mark.asyncio
    async def test_get_components_by_category_tool(self, mock_component):
        """Test the get_components_by_category tool."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_components_by_category = AsyncMock(
                return_value=[mock_component]
            )

            result = await call_tool(
                "get_components_by_category", {"category": "Test Components"}
            )

            data = json.loads(result[0].text)
            assert data["category"] == "Test Components"
            assert data["total_components"] == 1
            assert len(data["components"]) == 1

    @pytest.mark.asyncio
    async def test_get_components_by_category_missing_category(self):
        """Test get_components_by_category with missing category."""
        result = await call_tool("get_components_by_category", {})

        assert "category is required" in result[0].text

    @pytest.mark.asyncio
    async def test_debug_github_access_tool(self):
        """Test the debug_github_access tool."""
        mock_debug_info = {
            "raw_base_url": "https://raw.githubusercontent.com",
            "repo_owner": "celo-org",
            "repo_name": "composer-kit",
            "test_results": {
                "readme_access": {"success": True, "content_length": 1000},
                "component_discovery": {"success": True, "components_found": 5},
            },
        }

        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.debug_github_access = AsyncMock(return_value=mock_debug_info)

            result = await call_tool("debug_github_access", {})

            data = json.loads(result[0].text)
            assert data["raw_base_url"] == "https://raw.githubusercontent.com"
            assert data["test_results"]["readme_access"]["success"] is True
            assert data["test_results"]["component_discovery"]["components_found"] == 5

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling an unknown tool."""
        result = await call_tool("unknown_tool", {})

        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test error handling in tool calls."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.list_components.side_effect = Exception("Test error")

            result = await call_tool("list_components", {})

            assert "Error executing tool" in result[0].text
            assert "Test error" in result[0].text

    @pytest.mark.asyncio
    async def test_component_service_initialization(self):
        """Test that component service is properly initialized."""
        # This test verifies that the global component service is used
        # The service is initialized at module level, so we just test that it works
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.list_components = AsyncMock(return_value=[])

            result = await call_tool("list_components", {})

            # Should have used the global service instance
            mock_service.list_components.assert_called_once()

    @pytest.mark.asyncio
    async def test_json_serialization_with_datetime(self, mock_component):
        """Test that datetime objects are properly serialized."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=mock_component)

            result = await call_tool(
                "get_component", {"component_name": "test-component"}
            )

            # Should not raise JSON serialization error
            data = json.loads(result[0].text)
            assert "component" in data

    @pytest.mark.asyncio
    async def test_all_package_managers(self):
        """Test installation guide for all supported package managers."""
        package_managers = ["npm", "yarn", "pnpm", "bun"]

        for pm in package_managers:
            result = await call_tool("get_installation_guide", {"package_manager": pm})
            data = json.loads(result[0].text)

            assert data["package_manager"] == pm
            assert pm in data["installation_guide"]["install_command"]

    @pytest.mark.asyncio
    async def test_component_data_completeness(self, mock_component):
        """Test that component data includes all expected fields."""
        with patch("src.composer_kit_mcp.server.component_service") as mock_service:
            mock_service.get_component = AsyncMock(return_value=mock_component)

            result = await call_tool(
                "get_component", {"component_name": "test-component"}
            )
            data = json.loads(result[0].text)

            # Check component metadata
            component_data = data["component"]
            required_fields = [
                "name",
                "display_name",
                "description",
                "category",
                "installation_command",
                "documentation_url",
                "dependencies",
                "props_count",
                "examples_count",
            ]

            for field in required_fields:
                assert field in component_data

            # Check props structure
            for prop in data["props"]:
                assert "name" in prop
                assert "type" in prop
                assert "required" in prop

            # Check examples structure
            for example in data["examples"]:
                assert "name" in example
                assert "description" in example
                assert "file_path" in example
