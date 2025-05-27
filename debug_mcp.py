#!/usr/bin/env python3
"""Debug script to test MCP server directly."""

import asyncio
import json
from src.composer_kit_mcp.server import call_tool
from src.composer_kit_mcp.components import ComponentService


async def debug_mcp_server():
    """Debug the MCP server tools."""
    print("🔧 Debugging MCP Server Tools")

    # Test the component service directly first
    print("\n📊 Testing ComponentService directly...")
    service = ComponentService()
    components = await service.list_components()
    print(f"Direct service call: {len(components)} components found")

    if components:
        print("Components from direct call:")
        for comp in components[:3]:
            print(f"  • {comp.name} ({comp.category})")

    # Test the MCP server tools
    print("\n🔧 Testing MCP server tools...")

    # Test list_components
    try:
        result = await call_tool("list_components", {})
        print("MCP list_components result:")
        if result and len(result) > 0:
            content = json.loads(result[0].text)
            print(f"  Total components: {content.get('total_components', 0)}")
            print(f"  Categories: {list(content.get('categories', {}).keys())}")
        else:
            print("  No result returned")
    except Exception as e:
        print(f"  Error: {e}")

    # Test debug_github_access
    try:
        result = await call_tool("debug_github_access", {})
        print("\nMCP debug_github_access result:")
        if result and len(result) > 0:
            content = json.loads(result[0].text)
            print(
                f"  Components found: {content.get('test_results', {}).get('component_discovery', {}).get('components_found', 0)}"
            )
        else:
            print("  No result returned")
    except Exception as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_mcp_server())
