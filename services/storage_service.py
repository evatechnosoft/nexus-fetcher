import os
from pathlib import Path
from fetcher_mcp.interfaces import IMemoryGateway
from fetcher_mcp.utils.logger import NexusLogger

class NexusStorageService(IMemoryGateway):
    def __init__(self, base_path: str = "c:/projects/skills/data/history"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content: str) -> str:
        NexusLogger.log("SAVE", filename, "WAIT")
        if not filename.endswith(".md"): 
            filename += ".md"
            
        file_path = self.base_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            NexusLogger.log("SAVE", filename, "OK")
            return f"Success: Saved to {file_path}"
        except Exception as e:
            NexusLogger.log("SAVE", str(e), "ERR")
            return f"Error: {str(e)}"
