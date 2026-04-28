# generate_devices.py
import csv
import random

OUTPUT_FILE = "devices.csv"
NUM_RECORDS = 5000
SEED = 123

def main():
    random.seed(SEED)

    rows = []
    # ID 0: Main Grid
    rows.append({"ID": 0, "Type": "S", "Name": "Main_Grid", "Value": 4000.0, "Priority": 0})

    # Choose source IDs (excluding 0)
    source_ratio = 0.05  # ~5% sources
    num_sources = int((NUM_RECORDS - 1) * source_ratio)
    source_ids = set(random.sample(range(1, NUM_RECORDS), num_sources))

    for i in range(1, NUM_RECORDS):
        if i in source_ids:
            # DER sources: moderate capacity
            cap = round(random.uniform(5.0, 20.0), 2)
            rows.append({"ID": i, "Type": "S", "Name": f"Source_{i}", "Value": cap, "Priority": 0})
        else:
            # Loads: small to medium demand
            demand = round(random.uniform(0.5, 2.5), 2)
            # Priority distribution: Normal (3) most common
            pr = random.choices([1, 2, 3], weights=[15, 35, 50], k=1)[0]
            rows.append({"ID": i, "Type": "L", "Name": f"Load_{i}", "Value": demand, "Priority": pr})

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Type", "Name", "Value", "Priority"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ {NUM_RECORDS} rows written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()# generate_devices.py
import csv
import random

OUTPUT_FILE = "devices.csv"
NUM_RECORDS = 5000
SEED = 123

def main():
    random.seed(SEED)

    rows = []
    # ID 0: Main Grid
    rows.append({"ID": 0, "Type": "S", "Name": "Main_Grid", "Value": 4000.0, "Priority": 0})

    # Choose source IDs (excluding 0)
    source_ratio = 0.05  # ~5% sources
    num_sources = int((NUM_RECORDS - 1) * source_ratio)
    source_ids = set(random.sample(range(1, NUM_RECORDS), num_sources))

    for i in range(1, NUM_RECORDS):
        if i in source_ids:
            # DER sources: moderate capacity
            cap = round(random.uniform(5.0, 20.0), 2)
            rows.append({"ID": i, "Type": "S", "Name": f"Source_{i}", "Value": cap, "Priority": 0})
        else:
            # Loads: small to medium demand
            demand = round(random.uniform(0.5, 2.5), 2)
            # Priority distribution: Normal (3) most common
            pr = random.choices([1, 2, 3], weights=[15, 35, 50], k=1)[0]
            rows.append({"ID": i, "Type": "L", "Name": f"Load_{i}", "Value": demand, "Priority": pr})

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Type", "Name", "Value", "Priority"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ {NUM_RECORDS} rows written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()