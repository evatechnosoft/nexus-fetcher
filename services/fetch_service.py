import httpx
from bs4 import BeautifulSoup
from fetcher_mcp.interfaces import IContentFetcher
from fetcher_mcp.utils.logger import NexusLogger
from typing import Dict, Any

class WebFetcher(IContentFetcher):
    async def fetch(self, url: str) -> Dict[str, Any]:
        NexusLogger.log("FETCH", url, "WAIT")
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                
                text = soup.get_text(separator="\n")
                content = "\n".join(line.strip() for line in text.splitlines() if line.strip())
                NexusLogger.log("FETCH", url, "OK")
                return {"url": url, "content": content[:15000], "status": "ok"}
            except Exception as e:
                NexusLogger.log("FETCH", str(e), "ERR")
                return {"url": url, "error": str(e), "status": "err"}

class RedditFetcher(IContentFetcher):
    async def fetch(self, url: str) -> Dict[str, Any]:
        NexusLogger.log("REDDIT", url, "WAIT")
        json_url = url if url.endswith(".json") else f"{url.rstrip('/')}/.json"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(json_url, headers=headers, follow_redirects=True)
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    post = data[0]['data']['children'][0]['data']
                    NexusLogger.log("REDDIT", post.get('title', 'Post'), "OK")
                    return {
                        "title": post.get('title'),
                        "content": post.get('selftext'),
                        "ups": post.get('ups'),
                        "status": "ok"
                    }
                return {"error": "Invalid Structure", "status": "err"}
            except Exception as e:
                NexusLogger.log("REDDIT", str(e), "ERR")
                return {"error": str(e), "status": "err"}
