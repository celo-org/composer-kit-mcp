"""Tests for the component service."""

import pytest
from unittest.mock import AsyncMock, patch

from composer_kit_mcp.components import ComponentService, Component, ComponentRegistry


@pytest.fixture
def component_service():
    """Create a component service instance for testing."""
    return ComponentService()


@pytest.mark.asyncio
async def test_component_service_initialization(component_service):
    """Test that component service initializes correctly."""
    assert component_service.repo_owner == "celo-org"
    assert component_service.repo_name == "composer-kit"
    assert component_service.main_branch == "main"
    assert component_service.cache is not None


@pytest.mark.asyncio
async def test_get_component_category(component_service):
    """Test component category mapping."""
    assert component_service._get_component_category("wallet") == "Wallet Integration"
    assert (
        component_service._get_component_category("payment") == "Payment & Transactions"
    )
    assert component_service._get_component_category("address") == "Core Components"
    assert component_service._get_component_category("unknown") == "Other"


@pytest.mark.asyncio
async def test_normalize_component_name():
    """Test component name normalization."""
    from composer_kit_mcp.utils import normalize_component_name

    assert normalize_component_name("wallet") == "wallet"
    assert normalize_component_name("token-select") == "tokenSelect"
    assert normalize_component_name("composer-kit-button") == "button"
    assert normalize_component_name("PAYMENT") == "payment"


@pytest.mark.asyncio
async def test_component_registry_search():
    """Test component registry search functionality."""
    registry = ComponentRegistry()

    # Add test components
    component1 = Component(
        name="wallet",
        display_name="Wallet",
        description="Wallet connection component",
        category="Wallet Integration",
    )
    component2 = Component(
        name="payment",
        display_name="Payment",
        description="Payment processing component",
        category="Payment & Transactions",
    )

    registry.components["wallet"] = component1
    registry.components["payment"] = component2

    # Test search
    results = registry.search_components("wallet")
    assert len(results) == 1
    assert results[0].name == "wallet"

    results = registry.search_components("payment")
    assert len(results) == 1
    assert results[0].name == "payment"

    results = registry.search_components("component")
    assert len(results) == 2  # Both have "component" in description


@pytest.mark.asyncio
async def test_component_registry_get_by_category():
    """Test getting components by category."""
    registry = ComponentRegistry()

    # Add test components
    component1 = Component(
        name="wallet",
        display_name="Wallet",
        description="Wallet connection component",
        category="Wallet Integration",
    )
    component2 = Component(
        name="connect",
        display_name="Connect",
        description="Connect button component",
        category="Wallet Integration",
    )
    component3 = Component(
        name="payment",
        display_name="Payment",
        description="Payment processing component",
        category="Payment & Transactions",
    )

    registry.components["wallet"] = component1
    registry.components["connect"] = component2
    registry.components["payment"] = component3

    # Test category filtering
    wallet_components = registry.get_components_by_category("Wallet Integration")
    assert len(wallet_components) == 2
    assert all(c.category == "Wallet Integration" for c in wallet_components)

    payment_components = registry.get_components_by_category("Payment & Transactions")
    assert len(payment_components) == 1
    assert payment_components[0].name == "payment"


@pytest.mark.asyncio
@patch("composer_kit_mcp.components.service.httpx.AsyncClient")
async def test_github_api_request(mock_client, component_service):
    """Test GitHub raw file content fetching."""
    # Mock the response
    mock_response = AsyncMock()
    mock_response.text = "test file content"
    mock_response.status_code = 200

    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # Test the request using the actual method
    result = await component_service._get_raw_file_content("test/path.tsx")

    assert result == "test file content"
    mock_client_instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_cache_functionality(component_service):
    """Test cache functionality."""
    cache = component_service.cache

    # Test setting and getting
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

    # Test non-existent key
    assert cache.get("non_existent") is None

    # Test cache clear
    cache.clear()
    assert cache.get("test_key") is None


@pytest.mark.asyncio
async def test_extract_example_description(component_service):
    """Test example description extraction."""
    content = """
// This is a basic wallet example
// Shows how to connect a wallet
import { Wallet } from "@composer-kit/ui";

export const WalletBasic = () => {
    return <Wallet />;
};
"""

    description = component_service._extract_example_description(content)
    assert "basic wallet example" in description.lower()
    assert "connect a wallet" in description.lower()


if __name__ == "__main__":
    pytest.main([__file__])
