"""Compare two benchmark result files: benchmarks/compare.py <baseline-label> <other-label>"""

import json
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"


def main():
    base_label, other_label = sys.argv[1], sys.argv[2]
    base = json.loads((RESULTS_DIR / f"{base_label}.json").read_text())["results"]
    other = json.loads((RESULTS_DIR / f"{other_label}.json").read_text())["results"]

    print(f"{'scenario':25s} {base_label + ' (ms)':>15s} {other_label + ' (ms)':>15s} {'speedup':>9s}")
    for name in base:
        if name not in other:
            continue
        b, o = base[name]["min"], other[name]["min"]
        print(f"{name:25s} {b * 1000:15.3f} {o * 1000:15.3f} {b / o:8.2f}x")


if __name__ == "__main__":
    main()
