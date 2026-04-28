# SDOMS – Smart Distribution Optimization & Management System

## 📌 Overview

SDOMS is a simulation-based project designed to model the core logic of a smart microgrid Energy Management System (EMS). The system integrates concepts from object-oriented programming, graph algorithms, and power system control to manage distributed energy resources (DERs) and maintain grid stability.

The main goal is to simulate how a microgrid controller ensures balance between power generation and demand, especially under critical conditions using load shedding strategies.

---

## ⚙️ Key Features

* **Object-Oriented Design**

  * Abstract base class (`EnergyNode`)
  * Derived classes (`Source`, `Load`)
  * Bitwise state management for device status

* **Graph-Based Connectivity Verification**

  * Adjacency list representation
  * Recursive Depth-First Search (DFS) to ensure connection to main grid

* **Custom Load Shedding Algorithm**

  * Manual implementation of sorting (Bubble/Selection Sort)
  * Priority-based and demand-based load shedding
  * Under-Frequency Load Shedding (UFLS) simulation

* **Energy Analysis**

  * Calculation of Energy Not Served (ENS)
  * Functional programming (`filter`, `map`, `reduce`)

* **Cross-Platform Visualization**

  * Export simulation results to CSV
  * MATLAB-based visualization for:

    * Power balance
    * Load shedding distribution

---

## 📂 Project Structure

```
.
├── devices.csv                # Input: devices (sources & loads)
├── topology.csv              # Input: network connections
├── simulation_results.csv    # Output: simulation results
├── error_log.txt             # Parsing errors
├── main.py                   # Main simulation script
├── visualize_grid.m          # MATLAB visualization script
└── README.md
```

---

## 🚀 How It Works

1. **Data Ingestion**

   * Parse `devices.csv` and instantiate objects
   * Build network graph from `topology.csv`

2. **Connectivity Check**

   * Run DFS to verify nodes are connected to main grid

3. **Power Balance Calculation**

   * Compute total generation and demand

4. **Load Shedding (if needed)**

   * Sort loads based on priority and demand
   * Iteratively turn off loads until balance is restored

5. **Post-Processing**

   * Calculate ENS
   * Export results to CSV

6. **Visualization**

   * Use MATLAB script to generate plots

---

## 🧠 Core Concepts

* Smart Microgrids
* Energy Management Systems (EMS)
* Graph Traversal (DFS)
* Object-Oriented Programming (OOP)
* Bitwise Operations
* Custom Sorting Algorithms
* Functional Programming

---

## 📊 Output Example

* Total Generation vs Demand
* Actual Consumption after Shedding
* Shedded Load by Priority (Critical / High / Normal)

---

## 🛠️ Technologies Used

* Python
* MATLAB
* CSV-based data handling

---

## 📎 Future Improvements

* Replace basic sorting with optimized algorithms
* Add real-time simulation capabilities
* Integrate machine learning for predictive load management
* Develop a GUI dashboard

---

## 👤 Authors

* Alborz Seifaei
* Nima Soltani

---

## 📜 License





## 📄 Project Specification

You can find the full project description here:  
[Project PDF](FP.pdf)

This project is developed for academic purposes as part of an undergraduate programming course.
