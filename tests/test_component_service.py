"""Unit tests for ComponentService."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.composer_kit_mcp.components.service import ComponentService
from src.composer_kit_mcp.components.models import (
    Component,
    ComponentExample,
    ComponentProp,
)


class TestComponentService:
    """Test cases for ComponentService."""

    @pytest.fixture
    def service(self):
        """Create a ComponentService instance for testing."""
        return ComponentService()

    @pytest.fixture
    def mock_file_content(self):
        """Mock file content for testing."""
        return """
import { Component } from "@composer-kit/ui";

interface ComponentProps {
  title: string;
  description?: string;
  onClick: () => void;
}

export default function ExampleComponent({ title, description, onClick }: ComponentProps) {
  return (
    <div>
      <h1>{title}</h1>
      {description && <p>{description}</p>}
      <button onClick={onClick}>Click me</button>
    </div>
  );
}
"""

    @pytest.mark.asyncio
    async def test_get_raw_file_content_success(self, service):
        """Test successful file content retrieval."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "test content"

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            content = await service._get_raw_file_content("test/path.tsx")

            assert content == "test content"

    @pytest.mark.asyncio
    async def test_get_raw_file_content_not_found(self, service):
        """Test file not found scenario."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            content = await service._get_raw_file_content("nonexistent/path.tsx")

            assert content is None

    @pytest.mark.asyncio
    async def test_get_raw_file_content_error(self, service):
        """Test error handling in file content retrieval."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                Exception("Network error")
            )

            content = await service._get_raw_file_content("test/path.tsx")

            assert content is None

    @pytest.mark.asyncio
    async def test_discover_components(self, service):
        """Test component discovery."""
        with patch.object(service, "_component_exists") as mock_exists:
            # Mock that some components exist
            mock_exists.side_effect = lambda name: name in [
                "address",
                "wallet",
                "payment",
            ]

            components = await service._discover_components()

            assert "address" in components
            assert "wallet" in components
            assert "payment" in components
            assert len(components) == 3

    @pytest.mark.asyncio
    async def test_component_exists_standard(self, service):
        """Test component existence check for standard components."""
        with patch.object(service, "_get_raw_file_content") as mock_get_content:
            mock_get_content.return_value = "component content"

            exists = await service._component_exists("address")

            assert exists is True
            # Should check for basic.tsx first
            mock_get_content.assert_called_with("apps/docs/examples/address/basic.tsx")

    @pytest.mark.asyncio
    async def test_component_exists_nft_special_case(self, service):
        """Test component existence check for NFT component."""
        with patch.object(service, "_get_raw_file_content") as mock_get_content:
            # First call (mint.tsx) returns content
            mock_get_content.return_value = "nft mint content"

            exists = await service._component_exists("nft")

            assert exists is True
            # Should check for mint.tsx first for NFT
            mock_get_content.assert_called_with("apps/docs/examples/nft/mint.tsx")

    @pytest.mark.asyncio
    async def test_get_component_source_code(self, service, mock_file_content):
        """Test getting component source code."""
        with patch.object(service, "_get_raw_file_content") as mock_get_content:
            mock_get_content.return_value = mock_file_content

            source = await service._get_component_source_code("address")

            assert source == mock_file_content

    @pytest.mark.asyncio
    async def test_get_component_examples_standard(self, service, mock_file_content):
        """Test getting examples for standard components."""
        with patch.object(service, "_get_raw_file_content") as mock_get_content:
            mock_get_content.return_value = mock_file_content

            examples = await service._get_component_examples("address")

            assert len(examples) == 1
            assert examples[0].name == "address-basic"
            assert examples[0].code == mock_file_content

    @pytest.mark.asyncio
    async def test_get_component_examples_nft(self, service):
        """Test getting examples for NFT component."""
        with patch.object(service, "_get_raw_file_content") as mock_get_content:
            # Return different content for mint and preview
            def side_effect(path):
                if "mint.tsx" in path:
                    return "mint example content"
                elif "preview.tsx" in path:
                    return "preview example content"
                return None

            mock_get_content.side_effect = side_effect

            examples = await service._get_component_examples("nft")

            assert len(examples) == 2
            assert any(ex.name == "nft-mint" for ex in examples)
            assert any(ex.name == "nft-preview" for ex in examples)

    def test_extract_component_props(self, service, mock_file_content):
        """Test extracting component props from source code."""
        props = service._extract_component_props(mock_file_content)

        assert len(props) >= 2  # Should find title, description, onClick
        prop_names = [prop.name for prop in props]
        assert "title" in prop_names
        assert "description" in prop_names or "onClick" in prop_names

    def test_get_component_category(self, service):
        """Test getting component category."""
        assert service._get_component_category("address") == "Core Components"
        assert service._get_component_category("wallet") == "Wallet Integration"
        assert service._get_component_category("payment") == "Payment & Transactions"
        assert service._get_component_category("unknown") == "Other"

    @pytest.mark.asyncio
    async def test_build_component(self, service, mock_file_content):
        """Test building a complete component object."""
        with (
            patch.object(service, "_get_component_source_code") as mock_source,
            patch.object(service, "_get_component_examples") as mock_examples,
        ):

            mock_source.return_value = mock_file_content
            mock_examples.return_value = [
                ComponentExample(
                    name="test-example",
                    description="Test example",
                    code="example code",
                    file_path="test/path.tsx",
                    category="example",
                )
            ]

            component = await service._build_component("address")

            assert component is not None
            assert component.name == "address"
            assert component.display_name == "Address"
            assert component.category == "Core Components"
            assert component.source_code == mock_file_content
            assert len(component.examples) == 1

    @pytest.mark.asyncio
    async def test_get_component_registry(self, service):
        """Test getting the complete component registry."""
        with (
            patch.object(service, "_discover_components") as mock_discover,
            patch.object(service, "_build_component") as mock_build,
        ):

            mock_discover.return_value = ["address", "wallet"]
            mock_build.side_effect = [
                Component(
                    name="address",
                    display_name="Address",
                    description="Address component",
                    category="Core Components",
                    source_code="code",
                    file_path="path",
                    props=[],
                    examples=[],
                    dependencies=[],
                    installation_command="npm install",
                    documentation_url="url",
                    last_updated=datetime.now(),
                ),
                Component(
                    name="wallet",
                    display_name="Wallet",
                    description="Wallet component",
                    category="Wallet Integration",
                    source_code="code",
                    file_path="path",
                    props=[],
                    examples=[],
                    dependencies=[],
                    installation_command="npm install",
                    documentation_url="url",
                    last_updated=datetime.now(),
                ),
            ]

            registry = await service.get_component_registry()

            assert len(registry.components) == 2
            assert "address" in registry.components
            assert "wallet" in registry.components
            assert "Core Components" in registry.categories
            assert "Wallet Integration" in registry.categories

    @pytest.mark.asyncio
    async def test_list_components(self, service):
        """Test listing all components."""
        with patch.object(service, "get_component_registry") as mock_registry:
            mock_component = Component(
                name="test",
                display_name="Test",
                description="Test component",
                category="Test",
                source_code="code",
                file_path="path",
                props=[],
                examples=[],
                dependencies=[],
                installation_command="npm install",
                documentation_url="url",
                last_updated=datetime.now(),
            )

            mock_registry.return_value.components = {"test": mock_component}

            components = await service.list_components()

            assert len(components) == 1
            assert components[0].name == "test"

    @pytest.mark.asyncio
    async def test_search_components(self, service):
        """Test searching components."""
        with patch.object(service, "get_component_registry") as mock_registry:
            mock_registry_instance = MagicMock()
            mock_registry_instance.search_components.return_value = []
            mock_registry.return_value = mock_registry_instance

            results = await service.search_components("wallet")

            assert isinstance(results, list)
            mock_registry.return_value.search_components.assert_called_once_with(
                "wallet"
            )

    @pytest.mark.asyncio
    async def test_get_components_by_category(self, service):
        """Test getting components by category."""
        with patch.object(service, "get_component_registry") as mock_registry:
            mock_registry_instance = MagicMock()
            mock_registry_instance.get_components_by_category.return_value = []
            mock_registry.return_value = mock_registry_instance

            results = await service.get_components_by_category("Core Components")

            assert isinstance(results, list)
            mock_registry.return_value.get_components_by_category.assert_called_once_with(
                "Core Components"
            )

    @pytest.mark.asyncio
    async def test_debug_github_access(self, service):
        """Test debug GitHub access method."""
        with (
            patch.object(service, "_get_raw_file_content") as mock_get_content,
            patch.object(service, "_discover_components") as mock_discover,
        ):

            mock_get_content.return_value = "README content"
            mock_discover.return_value = ["address", "wallet"]

            debug_info = await service.debug_github_access()

            assert "raw_base_url" in debug_info
            assert "test_results" in debug_info
            assert debug_info["test_results"]["readme_access"]["success"] is True
            assert (
                debug_info["test_results"]["component_discovery"]["components_found"]
                == 2
            )

    @pytest.mark.asyncio
    async def test_clear_cache(self, service):
        """Test cache clearing."""
        # Add something to cache first
        service.cache.set("test_key", "test_value")
        assert service.cache.get("test_key") == "test_value"

        # Clear cache
        await service.clear_cache()

        # Verify cache is cleared
        assert service.cache.get("test_key") is None

    def test_generate_example_code(self, service):
        """Test generating example code."""
        code = service._generate_example_code("test-component")

        # The actual implementation capitalizes the first letter and removes hyphens
        assert "Testcomponent" in code or "TestComponent" in code
        assert "import" in code
        assert "export default" in code

    def test_extract_example_description(self, service):
        """Test extracting description from example content."""
        content_with_comments = """
// This is a test component
// It demonstrates basic usage
import React from 'react';

export default function Test() {
  return <div>Test</div>;
}
"""

        description = service._extract_example_description(content_with_comments)
        assert "test component" in description.lower()
        assert "demonstrates basic usage" in description.lower()

    @pytest.mark.asyncio
    async def test_caching_behavior(self, service):
        """Test that caching works correctly."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "cached content"

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            # First call should hit the network
            content1 = await service._get_raw_file_content("test/path.tsx")
            assert content1 == "cached content"

            # Second call should use cache (no network call)
            content2 = await service._get_raw_file_content("test/path.tsx")
            assert content2 == "cached content"

            # Should only have made one network call
            assert mock_client.return_value.__aenter__.return_value.get.call_count == 1
