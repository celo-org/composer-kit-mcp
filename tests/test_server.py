"""Tests for the Composer Kit MCP server."""

import pytest
from composer_kit_mcp.components.data import COMPONENTS, CATEGORIES
from composer_kit_mcp.server import (
    search_components,
    get_component_by_name,
    get_components_by_category,
)


def test_components_data():
    """Test that component data is properly loaded."""
    assert len(COMPONENTS) > 0
    assert len(CATEGORIES) > 0

    # Check that all components have required fields
    for component in COMPONENTS:
        assert component.name
        assert component.category
        assert component.description
        assert component.import_path


def test_get_component_by_name():
    """Test getting a component by name."""
    # Test existing component
    component = get_component_by_name("Address")
    assert component is not None
    assert component.name == "Address"

    # Test case insensitive
    component = get_component_by_name("address")
    assert component is not None
    assert component.name == "Address"

    # Test non-existing component
    component = get_component_by_name("NonExistentComponent")
    assert component is None


def test_get_components_by_category():
    """Test getting components by category."""
    # Test existing category
    components = get_components_by_category("Core Components")
    assert len(components) > 0

    for component in components:
        assert component.category == "Core Components"

    # Test case insensitive
    components = get_components_by_category("core components")
    assert len(components) > 0

    # Test non-existing category
    components = get_components_by_category("NonExistentCategory")
    assert len(components) == 0


def test_search_components():
    """Test component search functionality."""
    # Test search by name
    results = search_components("Address")
    assert len(results) > 0
    assert results[0].component.name == "Address"

    # Test search by description
    results = search_components("wallet")
    assert len(results) > 0

    # Test search with no results
    results = search_components("nonexistentterm")
    assert len(results) == 0

    # Test search relevance scoring
    results = search_components("payment")
    assert len(results) > 0
    # Results should be sorted by relevance
    for i in range(len(results) - 1):
        assert results[i].relevance_score >= results[i + 1].relevance_score


def test_categories():
    """Test that all categories are valid."""
    expected_categories = [
        "Core Components",
        "Wallet Integration",
        "Payment & Transactions",
        "Token Management",
        "NFT Components",
    ]

    assert set(CATEGORIES) == set(expected_categories)


def test_component_props():
    """Test that components have proper props structure."""
    address_component = get_component_by_name("Address")
    assert address_component is not None

    # Check that Address component has required props
    prop_names = [prop.name for prop in address_component.props]
    assert "address" in prop_names

    # Check that required prop is marked as required
    address_prop = next(
        prop for prop in address_component.props if prop.name == "address"
    )
    assert address_prop.required is True


def test_component_examples():
    """Test that components have examples."""
    for component in COMPONENTS:
        if component.examples:
            for example in component.examples:
                assert example.title
                assert example.description
                assert example.code
                assert example.example_type
