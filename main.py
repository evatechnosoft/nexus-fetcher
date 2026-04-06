#!/usr/bin/env python3
"""
Nexus Fetcher MCP Server (Satellite 8902)
Architecture: SOLID / Microservices
"""

import os
import asyncio
from fastmcp import FastMCP

# Paket içinden içe aktarma
from fetcher_mcp.services.search_service import DuckDuckGoSearchEngine
from fetcher_mcp.services.fetch_service import WebFetcher, RedditFetcher
from fetcher_mcp.services.storage_service import NexusStorageService
from fetcher_mcp.utils.logger import NexusLogger

# ---------------------------------------------------------------------------
# MCP Server Initialization
# ---------------------------------------------------------------------------
mcp = FastMCP("nexus-fetcher")

# Bağımlılıkları Örnekle (SOLID: Interface implementations)
search_engine = DuckDuckGoSearchEngine()
web_fetcher = WebFetcher()
reddit_fetcher = RedditFetcher()
storage_service = NexusStorageService()

@mcp.tool()
async def search_web(query: str, max_results: int = 5) -> str:
    """İnternette arama yapar (DDGS)."""
    results = await search_engine.search(query, max_results)
    if not results:
        return f"No results found for '{query}'."
    
    formatted = [f"### {r['title']}\nURL: {r['url']}\n{r['snippet']}\n" for r in results]
    return f"--- Nexus Web Search Results: {query} ---\n\n" + "\n".join(formatted)

@mcp.tool()
async def fetch_url(url: str) -> str:
    """Belirtilen URL'den içerik çeker (Web/Reddit)."""
    if "reddit.com" in url:
        res = await reddit_fetcher.fetch(url)
        if res.get("status") == "ok":
            return f"Reddit Post: {res['title']}\n\n{res['content']}"
        return f"Error: {res.get('error')}"
    
    res = await web_fetcher.fetch(url)
    if res.get("status") == "ok":
        return res["content"]
    return f"Error: {res.get('error')}"

@mcp.tool()
async def save_memory(filename: str, content: str) -> str:
    """Toplanan içeriği merkezi Nexus hafızasına (data/history) kaydeder."""
    return await storage_service.save(filename, content)

if __name__ == "__main__":
    NexusLogger.log("START", "Nexus Fetcher Satellite (8902) is ACTIVE", "OK")
    mcp.run(transport="sse")
