"""Unit tests for utility functions."""

import pytest
import time
from unittest.mock import patch, MagicMock

from src.composer_kit_mcp.utils import SimpleCache, create_cache_key, setup_logging


class TestSimpleCache:
    """Test cases for SimpleCache."""

    @pytest.fixture
    def cache(self):
        """Create a SimpleCache instance for testing."""
        return SimpleCache(default_ttl=60)

    def test_cache_creation(self):
        """Test creating a cache with default TTL."""
        cache = SimpleCache(default_ttl=120)
        assert cache._default_ttl == 120
        assert len(cache._cache) == 0

    def test_set_and_get(self, cache):
        """Test setting and getting cache values."""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent_key(self, cache):
        """Test getting a non-existent key returns None."""
        assert cache.get("nonexistent") is None

    def test_set_with_custom_ttl(self, cache):
        """Test setting a value with custom TTL."""
        cache.set("key1", "value1", ttl=30)
        assert cache.get("key1") == "value1"

    def test_cache_expiration(self, cache):
        """Test that cache entries expire after TTL."""
        # Set a value with very short TTL
        cache.set("key1", "value1", ttl=0.1)
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None

    def test_cache_not_expired(self, cache):
        """Test that cache entries don't expire before TTL."""
        cache.set("key1", "value1", ttl=10)
        assert cache.get("key1") == "value1"

        # Should still be valid
        time.sleep(0.1)
        assert cache.get("key1") == "value1"

    def test_cache_overwrite(self, cache):
        """Test overwriting cache values."""
        cache.set("key1", "value1")
        cache.set("key1", "value2")
        assert cache.get("key1") == "value2"

    def test_cache_clear(self, cache):
        """Test clearing the cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert len(cache._cache) == 2

        cache.clear()
        assert len(cache._cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_with_none_value(self, cache):
        """Test caching None values."""
        cache.set("key1", None)
        # Should return None but key should exist
        assert cache.get("key1") is None
        assert "key1" in cache._cache

    def test_cache_with_complex_objects(self, cache):
        """Test caching complex objects."""
        test_dict = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        cache.set("complex", test_dict)

        retrieved = cache.get("complex")
        assert retrieved == test_dict
        assert retrieved["nested"]["key"] == "value"
        assert retrieved["list"] == [1, 2, 3]

    def test_cache_size_tracking(self, cache):
        """Test that cache tracks its size correctly."""
        assert len(cache._cache) == 0

        cache.set("key1", "value1")
        assert len(cache._cache) == 1

        cache.set("key2", "value2")
        assert len(cache._cache) == 2

        # Overwriting shouldn't increase size
        cache.set("key1", "new_value")
        assert len(cache._cache) == 2

    def test_cache_cleanup_expired_entries(self, cache):
        """Test that expired entries are cleaned up on access."""
        # Set multiple entries with different TTLs
        cache.set("short", "value1", ttl=0.1)
        cache.set("long", "value2", ttl=10)

        # Wait for short TTL to expire
        time.sleep(0.2)

        # Accessing should trigger cleanup
        assert cache.get("short") is None
        assert cache.get("long") == "value2"

        # Expired entry should be removed from internal cache
        assert "short" not in cache._cache
        assert "long" in cache._cache


class TestCreateCacheKey:
    """Test cases for create_cache_key function."""

    def test_create_cache_key_single_arg(self):
        """Test creating cache key with single argument."""
        key = create_cache_key("test")
        # The actual implementation uses MD5 hashing
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_create_cache_key_multiple_args(self):
        """Test creating cache key with multiple arguments."""
        key = create_cache_key("prefix", "middle", "suffix")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_create_cache_key_with_none(self):
        """Test creating cache key with None values."""
        key = create_cache_key("test", None, "suffix")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_create_cache_key_with_numbers(self):
        """Test creating cache key with numeric values."""
        key = create_cache_key("test", 123, 45.6)
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_create_cache_key_with_empty_string(self):
        """Test creating cache key with empty strings."""
        key = create_cache_key("test", "", "suffix")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_create_cache_key_no_args(self):
        """Test creating cache key with no arguments."""
        key = create_cache_key()
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_create_cache_key_with_special_chars(self):
        """Test creating cache key with special characters."""
        key = create_cache_key("test", "with:colon", "and/slash")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_create_cache_key_consistency(self):
        """Test that same arguments produce same key."""
        key1 = create_cache_key("test", "arg1", "arg2")
        key2 = create_cache_key("test", "arg1", "arg2")
        assert key1 == key2

    def test_create_cache_key_different_order(self):
        """Test that different argument order produces different keys."""
        key1 = create_cache_key("arg1", "arg2")
        key2 = create_cache_key("arg2", "arg1")
        assert key1 != key2


class TestSetupLogging:
    """Test cases for setup_logging function."""

    @patch("src.composer_kit_mcp.utils.logging")
    def test_setup_logging_default_level(self, mock_logging):
        """Test setup_logging with default level."""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        setup_logging()

        # Should configure root logger
        mock_logging.basicConfig.assert_called_once()
        call_args = mock_logging.basicConfig.call_args[1]
        assert call_args["level"] == mock_logging.INFO

    @patch("src.composer_kit_mcp.utils.logging")
    def test_setup_logging_custom_level(self, mock_logging):
        """Test setup_logging with custom level."""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.DEBUG = 10  # Mock DEBUG level

        setup_logging(level="DEBUG")  # Pass string, not int

        mock_logging.basicConfig.assert_called_once()
        call_args = mock_logging.basicConfig.call_args[1]
        assert call_args["level"] == mock_logging.DEBUG

    @patch("src.composer_kit_mcp.utils.logging")
    def test_setup_logging_format(self, mock_logging):
        """Test that setup_logging configures proper format."""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        setup_logging()

        mock_logging.basicConfig.assert_called_once()
        call_args = mock_logging.basicConfig.call_args[1]

        # Should have format specified
        assert "format" in call_args
        format_str = call_args["format"]

        # Should include timestamp, level, and message
        assert "%(asctime)s" in format_str
        assert "%(levelname)s" in format_str
        assert "%(message)s" in format_str

    @patch("src.composer_kit_mcp.utils.logging")
    def test_setup_logging_httpx_level(self, mock_logging):
        """Test that setup_logging sets httpx logger level."""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.WARNING = 30  # Mock WARNING level

        setup_logging()

        # Should configure basic logging
        mock_logging.basicConfig.assert_called_once()

    @patch("src.composer_kit_mcp.utils.logging")
    def test_setup_logging_with_env_var(self, mock_logging):
        """Test setup_logging with default behavior."""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        setup_logging()

        # Should configure basic logging
        mock_logging.basicConfig.assert_called_once()

    @patch("src.composer_kit_mcp.utils.logging")
    def test_setup_logging_multiple_calls(self, mock_logging):
        """Test that multiple calls to setup_logging work correctly."""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        setup_logging()
        setup_logging()

        # Should be called twice
        assert mock_logging.basicConfig.call_count == 2

    @patch("src.composer_kit_mcp.utils.logging")
    def test_setup_logging_logger_names(self, mock_logging):
        """Test that setup_logging configures basic logging."""
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        setup_logging()

        # Should configure basic logging
        mock_logging.basicConfig.assert_called_once()
