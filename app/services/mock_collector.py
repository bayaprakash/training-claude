"""Mock metrics for offline demos."""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any


def collect_mock_metrics(hostname: str) -> dict[str, Any]:
    bucket = int(time.time() // 30)
    seed = int(hashlib.sha256(f"{hostname}:{bucket}".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    cpu = round(rng.uniform(5, 85), 1)
    mem_total = 8 * 1024**3
    mem_used = int(mem_total * rng.uniform(0.25, 0.8))
    mem_free = mem_total - mem_used
    rx = int(rng.uniform(1e6, 5e8))
    tx = int(rng.uniform(1e6, 3e8))
    ports = sorted(rng.sample([22, 80, 443, 3306, 5432, 6379, 8080, 9090], rng.randint(2, 5)))

    return {
        "status": "mock",
        "hostname": hostname,
        "cpu": {"percent": cpu},
        "memory": {
            "total": mem_total,
            "used": mem_used,
            "free": mem_free,
            "percent": round(mem_used / mem_total * 100, 1),
        },
        "network": {"bytes_recv": rx, "bytes_sent": tx},
        "ports": [{"port": p, "address": f"0.0.0.0:{p}", "state": "LISTEN"} for p in ports],
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
