"""Tests for VyOS documentation client."""

import time

import pytest

from vyos_mcp.docs import CacheEntry, DocsClient


class TestCacheEntry:
    def test_valid_entry(self):
        client = DocsClient()
        entry = CacheEntry(data="test", expires_at=time.monotonic() + 100)
        assert client._is_valid(entry) is True

    def test_expired_entry(self):
        client = DocsClient()
        entry = CacheEntry(data="test", expires_at=time.monotonic() - 1)
        assert client._is_valid(entry) is False

    def test_none_entry(self):
        client = DocsClient()
        assert client._is_valid(None) is False


class TestSearch:
    @pytest.fixture
    def client_with_tree(self):
        """DocsClient with a pre-populated tree cache."""
        client = DocsClient()
        client._tree_cache = CacheEntry(
            data=[
                "docs/configuration/firewall/groups.rst",
                "docs/configuration/firewall/index.rst",
                "docs/configuration/firewall/ipv4.rst",
                "docs/configuration/firewall/ipv6.rst",
                "docs/configuration/firewall/zone.rst",
                "docs/configuration/nat/index.rst",
                "docs/configuration/nat/nat44.rst",
                "docs/configuration/nat/nat66.rst",
                "docs/configuration/interfaces/bonding.rst",
                "docs/configuration/interfaces/ethernet.rst",
                "docs/automation/vyos-api.rst",
                "docs/configexamples/firewall.rst",
            ],
            expires_at=time.monotonic() + 3600,
        )
        return client

    async def test_single_term(self, client_with_tree):
        results = await client_with_tree.search("firewall")
        assert len(results) > 0
        assert all("firewall" in r["title"].lower() for r in results)

    async def test_multi_term_ranking(self, client_with_tree):
        results = await client_with_tree.search("firewall groups")
        # "firewall/groups" should rank first (matches both terms)
        assert results[0]["path"] == "docs/configuration/firewall/groups.rst"

    async def test_no_matches(self, client_with_tree):
        results = await client_with_tree.search("nonexistent_topic_xyz")
        assert results == []

    async def test_max_results(self, client_with_tree):
        results = await client_with_tree.search("configuration", max_results=3)
        assert len(results) <= 3

    async def test_result_format(self, client_with_tree):
        results = await client_with_tree.search("nat")
        assert len(results) > 0
        for r in results:
            assert "path" in r
            assert "title" in r
            assert r["path"].startswith("docs/")
            assert r["path"].endswith(".rst")
            assert not r["title"].startswith("docs/")
            assert not r["title"].endswith(".rst")
