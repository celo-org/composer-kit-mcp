"""Main MCP server for Composer Kit component access."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .components import ComponentService
from .utils import setup_logging

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# Initialize server
server = Server("composer-kit-mcp")

# Global service instances
component_service: ComponentService = None


@server.list_tools()
async def list_tools() -> List[Tool]:
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
                            "The name of the component to retrieve (e.g., 'button', "
                            "'wallet', 'payment', 'swap')"
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
                        "description": (
                            "The name of the component to get examples for"
                        ),
                    },
                    "example_type": {
                        "type": "string",
                        "description": (
                            "Optional: specific type of example (e.g., 'basic', "
                            "'advanced', 'with-props')"
                        ),
                    },
                },
                "required": ["component_name"],
            },
        ),
        Tool(
            name="search_components",
            description=(
                "Search for Composer Kit components by name, description, or "
                "functionality. Useful for finding components that match specific needs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Search query (e.g., 'wallet', 'payment', 'token', 'nft')"
                        ),
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
                "Get installation instructions for Composer Kit, including setup "
                "steps and configuration for different package managers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "package_manager": {
                        "type": "string",
                        "description": (
                            "Package manager to use (npm, yarn, pnpm, bun). "
                            "Defaults to npm if not specified."
                        ),
                        "enum": ["npm", "yarn", "pnpm", "bun"],
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_components_by_category",
            description=(
                "Get all components in a specific category (e.g., 'Wallet Integration', "
                "'Payment & Transactions', 'Core Components', 'NFT Components')."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": (
                            "The category name (e.g., 'Core Components', "
                            "'Wallet Integration', 'Payment & Transactions', "
                            "'Token Management', 'NFT Components')"
                        ),
                    }
                },
                "required": ["category"],
            },
        ),
        Tool(
            name="debug_github_access",
            description=(
                "Debug tool to test GitHub raw content access and component discovery. "
                "Useful for troubleshooting connection issues."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    global component_service

    if component_service is None:
        component_service = ComponentService()

    try:
        if name == "list_components":
            components = await component_service.list_components()

            # Format components for display
            result = {
                "total_components": len(components),
                "categories": {},
                "components": [],
            }

            # Group by category
            for component in components:
                if component.category not in result["categories"]:
                    result["categories"][component.category] = []
                result["categories"][component.category].append(
                    {
                        "name": component.name,
                        "display_name": component.display_name,
                        "description": component.description,
                    }
                )

                result["components"].append(
                    {
                        "name": component.name,
                        "display_name": component.display_name,
                        "description": component.description,
                        "category": component.category,
                        "has_examples": len(component.examples) > 0,
                        "props_count": len(component.props),
                    }
                )

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder)
                )
            ]

        elif name == "get_component":
            component_name = arguments.get("component_name")
            if not component_name:
                return [
                    TextContent(type="text", text="Error: component_name is required")
                ]

            component = await component_service.get_component(component_name)
            if not component:
                return [
                    TextContent(
                        type="text",
                        text=f"Component '{component_name}' not found. Use 'list_components' to see available components.",
                    )
                ]

            result = {
                "component": {
                    "name": component.name,
                    "display_name": component.display_name,
                    "description": component.description,
                    "category": component.category,
                    "installation_command": component.installation_command,
                    "documentation_url": component.documentation_url,
                    "dependencies": component.dependencies,
                    "props_count": len(component.props),
                    "examples_count": len(component.examples),
                },
                "source_code": component.source_code,
                "props": [
                    {
                        "name": prop.name,
                        "type": prop.type,
                        "description": prop.description,
                        "required": prop.required,
                        "default": prop.default,
                    }
                    for prop in component.props
                ],
                "examples": [
                    {
                        "name": example.name,
                        "description": example.description,
                        "file_path": example.file_path,
                    }
                    for example in component.examples
                ],
            }

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder)
                )
            ]

        elif name == "get_component_example":
            component_name = arguments.get("component_name")
            example_type = arguments.get("example_type")

            if not component_name:
                return [
                    TextContent(type="text", text="Error: component_name is required")
                ]

            component = await component_service.get_component(component_name)
            if not component:
                return [
                    TextContent(
                        type="text", text=f"Component '{component_name}' not found."
                    )
                ]

            if not component.examples:
                return [
                    TextContent(
                        type="text",
                        text=f"No examples found for component '{component_name}'.",
                    )
                ]

            # Filter examples by type if specified
            examples = component.examples
            if example_type:
                examples = [
                    ex
                    for ex in examples
                    if example_type.lower() in ex.name.lower()
                    or example_type.lower() in ex.description.lower()
                ]

            if not examples:
                return [
                    TextContent(
                        type="text",
                        text=f"No examples found for component '{component_name}' with type '{example_type}'.",
                    )
                ]

            result = {
                "component_name": component_name,
                "examples": [
                    {
                        "name": example.name,
                        "description": example.description,
                        "code": example.code,
                        "file_path": example.file_path,
                    }
                    for example in examples
                ],
            }

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder)
                )
            ]

        elif name == "search_components":
            query = arguments.get("query")
            if not query:
                return [TextContent(type="text", text="Error: query is required")]

            components = await component_service.search_components(query)

            result = {
                "query": query,
                "total_results": len(components),
                "components": [
                    {
                        "name": component.name,
                        "display_name": component.display_name,
                        "description": component.description,
                        "category": component.category,
                        "has_examples": len(component.examples) > 0,
                        "props_count": len(component.props),
                    }
                    for component in components
                ],
            }

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder)
                )
            ]

        elif name == "get_component_props":
            component_name = arguments.get("component_name")
            if not component_name:
                return [
                    TextContent(type="text", text="Error: component_name is required")
                ]

            component = await component_service.get_component(component_name)
            if not component:
                return [
                    TextContent(
                        type="text", text=f"Component '{component_name}' not found."
                    )
                ]

            result = {
                "component_name": component.name,
                "display_name": component.display_name,
                "total_props": len(component.props),
                "props": [
                    {
                        "name": prop.name,
                        "type": prop.type,
                        "description": prop.description or "No description available",
                        "required": prop.required,
                        "default": prop.default,
                    }
                    for prop in component.props
                ],
            }

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder)
                )
            ]

        elif name == "get_installation_guide":
            package_manager = arguments.get("package_manager", "npm")

            installation_guides = {
                "npm": {
                    "install_command": "npm install @composer-kit/ui",
                    "dev_dependencies": "npm install -D @types/react @types/react-dom",
                    "setup_steps": [
                        "Install the package: npm install @composer-kit/ui",
                        "Install peer dependencies if needed: npm install react react-dom",
                        "Import components in your React app",
                        "Wrap your app with ComposerKitProvider",
                    ],
                },
                "yarn": {
                    "install_command": "yarn add @composer-kit/ui",
                    "dev_dependencies": "yarn add -D @types/react @types/react-dom",
                    "setup_steps": [
                        "Install the package: yarn add @composer-kit/ui",
                        "Install peer dependencies if needed: yarn add react react-dom",
                        "Import components in your React app",
                        "Wrap your app with ComposerKitProvider",
                    ],
                },
                "pnpm": {
                    "install_command": "pnpm add @composer-kit/ui",
                    "dev_dependencies": "pnpm add -D @types/react @types/react-dom",
                    "setup_steps": [
                        "Install the package: pnpm add @composer-kit/ui",
                        "Install peer dependencies if needed: pnpm add react react-dom",
                        "Import components in your React app",
                        "Wrap your app with ComposerKitProvider",
                    ],
                },
                "bun": {
                    "install_command": "bun add @composer-kit/ui",
                    "dev_dependencies": "bun add -D @types/react @types/react-dom",
                    "setup_steps": [
                        "Install the package: bun add @composer-kit/ui",
                        "Install peer dependencies if needed: bun add react react-dom",
                        "Import components in your React app",
                        "Wrap your app with ComposerKitProvider",
                    ],
                },
            }

            guide = installation_guides.get(package_manager, installation_guides["npm"])

            result = {
                "package_manager": package_manager,
                "installation_guide": guide,
                "basic_usage": {
                    "provider_setup": """
import { ComposerKitProvider } from "@composer-kit/ui";

function App() {
  return (
    <ComposerKitProvider>
      {/* Your app content */}
    </ComposerKitProvider>
  );}""",
                    "component_import": """
import { Wallet, Payment, Swap } from "@composer-kit/ui";

// Use components in your JSX
<Wallet>
  <Payment />
  <Swap />
</Wallet>""",
                },
                "documentation_url": "https://github.com/celo-org/composer-kit",
                "examples_url": "https://github.com/celo-org/composer-kit/tree/main/apps/docs/examples",
            }

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder)
                )
            ]

        elif name == "get_components_by_category":
            category = arguments.get("category")
            if not category:
                return [TextContent(type="text", text="Error: category is required")]

            components = await component_service.get_components_by_category(category)

            result = {
                "category": category,
                "total_components": len(components),
                "components": [
                    {
                        "name": component.name,
                        "display_name": component.display_name,
                        "description": component.description,
                        "has_examples": len(component.examples) > 0,
                        "props_count": len(component.props),
                        "installation_command": component.installation_command,
                    }
                    for component in components
                ],
            }

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder)
                )
            ]

        elif name == "debug_github_access":
            debug_info = await component_service.debug_github_access()

            return [
                TextContent(
                    type="text",
                    text=json.dumps(debug_info, indent=2, cls=DateTimeEncoder),
                )
            ]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]


async def main():
    """Main entry point for the server."""
    setup_logging()
    logger.info("Starting Composer Kit MCP Server")

    # Initialize services
    global component_service
    component_service = ComponentService()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


def main_sync():
    """Synchronous entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
