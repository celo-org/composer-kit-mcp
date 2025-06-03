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
    CELO_COMPOSER_TEMPLATES,
    CELO_COMPOSER_FRAMEWORKS,
    CELO_COMPOSER_COMMANDS,
    CELO_COMPOSER_GUIDES,
    CELO_COMPOSER_INTEGRATION_GUIDE,
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
        # Celo Composer Tools
        Tool(
            name="list_celo_composer_templates",
            description=(
                "List all available Celo Composer templates with their descriptions, "
                "use cases, and features. Templates provide different starting points for dApp development."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_celo_composer_template",
            description=(
                "Get detailed information about a specific Celo Composer template, "
                "including use cases, features, and documentation links."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "The name of the template (e.g., 'Minipay', 'Valora', 'Social Connect')",
                    }
                },
                "required": ["template_name"],
            },
        ),
        Tool(
            name="list_celo_composer_frameworks",
            description=(
                "List supported frameworks in Celo Composer, including React/Next.js and Hardhat "
                "with their descriptions and documentation links."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_celo_composer_commands",
            description=(
                "Get available Celo Composer CLI commands with their descriptions, "
                "flags, and usage examples for creating projects."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_celo_composer_guide",
            description=(
                "Get step-by-step guides for various Celo Composer tasks such as "
                "project creation, deployment, and development setup."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "guide_type": {
                        "type": "string",
                        "enum": [
                            "quick-start",
                            "smart-contract-deployment",
                            "local-development",
                            "ui-components",
                            "deployment",
                        ],
                        "description": (
                            "Type of guide to retrieve: 'quick-start' for getting started, "
                            "'smart-contract-deployment' for deploying contracts, 'local-development' for dev setup, "
                            "'ui-components' for adding UI components, 'deployment' for Vercel deployment"
                        ),
                    }
                },
                "required": ["guide_type"],
            },
        ),
        Tool(
            name="get_integration_guide",
            description=(
                "Get a comprehensive guide on how to integrate Composer Kit components "
                "with Celo Composer projects for rapid dApp development."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="create_celo_composer_project",
            description=(
                "Generate the complete command to create a new Celo Composer project "
                "with specified configuration. Returns the CLI command to execute."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project (will be converted to kebab-case)",
                    },
                    "owner": {
                        "type": "string",
                        "description": "Project owner name",
                    },
                    "include_hardhat": {
                        "type": "boolean",
                        "description": "Whether to include Hardhat in the project",
                        "default": True,
                    },
                    "template": {
                        "type": "string",
                        "enum": ["Minipay", "Valora", "Social Connect"],
                        "description": "Template to use for the project",
                    },
                },
                "required": ["project_name", "owner", "template"],
            },
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

            # Filter components in search results to remove unsupported props
            filtered_results = []
            for result in results:
                filtered_component = filter_unsupported_props(result.component)
                result_dict = result.model_dump()
                result_dict["component"] = filtered_component.model_dump()
                filtered_results.append(result_dict)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(filtered_results, indent=2),
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

            # Filter out unsupported props like className
            filtered_component = filter_unsupported_props(component)

            return [
                TextContent(
                    type="text",
                    text=json.dumps([prop.model_dump() for prop in filtered_component.props], indent=2),
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

            # Filter components to remove unsupported props
            filtered_components = [filter_unsupported_props(comp) for comp in components]

            return [
                TextContent(
                    type="text",
                    text=json.dumps([comp.model_dump() for comp in filtered_components], indent=2),
                )
            ]

        # Celo Composer tool handlers
        elif name == "list_celo_composer_templates":
            return [
                TextContent(
                    type="text",
                    text=json.dumps([t.model_dump() for t in CELO_COMPOSER_TEMPLATES], indent=2),
                )
            ]

        elif name == "get_celo_composer_template":
            template_name = arguments["template_name"]
            template = next((t for t in CELO_COMPOSER_TEMPLATES if t.name == template_name), None)

            if not template:
                available_templates = ", ".join([t.name for t in CELO_COMPOSER_TEMPLATES])
                return [
                    TextContent(
                        type="text",
                        text=f"Template '{template_name}' not found. Available templates: {available_templates}",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps(template.model_dump(), indent=2),
                )
            ]

        elif name == "list_celo_composer_frameworks":
            return [
                TextContent(
                    type="text",
                    text=json.dumps([f.model_dump() for f in CELO_COMPOSER_FRAMEWORKS], indent=2),
                )
            ]

        elif name == "get_celo_composer_commands":
            return [
                TextContent(
                    type="text",
                    text=json.dumps([c.model_dump() for c in CELO_COMPOSER_COMMANDS], indent=2),
                )
            ]

        elif name == "get_celo_composer_guide":
            guide_type = arguments["guide_type"]

            # Map guide types to actual guide titles
            guide_map = {
                "quick-start": "Quick Start Guide",
                "smart-contract-deployment": "Smart Contract Deployment",
                "local-development": "Local Development Setup",
                "ui-components": "Adding UI Components",
                "deployment": "Deployment with Vercel",
            }

            guide_title = guide_map.get(guide_type)
            if not guide_title:
                return [
                    TextContent(
                        type="text",
                        text=f"Guide type '{guide_type}' not found. Available types: {', '.join(guide_map.keys())}",
                    )
                ]

            guide = next((g for g in CELO_COMPOSER_GUIDES if g.title == guide_title), None)

            if not guide:
                return [
                    TextContent(
                        type="text",
                        text=f"Guide '{guide_type}' not found.",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps(guide.model_dump(), indent=2),
                )
            ]

        elif name == "get_integration_guide":
            return [
                TextContent(
                    type="text",
                    text=json.dumps(CELO_COMPOSER_INTEGRATION_GUIDE.model_dump(), indent=2),
                )
            ]

        elif name == "create_celo_composer_project":
            project_name = arguments["project_name"]
            owner = arguments["owner"]
            include_hardhat = arguments.get("include_hardhat", True)
            template = arguments["template"]

            # Validate template exists
            template_obj = next((t for t in CELO_COMPOSER_TEMPLATES if t.name == template), None)
            if not template_obj:
                available_templates = ", ".join([t.name for t in CELO_COMPOSER_TEMPLATES])
                return [
                    TextContent(
                        type="text",
                        text=f"Template '{template}' not found. Available templates: {available_templates}",
                    )
                ]

            # Build the command
            command = f'npx @celo/celo-composer@latest create --name "{project_name}" --owner "{owner}" --template "{template}"'

            if include_hardhat:
                command += " --hardhat"
            else:
                command += " --no-hardhat"

            response = {
                "command": command,
                "description": f"Create a new Celo Composer project with {template} template",
                "next_steps": [f"cd {project_name}", "yarn install", "yarn dev"],
                "template_info": template_obj.model_dump(),
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(response, indent=2),
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
