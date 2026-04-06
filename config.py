import os
from pathlib import Path

class NexusConfig:
    def __init__(self, env: str = None):
        self.env = env or os.getenv("NEXUS_ENV", "dev")
        self.load_env()

    def load_env(self):
        # Ortama göre veri yollarını ve portu belirle
        if self.env == "prod":
            self.port = 8902
            self.data_dir = Path("/DATA/AppData/nexus-brain/history")
            self.debug = False
        elif self.env == "test":
            self.port = 8902
            self.data_dir = Path("c:/projects/skills/data/test")
            self.debug = True
        else: # dev (default)
            self.port = 8902
            self.data_dir = Path("c:/projects/skills/data/history")
            self.debug = True

    @property
    def info(self):
        return f"[Nexus-Fetcher] Env: {self.env} | Port: {self.port} | Data: {self.data_dir}"

config = NexusConfig()
