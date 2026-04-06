from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISearchEngine(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        pass

class IContentFetcher(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> Dict[str, Any]:
        pass

class IMemoryGateway(ABC):
    @abstractmethod
    async def save(self, filename: str, content: str) -> str:
        pass
