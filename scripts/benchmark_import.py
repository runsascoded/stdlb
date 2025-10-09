#!/usr/bin/env python
"""Benchmark stdlb import time."""
import sys
import subprocess
import time as time_module
from pathlib import Path

# Add parent directory to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

def benchmark_import(runs=50):
    """Benchmark the import time."""
    code = "from stdlb import *"

    times = []
    for _ in range(runs):
        start = time_module.perf_counter()
        # Run in subprocess to get fresh import each time
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            env={"PYTHONPATH": str(repo_root)},
        )
        end = time_module.perf_counter()

        if result.returncode != 0:
            print(f"Import failed: {result.stderr.decode()}")
            return 1

        times.append((end - start) * 1000)  # Convert to ms

    avg_time_ms = sum(times) / len(times)
    min_time_ms = min(times)
    max_time_ms = max(times)

    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Import time over {runs} runs:")
    print(f"  Average: {avg_time_ms:.2f}ms")
    print(f"  Min: {min_time_ms:.2f}ms")
    print(f"  Max: {max_time_ms:.2f}ms")

    # Warn if too slow
    if avg_time_ms > 50:
        print(f"⚠️  Warning: Import time exceeds 50ms")
        return 1
    elif avg_time_ms > 20:
        print(f"⚠️  Caution: Import time is getting slow (>{20}ms)")
        return 0
    else:
        print(f"✓ Import time is acceptable (<{20}ms)")
        return 0

if __name__ == "__main__":
    sys.exit(benchmark_import())
