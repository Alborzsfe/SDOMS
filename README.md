# SDOMS — Smart Distribution Optimization and Management System

SDOMS is an educational Python simulation of a simplified microgrid controller. It combines object-oriented device models, graph connectivity checks, power balancing, and priority-based load shedding.

## Scope and limitations

This repository is a software simulation, not a validated power-system or under-frequency load-shedding model. It does not model grid frequency or dynamic electrical transients. Reported power values and load-shedding totals must therefore not be interpreted as energy without multiplying by the simulation timestep.

## Files

- `generate_devices.py`: creates deterministic example devices
- `generate_topology.py`: creates a connected example topology without self-loops
- `sdoms.py`: runs the simulation using `devices.csv` and `topology.csv`
- `FP.pdf`: original project report

Generated CSV files, plots, and simulation results are excluded from Git.

## Setup and run

```bash
git clone https://github.com/Alborzsfe/SDOMS.git
cd SDOMS
python -m venv .venv
pip install -r requirements.txt
python generate_devices.py
python generate_topology.py
python sdoms.py
```

The generators use a fixed random seed so the example input is reproducible.

## Quality check

GitHub Actions performs syntax compilation. A scientifically meaningful validation suite will require documented reference scenarios and expected numerical outputs.

## License

MIT
