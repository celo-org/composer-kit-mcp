#!/usr/bin/env python3
"""
Basic usage example for the Composer Kit MCP Server.

This script demonstrates how to interact with the MCP server programmatically.
In practice, you would typically use this server with an MCP client like Claude Desktop.
"""

import asyncio
import json
from composer_kit_mcp.components import ComponentService


async def main():
    """Demonstrate basic usage of the ComponentService."""
    print("🚀 Composer Kit MCP Server - Basic Usage Example")
    print("=" * 50)

    # Initialize the service
    service = ComponentService()

    try:
        # List all available components
        print("\n📦 Listing all available components...")
        components = await service.list_components()
        print(f"Found {len(components)} components:")

        for component in components[:5]:  # Show first 5
            print(f"  • {component.display_name} ({component.category})")
            print(f"    {component.description}")

        if len(components) > 5:
            print(f"  ... and {len(components) - 5} more components")

        # Search for wallet-related components
        print("\n🔍 Searching for 'wallet' components...")
        wallet_components = await service.search_components("wallet")
        print(f"Found {len(wallet_components)} wallet-related components:")

        for component in wallet_components:
            print(f"  • {component.display_name}")
            print(f"    Category: {component.category}")
            print(f"    Description: {component.description}")

        # Get detailed information about a specific component
        if wallet_components:
            component_name = wallet_components[0].name
            print(f"\n🔧 Getting detailed info for '{component_name}' component...")

            component = await service.get_component(component_name)
            if component:
                print(f"Component: {component.display_name}")
                print(f"Category: {component.category}")
                print(f"Description: {component.description}")
                print(f"Props: {len(component.props)} defined")
                print(f"Examples: {len(component.examples)} available")

                if component.source_code:
                    print(f"Source code: {len(component.source_code)} characters")
                    # Show first few lines of source code
                    lines = component.source_code.split("\n")[:5]
                    print("First few lines:")
                    for line in lines:
                        print(f"    {line}")
                    if len(component.source_code.split("\n")) > 5:
                        print("    ...")

                # Show props if available
                if component.props:
                    print(f"\nProps for {component.display_name}:")
                    for prop in component.props[:3]:  # Show first 3 props
                        required = "required" if prop.required else "optional"
                        print(f"  • {prop.name}: {prop.type} ({required})")
                        if prop.description:
                            print(f"    {prop.description}")

                    if len(component.props) > 3:
                        print(f"    ... and {len(component.props) - 3} more props")

                # Show examples if available
                if component.examples:
                    print(f"\nExamples for {component.display_name}:")
                    for example in component.examples[:2]:  # Show first 2 examples
                        print(f"  • {example.name}")
                        print(f"    {example.description}")
                        print(f"    File: {example.file_path}")

        # Get components by category
        print("\n📂 Getting components by category...")
        categories = ["Core Components", "Wallet Integration", "Payment & Transactions"]

        for category in categories:
            category_components = await service.get_components_by_category(category)
            if category_components:
                print(f"\n{category} ({len(category_components)} components):")
                for component in category_components:
                    print(f"  • {component.display_name}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have internet access and the GitHub API is reachable.")

    print("\n✅ Example completed!")
    print("\nTo use this MCP server with Claude Desktop or other MCP clients,")
    print("run: python -m composer_kit_mcp.server")


if __name__ == "__main__":
    asyncio.run(main())
