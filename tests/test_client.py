"""Tests for VyOS API client."""

import pytest

from vyos_mcp.client import VyOSClient


def test_client_requires_url():
    with pytest.raises(ValueError, match="VyOS URL required"):
        VyOSClient(api_key="test")


def test_client_requires_api_key():
    with pytest.raises(ValueError, match="API key required"):
        VyOSClient(url="https://example.com")


def test_client_init():
    client = VyOSClient(url="https://vyos.example.com", api_key="test-key")
    assert client.url == "https://vyos.example.com"
    assert client.api_key == "test-key"
    assert client.verify_ssl is False
