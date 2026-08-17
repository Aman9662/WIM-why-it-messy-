"""
Web scraper service — fetches and extracts content from URLs.
"""
import httpx


async def scrape_url(url: str) -> dict:
    """Fetch a URL and extract its main text content."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        import re
        html = response.text
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "No title found"
        
        # Extract meta description
        meta_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        meta_desc = meta_match.group(1).strip() if meta_match else ""
        
        # Remove noisy tags
        html = re.sub(r'<(script|style|nav|footer|header|aside|form)[^>]*>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all other HTML tags
        body = re.sub(r'<[^>]+>', ' ', html)
        
        # Collapse whitespace
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        content = "\n".join(lines[:200])  # First 200 meaningful lines

        return {
            "success": True,
            "title": title,
            "meta_description": meta_desc,
            "content": content,
            "url": url
        }

    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"HTTP error {e.response.status_code}", "url": url}
    except httpx.RequestError as e:
        return {"success": False, "error": f"Connection error: {str(e)}", "url": url}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "url": url}
