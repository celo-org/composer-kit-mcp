#!/usr/bin/env python3
"""Test script to verify component discovery works."""

import asyncio
import logging
from src.composer_kit_mcp.components import ComponentService

# Set up logging
logging.basicConfig(level=logging.INFO)


async def test_component_service():
    """Test the component service."""
    print("🔧 Testing Component Service with Raw GitHub Content")

    service = ComponentService()

    # Test debug access first
    print("\n📊 Testing GitHub access...")
    debug_info = await service.debug_github_access()
    print(f"Raw base URL: {debug_info['raw_base_url']}")
    print(f"Known components: {len(debug_info['known_components'])}")

    # Test README access
    readme_test = debug_info["test_results"]["readme_access"]
    print(f"README access: {'✅' if readme_test['success'] else '❌'}")
    if readme_test["success"]:
        print(f"README content length: {readme_test['content_length']} characters")
    else:
        print(f"README error: {readme_test.get('error', 'Unknown error')}")

    # Test component discovery
    discovery_test = debug_info["test_results"]["component_discovery"]
    print(f"Component discovery: {'✅' if discovery_test['success'] else '❌'}")
    if discovery_test["success"]:
        print(f"Components found: {discovery_test['components_found']}")
        print(f"Components: {discovery_test['components']}")
    else:
        print(f"Discovery error: {discovery_test.get('error', 'Unknown error')}")

    # Test listing components
    print("\n📋 Testing component listing...")
    try:
        components = await service.list_components()
        print(f"Total components: {len(components)}")

        if components:
            print("\nFirst few components:")
            for component in components[:3]:
                print(f"  • {component.name} ({component.category})")
                print(f"    Description: {component.description}")
                print(
                    f"    Props: {len(component.props)}, Examples: {len(component.examples)}"
                )
        else:
            print("No components found!")

    except Exception as e:
        print(f"Error listing components: {e}")

    # Test getting a specific component
    if components:
        print(f"\n🔍 Testing specific component: {components[0].name}")
        try:
            component = await service.get_component(components[0].name)
            if component:
                print(f"Component: {component.display_name}")
                print(
                    f"Source code length: {len(component.source_code) if component.source_code else 0} characters"
                )
                if component.source_code:
                    # Show first few lines
                    lines = component.source_code.split("\n")[:3]
                    print("First few lines of source:")
                    for line in lines:
                        print(f"    {line}")
            else:
                print("Component not found!")
        except Exception as e:
            print(f"Error getting component: {e}")


if __name__ == "__main__":
    asyncio.run(test_component_service())
