"""Utility functions for the Composer Kit MCP server."""

import asyncio
import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import hashlib
import json


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > entry["expires_at"]

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if not self._is_expired(entry):
                return entry["value"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self._default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = {"value": value, "expires_at": expires_at}

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        expired_keys = [
            key for key, entry in self._cache.items() if self._is_expired(entry)
        ]
        for key in expired_keys:
            del self._cache[key]


def create_cache_key(*args: Any) -> str:
    """Create a cache key from arguments."""
    key_data = json.dumps(args, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment variables."""
    return os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")


def normalize_component_name(name: str) -> str:
    """Normalize component name for consistent lookup."""
    # Remove common prefixes/suffixes and normalize case
    name = name.lower().strip()

    # Remove common prefixes
    prefixes = ["composer-kit-", "composer-", "ck-"]
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break

    # Convert kebab-case to camelCase for component lookup
    if "-" in name:
        parts = name.split("-")
        name = parts[0] + "".join(word.capitalize() for word in parts[1:])

    return name


def extract_component_info_from_readme(content: str) -> Dict[str, Any]:
    """Extract component information from README content."""
    info = {"description": "", "props": [], "examples": [], "installation": ""}

    lines = content.split("\n")
    current_section = None

    for line in lines:
        line = line.strip()

        # Detect sections
        if line.startswith("## "):
            current_section = line[3:].lower()
        elif line.startswith("# "):
            # Main title - extract description
            if not info["description"] and len(lines) > lines.index(line) + 1:
                next_line = lines[lines.index(line) + 1].strip()
                if next_line and not next_line.startswith("#"):
                    info["description"] = next_line

        # Extract props from tables
        if current_section == "props" and "|" in line and line.count("|") >= 3:
            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 4 and parts[1] and parts[1] != "Prop":
                info["props"].append(
                    {
                        "name": parts[1],
                        "type": parts[2] if len(parts) > 2 else "",
                        "description": parts[3] if len(parts) > 3 else "",
                        "default": parts[4] if len(parts) > 4 else "",
                    }
                )

    return info


async def retry_with_backoff(
    func: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
) -> Any:
    """Retry function with exponential backoff."""
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            else:
                return func()
        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                break

            delay = min(base_delay * (backoff_factor**attempt), max_delay)
            await asyncio.sleep(delay)

    raise last_exception


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"

    return filename


def parse_github_url(url: str) -> Optional[Dict[str, str]]:
    """Parse GitHub URL to extract owner, repo, and path information."""
    if "github.com" not in url:
        return None

    # Remove protocol and domain
    path = url.split("github.com/", 1)[-1]

    # Remove query parameters and fragments
    path = path.split("?")[0].split("#")[0]

    parts = path.split("/")
    if len(parts) < 2:
        return None

    result = {"owner": parts[0], "repo": parts[1]}

    # Extract additional path information
    if len(parts) > 2:
        if parts[2] in ["tree", "blob"]:
            result["ref"] = parts[3] if len(parts) > 3 else "main"
            result["path"] = "/".join(parts[4:]) if len(parts) > 4 else ""
        else:
            result["path"] = "/".join(parts[2:])

    return result
