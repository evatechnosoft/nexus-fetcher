import asyncio
import json
from fetcher_mcp.fetcher_mcp import mcp

async def test_nexus_gemma():
    query = "Gemma 4 release date reddit"
    print(f"--- [TEST] Arama Sorgusu: {query} ---")
    
    # 1. Web'de Reddit linki ara
    search_tool = mcp.get_tool("search_web")
    search_results = await search_tool(query)
    print("\n[STEP 1] Arama Sonuçları Alındı.")
    
    # 2. Reddit linkini bul ve veriyi çek
    reddit_url = None
    for line in search_results.splitlines():
        if "reddit.com/r/" in line and "URL:" in line:
            reddit_url = line.split("URL:")[1].strip()
            break
            
    if not reddit_url:
        print("[ERR] Uygun Reddit linki bulunamadı.")
        # Fallback to a general search result for demo if no reddit
        reddit_url = "https://www.reddit.com/r/LocalLLaMA/comments/1mgljhp/teaching_lm_studio_to_browse_the_internet_when/" # Demo link if needed
    
    print(f"[STEP 2] Reddit Verisi Çekiliyor: {reddit_url}")
    reddit_tool = mcp.get_tool("fetch_reddit")
    content = await reddit_tool(reddit_url)
    
    # 3. JSON ve MD formatında sun
    md_output = f"# Gemma 4 Research Report\n\nSource: {reddit_url}\n\n{content}"
    
    json_data = {
        "status": "success",
        "search_query": query,
        "source": reddit_url,
        "content_length": len(content),
        "data": content
    }
    
    print("\n--- [RESULT: MD FORMAT] ---")
    print(md_output[:1000] + "...")
    
    print("\n--- [RESULT: JSON FORMAT] ---")
    print(json.dumps(json_data, indent=2, ensure_ascii=False)[:1000] + "...")

if __name__ == "__main__":
    asyncio.run(test_nexus_gemma())
