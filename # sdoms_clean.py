# sdoms.py
# SDOMS - Python implementation (no MATLAB)
# Input files (fixed names): devices.csv, topology.csv
# Output: simulation_results.csv + plots/*.png

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Set

import pandas as pd
import matplotlib.pyplot as plt


# =========================
# Phase I: OOP + Bitwise
# =========================
class EnergyNode:
    """
    _status bit-field:
      Bit 0: Connected (0=Disconnected, 1=Connected)
      Bit 1: ON/OFF    (0=OFF, 1=ON)
    """
    BIT_CONNECTED = 1 << 0
    BIT_ON = 1 << 1

    def __init__(self, node_id: int, name: str):
        self.node_id = int(node_id)
        self.name = str(name)
        self._status = 0
        self.turn_on()
        self.set_disconnected()

    # Connectivity
    def set_connected(self) -> None:
        self._status |= self.BIT_CONNECTED

    def set_disconnected(self) -> None:
        self._status &= ~self.BIT_CONNECTED

    def is_connected(self) -> bool:
        return (self._status & self.BIT_CONNECTED) != 0

    # ON/OFF
    def turn_on(self) -> None:
        self._status |= self.BIT_ON

    def turn_off(self) -> None:
        self._status &= ~self.BIT_ON

    def is_on(self) -> bool:
        return (self._status & self.BIT_ON) != 0

    def get_power(self) -> float:
        raise NotImplementedError


class Source(EnergyNode):
    def __init__(self, node_id: int, name: str, generation_capacity: float):
        super().__init__(node_id, name)
        self.generation_capacity = float(generation_capacity)

    def get_power(self) -> float:
        return self.generation_capacity if self.is_on() else 0.0


class Load(EnergyNode):
    def __init__(self, node_id: int, name: str, demand_value: float, priority: int):
        super().__init__(node_id, name)
        self.demand_value = float(demand_value)
        self.priority = int(priority)

    def get_power(self) -> float:
        return -self.demand_value if self.is_on() else 0.0


# Global dict required
network_objects: Dict[int, EnergyNode] = {}


def load_devices(devices_csv: str = "devices.csv", error_log_path: str = "error_log.txt") -> None:
    """
    devices.csv columns: ID, Type(S/L), Name, Value, Priority
    Malformed lines -> error_log.txt
    """
    global network_objects
    network_objects = {}

    with open(error_log_path, "w", encoding="utf-8") as f:
        f.write("")

    with open(devices_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"ID", "Type", "Name", "Value", "Priority"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"devices.csv must contain {required}. Found: {reader.fieldnames}")

        for line_no, row in enumerate(reader, start=2):
            try:
                _id = int(row["ID"])
                _type = row["Type"].strip()
                _name = row["Name"].strip()
                _value = float(row["Value"])
                _prio = int(row["Priority"])

                if _type == "S":
                    obj = Source(_id, _name, _value)
                elif _type == "L":
                    obj = Load(_id, _name, _value, _prio)
                else:
                    raise ValueError(f"Unknown Type={_type}")

                network_objects[_id] = obj

            except Exception as e:
                raw = ",".join(str(row.get(k, "")) for k in (reader.fieldnames or []))
                with open(error_log_path, "a", encoding="utf-8") as ef:
                    ef.write(f"Line {line_no}: {raw} | ERROR: {e}\n")


def load_topology(topology_csv: str = "topology.csv") -> Dict[int, List[int]]:
    """
    topology.csv columns: Source_ID, Target_ID
    Returns directed adjacency list.
    """
    df = pd.read_csv(topology_csv)
    if not {"Source_ID", "Target_ID"}.issubset(df.columns):
        raise ValueError(f"topology.csv must contain Source_ID, Target_ID. Found: {list(df.columns)}")

    graph: Dict[int, List[int]] = {}
    for _, r in df.iterrows():
        u = int(r["Source_ID"])
        v = int(r["Target_ID"])
        graph.setdefault(u, []).append(v)
    return graph


# =========================
# Phase II: DFS (Recursive)
# =========================
def build_undirected_graph(graph: Dict[int, List[int]]) -> Dict[int, List[int]]:
    """
    To interpret 'connected to grid', treat topology edges as undirected for connectivity.
    """
    und: Dict[int, List[int]] = {}
    for u, vs in graph.items():
        und.setdefault(u, [])
        for v in vs:
            und.setdefault(v, [])
            und[u].append(v)
            und[v].append(u)
    return und


def mark_all_disconnected() -> None:
    for obj in network_objects.values():
        obj.set_disconnected()


def dfs_mark_connected(node_id: int, visited: Set[int], graph: Dict[int, List[int]]) -> None:
    """
    Recursive DFS from node 0:
      - marks connected nodes
    """
    visited.add(node_id)
    if node_id in network_objects:
        network_objects[node_id].set_connected()

    for nbr in graph.get(node_id, []):
        if nbr not in visited:
            dfs_mark_connected(nbr, visited, graph)


# =========================
# Phase III: Bubble Sort + Shedding
# =========================
def sort_loads(load_list: List[Load]) -> List[Load]:
    """
    Bubble sort candidates for shedding:
      Priority DESC (3 first)
      Demand DESC
    """
    arr = load_list[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            a, b = arr[j], arr[j + 1]
            swap = False
            if a.priority < b.priority:
                swap = True
            elif a.priority == b.priority and a.demand_value < b.demand_value:
                swap = True
            if swap:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


@dataclass
class BalanceResult:
    total_generation: float
    total_demand_requested: float
    actual_consumption: float
    shed_p1: float
    shed_p2: float
    shed_p3: float


def balance_grid() -> BalanceResult:
    sources = [o for o in network_objects.values() if isinstance(o, Source)]
    loads = [o for o in network_objects.values() if isinstance(o, Load)]

    total_generation = sum(s.get_power() for s in sources)
    total_demand_requested = sum(l.demand_value for l in loads if l.is_on())
    net = sum(o.get_power() for o in sources + loads)

    shed_p1 = shed_p2 = shed_p3 = 0.0

    if net < 0:
        candidates = sort_loads([l for l in loads if l.is_on()])
        for l in candidates:
            if net >= 0:
                break
            l.turn_off()
            amount = l.demand_value
            if l.priority == 1:
                shed_p1 += amount
            elif l.priority == 2:
                shed_p2 += amount
            elif l.priority == 3:
                shed_p3 += amount
            net += amount

    actual_consumption = sum(l.demand_value for l in loads if l.is_on())

    return BalanceResult(
        total_generation=total_generation,
        total_demand_requested=total_demand_requested,
        actual_consumption=actual_consumption,
        shed_p1=shed_p1,
        shed_p2=shed_p2,
        shed_p3=shed_p3,
    )


# =========================
# Phase IV: ENS via filter/map/lambda
# =========================
def compute_ens() -> float:
    loads = [o for o in network_objects.values() if isinstance(o, Load)]
    off_loads = list(filter(lambda l: not l.is_on(), loads))
    off_demands = list(map(lambda l: l.demand_value, off_loads))
    return sum(off_demands)


# =========================
# Export + Plots
# =========================
def export_results(out_csv: str, rows: List[dict]) -> None:
    pd.DataFrame(rows).to_csv(out_csv, index=False)


def plot_pdf_compliant(sim_csv: str) -> None:
    """
    مطابق PDF:
      subplot(2,1,1): Total_Generation & Total_Demand
      subplot(2,1,2): bar totals by priority
    """
    T = pd.read_csv(sim_csv)
    os.makedirs("plots", exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # (1) Power Balance
    axes[0].plot(T["Timestamp"], T["Total_Generation"], label="Total Generation")
    axes[0].plot(T["Timestamp"], T["Total_Demand"], label="Total Demand (Requested)")
    axes[0].set_title("Power Balance")
    axes[0].set_xlabel("Time Step")
    axes[0].set_ylabel("Power (kW)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    # (2) Shedding bar
    totals = [
        float(T["Shedded_Amount_P1"].sum()),
        float(T["Shedded_Amount_P2"].sum()),
        float(T["Shedded_Amount_P3"].sum()),
    ]
    axes[1].bar(["Critical", "High", "Normal"], totals)
    axes[1].set_title("Load Shedding by Priority (Total)")
    axes[1].set_xlabel("Priority")
    axes[1].set_ylabel("Shedded Power (kW)")
    axes[1].grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("plots/figure_1_2.png", dpi=220)
    plt.close(fig)


def plot_extra(sim_csv: str) -> None:
    """
    نمودار اضافی برای اینکه منطق shedding واضح باشد (اختیاری).
    """
    T = pd.read_csv(sim_csv)
    os.makedirs("plots", exist_ok=True)

    plt.figure(figsize=(12, 5))
    plt.plot(T["Timestamp"], T["Total_Generation"], label="Total Generation", linewidth=1.8)
    plt.plot(T["Timestamp"], T["Total_Demand"], label="Requested Demand", linewidth=1.2)
    plt.plot(T["Timestamp"], T["Actual_Consumption"], label="Served Demand (After Shedding)", linewidth=2.2)
    plt.title("Served vs Requested (UFLS Behavior)")
    plt.xlabel("Time Step")
    plt.ylabel("Power (kW)")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig("plots/served_vs_requested.png", dpi=220)
    plt.close()


# =========================
# Main Simulation
# =========================
def run_simulation(sim_steps: int = 5000) -> None:
    # Fixed input names
    devices_csv = "devices.csv"
    topology_csv = "topology.csv"

    # Fixed output
    out_csv = "simulation_results.csv"

    # Basic run info
    print("CWD =", os.getcwd())
    print("Expecting input files:", devices_csv, topology_csv)

    load_devices(devices_csv)
    graph = load_topology(topology_csv)
    und_graph = build_undirected_graph(graph)

    rows: List[dict] = []

    for t in range(sim_steps):
        if t % 250 == 0:
            print(f"Progress: {t}/{sim_steps}")

        # Connectivity: one DFS from 0
        mark_all_disconnected()
        visited = set()
        dfs_mark_connected(0, visited, und_graph)

        # Turn off disconnected devices (if any)
        for obj in network_objects.values():
            if not obj.is_connected():
                obj.turn_off()

        br = balance_grid()
        ens = compute_ens()

        rows.append({
            "Timestamp": t,
            "Total_Generation": br.total_generation,
            "Total_Demand": br.total_demand_requested,
            "Actual_Consumption": br.actual_consumption,
            "Shedded_Amount_P1": br.shed_p1,
            "Shedded_Amount_P2": br.shed_p2,
            "Shedded_Amount_P3": br.shed_p3,
            "ENS_Total": ens,
        })

    export_results(out_csv, rows)
    plot_pdf_compliant(out_csv)
    plot_extra(out_csv)

    print("Done:")
    print(" - simulation_results.csv")
    print(" - plots/figure_1_2.png (PDF compliant)")
    print(" - plots/served_vs_requested.png (extra)")


if __name__ == "__main__":
    run_simulation(sim_steps=5000)
