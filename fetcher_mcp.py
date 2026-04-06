#!/usr/bin/env python3
"""
Nexus Fetcher Satellite (8902)
Merkezi Nexus sistemine internet tarama ve veri çekme hizmeti sunan bağımsız uydu.

Hizmet Portu: 8902
Bağımlılıklar: duckduckgo-search, httpx, beautifulsoup4, fastmcp
"""

import os
import json
import asyncio
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
from fastmcp import FastMCP
from duckduckgo_search import DDGS
from typing import Optional, List
from pathlib import Path

# --- Görsel Takip için Loglama ---
def nexus_log(action: str, target: str, status: str = "WAIT"):
    colors = {"OK": "\033[92m", "WAIT": "\033[94m", "ERR": "\033[91m", "END": "\033[0m"}
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{colors[status]}[{ts}] NEXUS-FETCHER | {action:12} | {target[:40]:40} | {status}{colors['END']}")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
DATA_DIR = Path(os.getenv("AI_SYNC_DATA", "c:/projects/skills/data"))
MEMORY_DIR = DATA_DIR / "history"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# MCP Server (Satellite Identity)
# ---------------------------------------------------------------------------
mcp = FastMCP("nexus-fetcher")

@mcp.tool()
async def search_web(query: str, max_results: int = 5) -> str:
    """
    DuckDuckGo kütüphanesini kullanarak internette arama yapar. (Yüksek Hız)
    """
    nexus_log("SEARCH", query, "WAIT")
    try:
        results = []
        with DDGS() as ddgs:
            ddgs_results = ddgs.text(query, max_results=max_results)
            for i, r in enumerate(ddgs_results):
                results.append(f"### {r['title']}\nURL: {r['href']}\n{r['body']}\n")
        
        if not results:
            nexus_log("SEARCH", query, "ERR")
            return f"No results found for '{query}'."
            
        nexus_log("SEARCH", query, "OK")
        return f"--- Nexus Web Search: {query} ---\n\n" + "\n".join(results)
        
    except Exception as e:
        nexus_log("SEARCH", str(e), "ERR")
        return f"Error performing search: {str(e)}"

@mcp.tool()
async def fetch_url(url: str) -> str:
    """
    Belirtilen URL'den ana metni çeker ve HTML etiketlerini temizler.
    """
    nexus_log("FETCH", url, "WAIT")
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            
            nexus_log("FETCH", url, "OK")
            return f"--- Content from {url} ---\n\n{text[:15000]}" # 15k limit
            
        except Exception as e:
            nexus_log("FETCH", str(e), "ERR")
            return f"Error fetching URL: {str(e)}"

@mcp.tool()
async def fetch_reddit(url: str) -> str:
    """
    Reddit postunu ve en iyi yorumlarını analiz eder.
    """
    nexus_log("REDDIT", url, "WAIT")
    json_url = url if url.endswith(".json") else f"{url.rstrip('/')}/.json"
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(json_url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                post = data[0]['data']['children'][0]['data']
                title = post.get('title', 'No Title')
                content = post.get('selftext', 'No content')
                
                nexus_log("REDDIT", title, "OK")
                return f"Title: {title}\n\nContent:\n{content[:10000]}"
            else:
                nexus_log("REDDIT", "Structure Error", "ERR")
                return "Error: Unexpected Reddit structure."
        except Exception as e:
            nexus_log("REDDIT", str(e), "ERR")
            return f"Error: {str(e)}"

@mcp.tool()
async def save_to_nexus_memory(filename: str, content: str) -> str:
    """
    Toplanan bilgiyi merkezi Nexus hafızasına (history mirror) kaydeder.
    """
    nexus_log("SAVE", filename, "WAIT")
    if not filename.endswith(".md"): filename += ".md"
    file_path = MEMORY_DIR / filename
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        nexus_log("SAVE", filename, "OK")
        return f"Success: Content saved to {file_path}"
    except Exception as e:
        nexus_log("SAVE", str(e), "ERR")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # 8902 portunda SSE sunucusu olarak başlat
    nexus_log("START", "Nexus Fetcher Satellite on Port 8902", "OK")
    mcp.run(transport="sse")
