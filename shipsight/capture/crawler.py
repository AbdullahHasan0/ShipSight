from bs4 import BeautifulSoup
import httpx
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.visited = set()
        self.to_visit = [base_url]

    async def discover_routes(self, limit: int = 10):
        routes = ["/"]
        domain = urlparse(self.base_url).netloc
        
        async with httpx.AsyncClient() as client:
            while self.to_visit and len(routes) < limit:
                url = self.to_visit.pop(0)
                if url in self.visited:
                    continue
                self.visited.add(url)
                
                try:
                    response = await client.get(url, timeout=5.0)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        for a in soup.find_all("a", href=True):
                            href = a["href"]
                            full_url = urljoin(url, href)
                            parsed = urlparse(full_url)
                            
                            if parsed.netloc == domain and full_url not in self.visited:
                                path = parsed.path or "/"
                                if path not in routes:
                                    routes.append(path)
                                    self.to_visit.append(full_url)
                except Exception:
                    continue
        return routes
