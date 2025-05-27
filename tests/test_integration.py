"""End-to-end integration tests for the MCP server."""

import pytest
import asyncio
import json
from unittest.mock import patch

from src.composer_kit_mcp.components.service import ComponentService
from src.composer_kit_mcp.server import call_tool


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_component_discovery_flow(self):
        """Test the complete flow from component discovery to retrieval."""
        service = ComponentService()

        # Clear cache to ensure fresh data
        await service.clear_cache()

        # Test component discovery
        components = await service._discover_components()
        assert len(components) > 0, "Should discover at least some components"

        # Test that we can build components from discovered names
        for component_name in components[:3]:  # Test first 3 components
            component = await service._build_component(component_name)
            assert (
                component is not None
            ), f"Should be able to build component {component_name}"
            assert component.name == component_name
            assert component.display_name is not None
            assert component.category is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_github_access(self):
        """Test actual GitHub access without mocking."""
        service = ComponentService()

        # Test fetching README
        readme_content = await service._get_raw_file_content("README.md")
        assert readme_content is not None, "Should be able to fetch README"
        assert len(readme_content) > 1000, "README should have substantial content"
        assert (
            "composer-kit" in readme_content.lower()
        ), "README should mention composer-kit"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_component_examples_retrieval(self):
        """Test retrieving real component examples."""
        service = ComponentService()

        # Test known components
        known_components = ["address", "wallet", "payment"]

        for component_name in known_components:
            if await service._component_exists(component_name):
                examples = await service._get_component_examples(component_name)
                assert (
                    len(examples) > 0
                ), f"Component {component_name} should have examples"

                for example in examples:
                    assert (
                        example.code is not None
                    ), f"Example {example.name} should have code"
                    assert (
                        len(example.code) > 0
                    ), f"Example {example.name} should have non-empty code"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_mcp_tools_integration(self):
        """Test MCP tools with real data."""
        # Test list_components
        result = await call_tool("list_components", {})
        assert len(result) == 1

        data = json.loads(result[0].text)
        assert data["total_components"] >= 0, "Should return valid component count"

        if data["total_components"] > 0:
            # Test get_component with a real component
            component_name = data["components"][0]["name"]

            result = await call_tool(
                "get_component", {"component_name": component_name}
            )
            component_data = json.loads(result[0].text)

            assert "component" in component_data
            assert component_data["component"]["name"] == component_name

            # Test get_component_example
            result = await call_tool(
                "get_component_example", {"component_name": component_name}
            )
            example_data = json.loads(result[0].text)

            assert "examples" in example_data
            assert example_data["component_name"] == component_name

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_functionality(self):
        """Test search functionality with real data."""
        service = ComponentService()

        # Get all components first
        components = await service.list_components()

        if len(components) > 0:
            # Test search by partial name
            first_component = components[0]
            search_term = first_component.name[:3]  # First 3 characters

            search_results = await service.search_components(search_term)
            assert (
                len(search_results) > 0
            ), f"Search for '{search_term}' should return results"

            # Test search by category
            category_results = await service.get_components_by_category(
                first_component.category
            )
            assert (
                len(category_results) > 0
            ), f"Category '{first_component.category}' should have components"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_caching_behavior(self):
        """Test that caching works correctly in real scenarios."""
        service = ComponentService()

        # Clear cache
        await service.clear_cache()

        # First call should hit the network
        start_time = asyncio.get_event_loop().time()
        components1 = await service.list_components()
        first_call_time = asyncio.get_event_loop().time() - start_time

        # Second call should use cache (should be faster)
        start_time = asyncio.get_event_loop().time()
        components2 = await service.list_components()
        second_call_time = asyncio.get_event_loop().time() - start_time

        # Results should be the same
        assert len(components1) == len(components2)

        # Second call should be significantly faster (cached)
        assert (
            second_call_time < first_call_time * 0.5
        ), "Cached call should be much faster"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_with_invalid_requests(self):
        """Test error handling with invalid requests."""
        # Test with non-existent component
        result = await call_tool(
            "get_component", {"component_name": "non-existent-component"}
        )
        assert "not found" in result[0].text.lower()

        # Test with missing required parameters
        result = await call_tool("get_component", {})
        assert "required" in result[0].text.lower()

        # Test search with empty query
        result = await call_tool("search_components", {"query": ""})
        data = json.loads(result[0].text)
        assert data["total_results"] == 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_component_data_consistency(self):
        """Test that component data is consistent across different access methods."""
        service = ComponentService()

        # Get components through different methods
        all_components = await service.list_components()

        if len(all_components) > 0:
            test_component = all_components[0]
            component_name = test_component.name

            # Get the same component directly
            direct_component = await service.get_component(component_name)

            # Data should be consistent
            assert direct_component.name == test_component.name
            assert direct_component.display_name == test_component.display_name
            assert direct_component.category == test_component.category
            assert len(direct_component.props) == len(test_component.props)
            assert len(direct_component.examples) == len(test_component.examples)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_debug_tool_provides_useful_info(self):
        """Test that debug tool provides useful debugging information."""
        result = await call_tool("debug_github_access", {})
        debug_data = json.loads(result[0].text)

        assert "raw_base_url" in debug_data
        assert "test_results" in debug_data
        assert "readme_access" in debug_data["test_results"]
        assert "component_discovery" in debug_data["test_results"]

        # Should provide meaningful results
        readme_result = debug_data["test_results"]["readme_access"]
        assert "success" in readme_result

        discovery_result = debug_data["test_results"]["component_discovery"]
        assert "success" in discovery_result
        assert "components_found" in discovery_result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_installation_guide_completeness(self):
        """Test that installation guide provides complete information."""
        package_managers = ["npm", "yarn", "pnpm", "bun"]

        for pm in package_managers:
            result = await call_tool("get_installation_guide", {"package_manager": pm})
            data = json.loads(result[0].text)

            assert data["package_manager"] == pm
            assert "installation_guide" in data
            assert "basic_usage" in data

            guide = data["installation_guide"]
            assert "install_command" in guide
            assert "setup_steps" in guide
            assert pm in guide["install_command"]

            usage = data["basic_usage"]
            assert "provider_setup" in usage
            assert "component_import" in usage

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_component_props_extraction(self):
        """Test that component props are properly extracted from real code."""
        service = ComponentService()

        components = await service.list_components()

        for component in components[:3]:  # Test first 3 components
            if component.source_code:
                # If we have source code, we should be able to extract some information
                props = service._extract_component_props(component.source_code)

                # Even if no props are found, the extraction should not fail
                assert isinstance(props, list)

                for prop in props:
                    assert hasattr(prop, "name")
                    assert hasattr(prop, "type")
                    assert hasattr(prop, "required")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_network_resilience(self):
        """Test behavior when network requests fail."""
        service = ComponentService()

        # Test with invalid file path
        content = await service._get_raw_file_content("nonexistent/path/file.tsx")
        assert content is None, "Should return None for non-existent files"

        # Test component existence check with invalid component
        exists = await service._component_exists("definitely-not-a-real-component")
        assert exists is False, "Should return False for non-existent components"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_requests(self):
        """Test that the service handles concurrent requests correctly."""
        service = ComponentService()

        # Make multiple concurrent requests
        tasks = [
            service.list_components(),
            service.debug_github_access(),
            service._get_raw_file_content("README.md"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All requests should complete without exceptions
        for result in results:
            assert not isinstance(result, Exception), f"Request failed with: {result}"

        # Results should be valid
        components, debug_info, readme = results
        assert isinstance(components, list)
        assert isinstance(debug_info, dict)
        assert isinstance(readme, str) or readme is None


# Pytest configuration for integration tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may be slow)"
    )


# Skip integration tests by default unless explicitly requested
def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --integration flag is used."""
    if not config.getoption("--integration", default=False):
        skip_integration = pytest.mark.skip(reason="need --integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
