import requests
from requests.auth import HTTPBasicAuth
from app.config import (
    CONFLUENCE_BASE_URL,
    CONFLUENCE_EMAIL,
    CONFLUENCE_API_TOKEN,
    CONFLUENCE_SPACE_KEY,
)

class ConfluenceClient:
    def __init__(self):
        self.base_url = CONFLUENCE_BASE_URL.rstrip("/")
        self.auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
        self.headers = {"Accept": "application/json"}

    def search_pages(self, query: str, limit: int = 8):
        cql_parts = ['type="page"']
        if CONFLUENCE_SPACE_KEY:
            cql_parts.append(f'space="{CONFLUENCE_SPACE_KEY}"')
        cql_parts.append(f'text ~ "{query}"')
        cql = " AND ".join(cql_parts)

        url = f"{self.base_url}/rest/api/search"
        params = {
            "cql": cql,
            "limit": limit,
            "expand": "content.space,content.version"
        }

        resp = requests.get(url, headers=self.headers, auth=self.auth, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        pages = []
        for item in data.get("results", []):
            content = item.get("content", {})
            page_id = content.get("id")
            title = content.get("title", "Untitled")
            webui = item.get("_links", {}).get("webui", "")
            base = item.get("_links", {}).get("base", self.base_url)
            url = f"{base}{webui}" if webui else ""
            excerpt = item.get("excerpt", "")

            pages.append({
                "id": page_id,
                "title": title,
                "url": url,
                "snippet": excerpt
            })

        return pages

    def get_page_content(self, page_id: str):
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {"expand": "body.storage"}
        resp = requests.get(url, headers=self.headers, auth=self.auth, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "html": data.get("body", {}).get("storage", {}).get("value", "")
        }