from datetime import datetime

class NexusLogger:
    @staticmethod
    def log(action: str, target: str, status: str = "WAIT"):
        colors = {"OK": "\033[92m", "WAIT": "\033[94m", "ERR": "\033[91m", "END": "\033[0m"}
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{colors[status]}[{ts}] NEXUS-FETCHER | {action:12} | {target[:40]:40} | {status}{colors['END']}")
