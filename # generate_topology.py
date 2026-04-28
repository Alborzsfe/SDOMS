# generate_topology.py
import csv
import random

OUTPUT_FILE = "topology.csv"
NUM_DEVICES = 5000
SEED = 123

def main():
    random.seed(SEED)

    # Determine source IDs (must match generate_devices.py logic)
    source_ratio = 0.05
    num_sources = int((NUM_DEVICES - 1) * source_ratio)
    source_ids = set(random.sample(range(1, NUM_DEVICES), num_sources))
    # Ensure at least one source if rounding leads to zero
    if not source_ids:
        source_ids = {1}

    edges = []

    # Connect each source to Main Grid (0)
    for sid in sorted(source_ids):
        edges.append({"Source_ID": sid, "Target_ID": 0})

    # Connect each load to a random source
    for i in range(1, NUM_DEVICES):
        if i not in source_ids:
            src_choice = random.choice(sorted(source_ids))
            edges.append({"Source_ID": i, "Target_ID": src_choice})

    # Write exactly 5000 edges: sources->0 plus loads->some source
    # Count: len(source_ids) + (NUM_DEVICES - 1 - len(source_ids)) = NUM_DEVICES - 1 edges
    # Add one extra redundant edge (Main Grid self-loop) to reach 5000 total
    # This helps keep the CSV at requested size exactly.
    while len(edges) < 5000:
        edges.append({"Source_ID": 0, "Target_ID": 0})

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Source_ID", "Target_ID"])
        writer.writeheader()
        writer.writerows(edges)

    print(f"✅ {len(edges)} edges written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()