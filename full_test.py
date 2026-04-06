import asyncio
import json
import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# --- Minimal Fetcher Tools (Test Version) ---
async def search_web(query, max_results=5):
    results = []
    with DDGS() as ddgs:
        ddgs_results = ddgs.text(query, max_results=max_results)
        for r in ddgs_results:
            results.append({"title": r['title'], "url": r['href'], "body": r['body']})
    return results

async def fetch_reddit(url):
    json_url = url if url.endswith(".json") else f"{url.rstrip('/')}/.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(json_url, headers=headers, follow_redirects=True)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            post = data[0]['data']['children'][0]['data']
            return {
                "title": post.get('title'),
                "content": post.get('selftext'),
                "author": post.get('author'),
                "ups": post.get('ups')
            }
        return {"error": "Invalid Reddit Response"}

async def run_test():
    query = "Gemma 4 release rumors reddit"
    print(f"--- [Nexus Test] Searching: {query} ---")
    
    # 1. Search
    search_results = await search_web(query)
    reddit_url = None
    for res in search_results:
        if "reddit.com/r/" in res['url']:
            reddit_url = res['url']
            break
    
    if not reddit_url:
        print("No Reddit link found in first search results.")
        return
    
    # 2. Fetch Reddit
    print(f"--- [Nexus Test] Fetching Reddit: {reddit_url} ---")
    reddit_data = await fetch_reddit(reddit_url)
    
    # 3. MD Format
    md_output = f"""# Nexus Gemma Research
**Source:** {reddit_url}
**Title:** {reddit_data.get('title')}
**Author:** u/{reddit_data.get('author')}
**Upvotes:** {reddit_data.get('ups')}

## Content:
{reddit_data.get('content')[:2000]}
"""
    
    # 4. JSON Format
    json_output = json.dumps({
        "status": "success",
        "search_query": query,
        "source": reddit_url,
        "payload": reddit_data
    }, indent=2, ensure_ascii=False)
    
    print("\n[RESULT: MARKDOWN]\n" + "="*20 + "\n" + md_output)
    print("\n[RESULT: JSON]\n" + "="*20 + "\n" + json_output)

if __name__ == "__main__":
    asyncio.run(run_test())
