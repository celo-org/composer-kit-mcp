"""Main MCP server for Composer Kit UI components documentation."""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .components.data import CATEGORIES, COMPONENTS, INSTALLATION_GUIDES
from .components.models import (
    Component,
    ComponentSearchResult,
    ComponentsResponse,
)

logger = logging.getLogger(__name__)

# Initialize server
server: Server = Server("composer-kit-mcp")


def search_components(query: str) -> list[ComponentSearchResult]:
    """Search components by name, description, or functionality."""
    results = []
    query_lower = query.lower()

    for component in COMPONENTS:
        relevance_score = 0.0
        matching_fields = []

        # Check name match
        if query_lower in component.name.lower():
            relevance_score += 1.0
            matching_fields.append("name")

        # Check description match
        if query_lower in component.description.lower():
            relevance_score += 0.8
            matching_fields.append("description")

        # Check detailed description match
        if component.detailed_description and query_lower in component.detailed_description.lower():
            relevance_score += 0.6
            matching_fields.append("detailed_description")

        # Check category match
        if query_lower in component.category.lower():
            relevance_score += 0.5
            matching_fields.append("category")

        # Check subcomponents match
        for subcomp in component.subcomponents:
            if query_lower in subcomp.lower():
                relevance_score += 0.4
                matching_fields.append("subcomponents")
                break

        # Check props match
        for prop in component.props:
            if query_lower in prop.name.lower() or query_lower in prop.description.lower():
                relevance_score += 0.3
                matching_fields.append("props")
                break

        if relevance_score > 0:
            results.append(
                ComponentSearchResult(
                    component=component,
                    relevance_score=relevance_score,
                    matching_fields=matching_fields,
                )
            )

    # Sort by relevance score (descending)
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results


def get_component_by_name(name: str) -> Component | None:
    """Get a component by its name (case-insensitive)."""
    name_lower = name.lower()
    for component in COMPONENTS:
        if component.name.lower() == name_lower:
            return component
    return None


def get_components_by_category(category: str) -> list[Component]:
    """Get all components in a specific category."""
    return [comp for comp in COMPONENTS if comp.category.lower() == category.lower()]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_components",
            description=(
                "List all available Composer Kit components with their descriptions "
                "and categories. Returns a comprehensive overview of the component library."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_component",
            description=(
                "Get detailed information about a specific Composer Kit component, "
                "including source code, props, and usage information."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": (
                            "The name of the component to retrieve " "(e.g., 'button', 'wallet', 'payment', 'swap')"
                        ),
                    }
                },
                "required": ["component_name"],
            },
        ),
        Tool(
            name="get_component_example",
            description=(
                "Get example usage code for a specific Composer Kit component. "
                "Returns real-world examples from the documentation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": "The name of the component to get examples for",
                    },
                    "example_type": {
                        "type": "string",
                        "description": (
                            "Optional: specific type of example " "(e.g., 'basic', 'advanced', 'with-props')"
                        ),
                    },
                },
                "required": ["component_name"],
            },
        ),
        Tool(
            name="search_components",
            description=(
                "Search for Composer Kit components by name, description, or functionality. "
                "Useful for finding components that match specific needs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": ("Search query (e.g., 'wallet', 'payment', 'token', 'nft')"),
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_component_props",
            description=(
                "Get detailed prop information for a specific component, including "
                "types, descriptions, and whether props are required or optional."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": "The name of the component to get props for",
                    }
                },
                "required": ["component_name"],
            },
        ),
        Tool(
            name="get_installation_guide",
            description=(
                "Get installation instructions for Composer Kit, including setup steps "
                "and configuration for different package managers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "package_manager": {
                        "type": "string",
                        "enum": ["npm", "yarn", "pnpm", "bun"],
                        "description": (
                            "Package manager to use (npm, yarn, pnpm, bun). " "Defaults to npm if not specified."
                        ),
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_components_by_category",
            description=(
                "Get all components in a specific category "
                "(e.g., 'Wallet Integration', 'Payment & Transactions', 'Core Components', 'NFT Components')."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": (
                            "The category name (e.g., 'Core Components', 'Wallet Integration', "
                            "'Payment & Transactions', 'Token Management', 'NFT Components')"
                        ),
                    }
                },
                "required": ["category"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_components":
            response = ComponentsResponse(
                components=COMPONENTS,
                categories=CATEGORIES,
                total_count=len(COMPONENTS),
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(response.model_dump(), indent=2),
                )
            ]

        elif name == "get_component":
            component_name = arguments["component_name"]
            component = get_component_by_name(component_name)

            if not component:
                return [
                    TextContent(
                        type="text",
                        text=f"Component '{component_name}' not found. Available components: {', '.join([c.name for c in COMPONENTS])}",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps(component.model_dump(), indent=2),
                )
            ]

        elif name == "get_component_example":
            component_name = arguments["component_name"]
            example_type = arguments.get("example_type")

            component = get_component_by_name(component_name)
            if not component:
                return [
                    TextContent(
                        type="text",
                        text=f"Component '{component_name}' not found.",
                    )
                ]

            examples = component.examples
            if example_type:
                examples = [ex for ex in examples if ex.example_type == example_type]

            if not examples:
                return [
                    TextContent(
                        type="text",
                        text=f"No examples found for component '{component_name}'"
                        + (f" with type '{example_type}'" if example_type else ""),
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps([ex.model_dump() for ex in examples], indent=2),
                )
            ]

        elif name == "search_components":
            query = arguments["query"]
            results = search_components(query)

            if not results:
                return [
                    TextContent(
                        type="text",
                        text=f"No components found matching query: '{query}'",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps([result.model_dump() for result in results], indent=2),
                )
            ]

        elif name == "get_component_props":
            component_name = arguments["component_name"]
            component = get_component_by_name(component_name)

            if not component:
                return [
                    TextContent(
                        type="text",
                        text=f"Component '{component_name}' not found.",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps([prop.model_dump() for prop in component.props], indent=2),
                )
            ]

        elif name == "get_installation_guide":
            package_manager = arguments.get("package_manager", "npm")

            if package_manager not in INSTALLATION_GUIDES:
                return [
                    TextContent(
                        type="text",
                        text=f"Package manager '{package_manager}' not supported. Available: {', '.join(INSTALLATION_GUIDES.keys())}",
                    )
                ]

            guide = INSTALLATION_GUIDES[package_manager]
            return [
                TextContent(
                    type="text",
                    text=json.dumps(guide.model_dump(), indent=2),
                )
            ]

        elif name == "get_components_by_category":
            category = arguments["category"]
            components = get_components_by_category(category)

            if not components:
                return [
                    TextContent(
                        type="text",
                        text=f"No components found in category '{category}'. Available categories: {', '.join(CATEGORIES)}",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps([comp.model_dump() for comp in components], indent=2),
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main() -> None:
    """Main server function."""
    logger.info("Starting Composer Kit MCP Server")
    logger.info(f"Available components: {len(COMPONENTS)}")
    logger.info(f"Available categories: {', '.join(CATEGORIES)}")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main_sync() -> None:
    """Synchronous main function for CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
