"""Main MCP server for Composer Kit UI components documentation."""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .components.data import (
    CATEGORIES,
    COMPONENTS,
    INSTALLATION_GUIDES,
)
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


def filter_unsupported_props(component: Component) -> Component:
    """Filter out unsupported props like className if the component doesn't support them."""
    if not component.supports_className:
        # Create a new component with filtered props
        filtered_props = [prop for prop in component.props if prop.name != "className"]
        # Create a copy of the component with filtered props
        component_dict = component.model_dump()
        component_dict["props"] = [prop.model_dump() for prop in filtered_props]
        return Component(**component_dict)
    return component


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
        # Celo Composer Tool
        Tool(
            name="get_celo_composer_cli_info",
            description=(
                "Get detailed information on the Celo Composer CLI `create` command, including all available flags "
                "like `--description`, `--wallet-provider`, and `--contracts`. Provides documentation, options, and "
                "usage examples to help construct `create` commands."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_components":
            # Filter all components to remove unsupported props
            filtered_components = [filter_unsupported_props(comp) for comp in COMPONENTS]

            response = ComponentsResponse(
                components=filtered_components,
                categories=CATEGORIES,
                total_count=len(filtered_components),
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

            # Filter out unsupported props like className
            filtered_component = filter_unsupported_props(component)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(filtered_component.model_dump(), indent=2),
                )
            ]

        elif name == "get_component_example":
            component_name = arguments["component_name"]
            component = get_component_by_name(component_name)

            if not component:
                return [
                    TextContent(
                        type="text",
                        text=f"Component '{component_name}' not found.",
                    )
                ]

            example_type = arguments.get("example_type", "basic")
            example = next((ex for ex in component.examples if ex.type == example_type), None)

            if not example:
                return [
                    TextContent(
                        type="text",
                        text=f"Example type '{example_type}' not found for component '{component_name}'.",
                    )
                ]

            return [TextContent(type="text", text=json.dumps(example.model_dump(), indent=2))]

        elif name == "search_components":
            query = arguments["query"]
            search_results = search_components(query)
            # Limit to top 5 results to avoid excessive output
            top_results = search_results[:5]
            return [
                TextContent(
                    type="text",
                    text=json.dumps([r.model_dump() for r in top_results], indent=2),
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
                    text=json.dumps([p.model_dump() for p in component.props], indent=2),
                )
            ]

        elif name == "get_installation_guide":
            package_manager = arguments.get("package_manager", "npm")
            guide = INSTALLATION_GUIDES.get(package_manager)
            if not guide:
                return [
                    TextContent(
                        type="text",
                        text=f"Installation guide for '{package_manager}' not found.",
                    )
                ]
            return [TextContent(type="text", text=json.dumps(guide, indent=2))]

        elif name == "get_components_by_category":
            category = arguments["category"]
            components_in_category = get_components_by_category(category)
            return [
                TextContent(
                    type="text",
                    text=json.dumps([c.model_dump() for c in components_in_category], indent=2),
                )
            ]

        # Celo Composer Tool
        elif name == "get_celo_composer_cli_info":
            cli_info = {
                "command_name": "celo-composer create",
                "base_command": "npx @celo/celo-composer@latest create",
                "description": "Create a new Celo project from the command line.",
                "arguments": [
                    {
                        "name": "project-name",
                        "description": "The name of the project to be created.",
                        "is_required": True,
                    }
                ],
                "options": [
                    {
                        "name": "--description",
                        "alias": "-d",
                        "description": "A description for your project.",
                        "type": "string",
                        "is_required": True,
                    },
                    {
                        "name": "--wallet-provider",
                        "description": "The wallet provider to use.",
                        "type": "string",
                        "is_required": True,
                        "allowed_values": ["rainbowkit", "thirdweb", "none"],
                    },
                    {
                        "name": "--contracts",
                        "alias": "-c",
                        "description": "The smart contract framework to include.",
                        "type": "string",
                        "is_required": True,
                        "allowed_values": ["hardhat", "none"],
                    },
                    {
                        "name": "--skip-install",
                        "description": "Skip the automatic installation of package dependencies.",
                        "type": "boolean",
                    },
                    {
                        "name": "--yes",
                        "alias": "-y",
                        "description": """
                        Skip all prompts and use default settings. Never add this flag if you want to 
                        have specific values for any of the flags.
                        """,
                        "type": "boolean",
                    },
                ],
                "examples": [
                    {
                        "description": "Create a basic project with prompts for all options:",
                        "command": "npx @celo/celo-composer@latest create my-celo-app",
                    },
                    {
                        "description": "Create a project with a specific wallet provider (Thirdweb) and skip prompts:",
                        "command": "npx @celo/celo-composer@latest create my-dapp --wallet-provider thirdweb -y",
                    },
                    {
                        "description": ("Create a project with Hardhat contracts and skip dependency installation:"),
                        "command": (
                            "npx @celo/celo-composer@latest create full-stack-dapp --contracts hardhat --skip-install"
                        ),
                    },
                ],
            }
            return [
                TextContent(
                    type="text",
                    text=json.dumps(cli_info, indent=2),
                )
            ]
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error calling tool '{name}': {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


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
