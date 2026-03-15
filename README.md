# Hefei AV Trajectory Heatmap

Interactive HTML heatmaps of autonomous vehicle GPS trajectory data for Hefei (合肥), China. Visualizes collection density to identify coverage gaps and over-sampled areas.

## Project Structure

```
├── heatmap.py              # Simple heatmap from a single CSV
├── heatmap_large.py        # Heatmap from 200 trajectory files
├── data/
│   ├── hefei_mock_trajectory.csv   # Auto-generated if missing
│   ├── hefei_graph.graphml         # Hefei road network graph
│   └── trajectories/               # 200 trajectory CSVs (traj_001.csv …)
├── scripts/
│   ├── gen_trajectories.py         # Generate 100-trajectory mock dataset
│   ├── gen_200k.py                 # Generate 200k-point dataset (200 files)
│   └── gen_highway_200k.py         # Generate highway-focused dataset
├── output/                         # Generated HTML heatmaps
└── cache/                          # OSMnx graph cache
```

## Quick Start

```bash
pip install -r requirements.txt
python heatmap.py
```

If `data/hefei_mock_trajectory.csv` does not exist it is auto-generated. Open `output/Hefei_Trajectory_Heatmap.html` in a browser to view the result.

## Large Dataset

```bash
# Generate the dataset first (if not already present)
python scripts/gen_200k.py

# Render the heatmap
python heatmap_large.py
```

Output: `output/Hefei_200k_Heatmap.html`

## Configuration

Edit the constants at the top of each script:

| Variable | Description |
|---|---|
| `DATA_PATH` | Input CSV path (must have `lat`, `lon` columns, WGS84) |
| `OUTPUT_FILE` | Output HTML path |
| `CENTER_LAT`, `CENTER_LON` | Map center coordinates |

## Color Scale

| Color | Density |
|---|---|
| Blue | Low |
| Cyan → Lime | Medium |
| Red | High |
| Purple | Extreme |
