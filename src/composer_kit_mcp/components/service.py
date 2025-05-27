"""Service for managing Composer Kit components."""

import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx

from .models import (
    Component,
    ComponentExample,
    ComponentProp,
    ComponentRegistry,
)
from ..utils import (
    SimpleCache,
    create_cache_key,
)

logger = logging.getLogger(__name__)


class ComponentService:
    """Service for accessing Composer Kit components from GitHub."""

    def __init__(self):
        self.cache = SimpleCache(default_ttl=3600)  # 1 hour cache
        self.raw_base_url = "https://raw.githubusercontent.com"
        self.repo_owner = "celo-org"
        self.repo_name = "composer-kit"
        self.main_branch = "main"

        # Component paths in the repository - updated based on actual structure
        self.components_path = "packages/ui/src"  # Actual UI components
        self.examples_path = "apps/docs/examples"  # Examples
        self.docs_path = "apps/docs"

        # Known component categories and their mappings
        self.component_categories = {
            "address": "Core Components",
            "balance": "Core Components",
            "identity": "Core Components",
            "wallet": "Wallet Integration",
            "connect": "Wallet Integration",
            "payment": "Payment & Transactions",
            "transaction": "Payment & Transactions",
            "swap": "Payment & Transactions",
            "tokenselect": "Token Management",
            "token-select": "Token Management",
            "nftcard": "NFT Components",
            "nft-card": "NFT Components",
            "nftmint": "NFT Components",
            "nft-mint": "NFT Components",
        }

        # Known components based on the examples directory structure
        self.known_components = [
            "address",
            "balance",
            "identity",
            "nft",
            "payment",
            "swap",
            "token-select",
            "transaction",
            "wallet",
        ]

    async def _get_raw_file_content(self, path: str, ref: str = None) -> Optional[str]:
        """Get file content directly from GitHub raw URLs."""
        ref = ref or "refs/heads/main"  # Updated to use refs/heads/main
        cache_key = create_cache_key("raw_file_content", path, ref)

        # Check cache first
        cached_content = self.cache.get(cache_key)
        if cached_content is not None:
            return cached_content

        try:
            url = f"{self.raw_base_url}/{self.repo_owner}/{self.repo_name}/{ref}/{path}"
            logger.debug(f"Fetching raw content from: {url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content = response.text
                    self.cache.set(cache_key, content)
                    logger.debug(
                        f"Successfully fetched {len(content)} characters from {path}"
                    )
                    return content
                elif response.status_code == 404:
                    logger.debug(f"File not found: {path}")
                    return None
                else:
                    logger.warning(
                        f"Failed to fetch {path}: HTTP {response.status_code}"
                    )
                    return None
        except Exception as e:
            logger.warning(f"Failed to get raw file content for {path}: {e}")

        return None

    async def _discover_components(self) -> List[str]:
        """Discover available components using known component list and validation."""
        cache_key = create_cache_key("discovered_components")

        # Check cache first
        cached_components = self.cache.get(cache_key)
        if cached_components is not None:
            logger.info(f"Found {len(cached_components)} cached components")
            return cached_components

        components = []

        try:
            logger.info(
                f"Discovering components from known list: {self.known_components}"
            )

            # Check each known component to see if it exists
            for component_name in self.known_components:
                # Try to find the component's main file
                component_exists = await self._component_exists(component_name)
                if component_exists:
                    logger.info(f"Found component: {component_name}")
                    components.append(component_name)
                else:
                    logger.debug(f"Component not found: {component_name}")

            logger.info(f"Discovered {len(components)} components: {components}")
            # Cache the discovered components
            self.cache.set(cache_key, components, ttl=7200)  # 2 hours cache

        except Exception as e:
            logger.error(f"Failed to discover components: {e}")
            logger.exception("Full traceback:")

        return components

    async def _component_exists(self, component_name: str) -> bool:
        """Check if a component exists by trying to fetch its files from examples or UI packages."""
        # Check for examples using the correct structure: examples/{component_name}/basic.tsx
        if component_name == "nft":
            # Special case for NFT which has mint.tsx and preview.tsx instead of basic.tsx
            nft_paths = [
                f"{self.examples_path}/{component_name}/mint.tsx",
                f"{self.examples_path}/{component_name}/preview.tsx",
            ]
            for path in nft_paths:
                content = await self._get_raw_file_content(path)
                if content:
                    logger.debug(f"Found NFT example for {component_name} at {path}")
                    return True
        else:
            # Standard structure: examples/{component_name}/basic.tsx
            basic_path = f"{self.examples_path}/{component_name}/basic.tsx"
            content = await self._get_raw_file_content(basic_path)
            if content:
                logger.debug(f"Found example for {component_name} at {basic_path}")
                return True

        # Fallback: check if there's a UI component (though this might not exist)
        ui_paths = [
            f"{self.components_path}/{component_name}/index.tsx",
            f"{self.components_path}/{component_name}/index.ts",
        ]

        for path in ui_paths:
            content = await self._get_raw_file_content(path)
            if content:
                logger.debug(f"Found UI component for {component_name} at {path}")
                return True

        return False

    async def _get_component_source_code(self, component_name: str) -> Optional[str]:
        """Get the source code for a component from examples first, then UI packages."""
        # First try to get example code (this is what we actually have)
        if component_name == "nft":
            # Special case for NFT - try mint.tsx first, then preview.tsx
            nft_paths = [
                f"{self.examples_path}/{component_name}/mint.tsx",
                f"{self.examples_path}/{component_name}/preview.tsx",
            ]
            for path in nft_paths:
                content = await self._get_raw_file_content(path)
                if content:
                    logger.debug(f"Found NFT source for {component_name} at {path}")
                    return content
        else:
            # Standard structure: examples/{component_name}/basic.tsx
            basic_path = f"{self.examples_path}/{component_name}/basic.tsx"
            content = await self._get_raw_file_content(basic_path)
            if content:
                logger.debug(f"Found source code for {component_name} at {basic_path}")
                return content

        # Fallback: try UI component paths (though these might not exist)
        ui_paths = [
            f"{self.components_path}/{component_name}/index.tsx",
            f"{self.components_path}/{component_name}/index.ts",
        ]

        for path in ui_paths:
            content = await self._get_raw_file_content(path)
            if content:
                logger.debug(f"Found UI source for {component_name} at {path}")
                return content

        return None

    async def _get_component_examples(
        self, component_name: str
    ) -> List[ComponentExample]:
        """Get examples for a component from the examples directory."""
        examples = []

        try:
            if component_name == "nft":
                # Special case for NFT which has mint.tsx and preview.tsx
                nft_example_paths = [
                    f"{self.examples_path}/{component_name}/mint.tsx",
                    f"{self.examples_path}/{component_name}/preview.tsx",
                ]

                for path in nft_example_paths:
                    content = await self._get_raw_file_content(path)
                    if content:
                        filename = path.split("/")[-1]
                        example_name = filename.replace(".tsx", "").replace(".ts", "")
                        description = self._extract_example_description(content)

                        examples.append(
                            ComponentExample(
                                name=f"{component_name}-{example_name}",
                                description=description,
                                code=content,
                                file_path=path,
                                category="example",
                            )
                        )
                        logger.debug(
                            f"Found NFT example {example_name} for {component_name}"
                        )
            else:
                # Standard case: look for basic.tsx
                basic_path = f"{self.examples_path}/{component_name}/basic.tsx"
                content = await self._get_raw_file_content(basic_path)
                if content:
                    description = self._extract_example_description(content)
                    examples.append(
                        ComponentExample(
                            name=f"{component_name}-basic",
                            description=description,
                            code=content,
                            file_path=basic_path,
                            category="example",
                        )
                    )
                    logger.debug(f"Found basic example for {component_name}")

            # If no examples found, generate a basic one
            if not examples:
                example_code = self._generate_example_code(component_name)
                examples.append(
                    ComponentExample(
                        name=f"{component_name}-basic",
                        description=f"Basic usage example for {component_name} component",
                        code=example_code,
                        file_path=f"examples/{component_name}-basic.tsx",
                        category="example",
                    )
                )

        except Exception as e:
            logger.warning(f"Failed to get examples for {component_name}: {e}")

        return examples

    def _generate_example_code(self, component_name: str) -> str:
        """Generate a basic example code for a component."""
        component_display_name = component_name.replace("-", "").title()

        return f"""import {{ {component_display_name} }} from "@composer-kit/ui";

export default function {component_display_name}Example() {{
  return (
    <div>
      <h2>{component_display_name} Example</h2>
      <{component_display_name} />
    </div>
  );
}}"""

    def _extract_example_description(self, content: str) -> str:
        """Extract description from example file content."""
        # Look for comments at the top of the file
        lines = content.split("\n")
        description_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("//") or line.startswith("/*") or line.startswith("*"):
                # Remove comment markers
                clean_line = re.sub(r"^[/*\s]*", "", line).strip()
                if clean_line and not clean_line.startswith("@"):
                    description_lines.append(clean_line)
            elif line and not line.startswith("import"):
                break

        return " ".join(description_lines) if description_lines else "Example usage"

    def _extract_component_props(self, source_code: str) -> List[ComponentProp]:
        """Extract component props from TypeScript source code."""
        props = []

        try:
            # Look for interface or type definitions
            interface_pattern = r"interface\s+(\w+Props)\s*{([^}]+)}"
            type_pattern = r"type\s+(\w+Props)\s*=\s*{([^}]+)}"

            for pattern in [interface_pattern, type_pattern]:
                matches = re.finditer(pattern, source_code, re.DOTALL)
                for match in matches:
                    props_content = match.group(2)

                    # Parse individual props
                    prop_lines = props_content.split("\n")
                    for line in prop_lines:
                        line = line.strip()
                        if line and not line.startswith("//") and ":" in line:
                            # Parse prop definition
                            prop_match = re.match(r"(\w+)(\??):\s*([^;]+)", line)
                            if prop_match:
                                prop_name = prop_match.group(1)
                                is_optional = prop_match.group(2) == "?"
                                prop_type = prop_match.group(3).strip()

                                props.append(
                                    ComponentProp(
                                        name=prop_name,
                                        type=prop_type,
                                        description="",  # Would need JSDoc parsing for descriptions
                                        required=not is_optional,
                                    )
                                )

        except Exception as e:
            logger.warning(f"Failed to extract props from source code: {e}")

        return props

    def _get_component_category(self, component_name: str) -> str:
        """Get the category for a component."""
        name_lower = component_name.lower()
        return self.component_categories.get(name_lower, "Other")

    async def get_component_registry(self) -> ComponentRegistry:
        """Get the complete component registry."""
        cache_key = create_cache_key("component_registry")

        # Check cache first
        cached_registry = self.cache.get(cache_key)
        if cached_registry is not None:
            return ComponentRegistry(**cached_registry)

        registry = ComponentRegistry()

        try:
            # Discover all components
            component_names = await self._discover_components()

            # Process each component
            for component_name in component_names:
                component = await self._build_component(component_name)
                if component:
                    registry.components[component_name] = component

                    # Add category to registry
                    if component.category not in registry.categories:
                        registry.categories.append(component.category)

            registry.last_updated = datetime.now()

            # Cache the registry
            self.cache.set(cache_key, registry.dict(), ttl=3600)  # 1 hour cache

        except Exception as e:
            logger.error(f"Failed to build component registry: {e}")

        return registry

    async def _build_component(self, component_name: str) -> Optional[Component]:
        """Build a complete component object."""
        try:
            # Get source code
            source_code = await self._get_component_source_code(component_name)

            # Get examples
            examples = await self._get_component_examples(component_name)

            # Extract props from source code
            props = []
            if source_code:
                props = self._extract_component_props(source_code)

            # Get category
            category = self._get_component_category(component_name)

            # Create component
            component = Component(
                name=component_name,
                display_name=component_name.title(),
                description=f"Composer Kit {component_name} component for Celo dApps",
                category=category,
                source_code=source_code,
                file_path=f"{self.components_path}/{component_name}",
                props=props,
                examples=examples,
                dependencies=["@composer-kit/ui"],
                installation_command="npm install @composer-kit/ui",
                documentation_url=f"https://github.com/{self.repo_owner}/{self.repo_name}",
                last_updated=datetime.now(),
            )

            return component

        except Exception as e:
            logger.warning(f"Failed to build component {component_name}: {e}")
            return None

    async def get_component(self, component_name: str) -> Optional[Component]:
        """Get a specific component by name."""
        registry = await self.get_component_registry()
        return registry.get_component(component_name)

    async def list_components(self) -> List[Component]:
        """List all available components."""
        registry = await self.get_component_registry()
        return list(registry.components.values())

    async def search_components(self, query: str) -> List[Component]:
        """Search for components by query."""
        registry = await self.get_component_registry()
        return registry.search_components(query)

    async def get_components_by_category(self, category: str) -> List[Component]:
        """Get components by category."""
        registry = await self.get_component_registry()
        return registry.get_components_by_category(category)

    async def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        logger.info("Cache cleared")

    async def debug_github_access(self) -> Dict[str, Any]:
        """Debug method to test GitHub raw content access."""
        debug_info = {
            "raw_base_url": self.raw_base_url,
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "components_path": self.components_path,
            "known_components": self.known_components,
            "test_results": {},
        }

        try:
            # Test fetching a known file (README)
            readme_content = await self._get_raw_file_content("README.md")
            debug_info["test_results"]["readme_access"] = {
                "success": bool(readme_content),
                "content_length": len(readme_content) if readme_content else 0,
            }
        except Exception as e:
            debug_info["test_results"]["readme_access"] = {
                "success": False,
                "error": str(e),
            }

        try:
            # Test component discovery
            components = await self._discover_components()
            debug_info["test_results"]["component_discovery"] = {
                "success": True,
                "components_found": len(components),
                "components": components,
            }
        except Exception as e:
            debug_info["test_results"]["component_discovery"] = {
                "success": False,
                "error": str(e),
            }

        return debug_info
