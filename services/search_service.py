import asyncio
from duckduckgo_search import DDGS
from fetcher_mcp.interfaces import ISearchEngine
from fetcher_mcp.utils.logger import NexusLogger
from typing import List, Dict, Any

class DuckDuckGoSearchEngine(ISearchEngine):
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        NexusLogger.log("SEARCH", query, "WAIT")
        try:
            results = []
            with DDGS() as ddgs:
                ddgs_results = ddgs.text(query, max_results=max_results)
                for r in ddgs_results:
                    results.append({
                        "title": r['title'],
                        "url": r['href'],
                        "snippet": r['body']
                    })
            NexusLogger.log("SEARCH", query, "OK")
            return results
        except Exception as e:
            NexusLogger.log("SEARCH", str(e), "ERR")
            return []
