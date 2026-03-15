# Hefei AV Trajectory Heatmap

Interactive HTML heatmaps of autonomous vehicle GPS trajectory data for Hefei (合肥), China. Visualizes collection density to identify coverage gaps and over-sampled areas.

## Quick Start

```bash
pip install -r requirements.txt
python generate_hefei_heatmap.py
```

A text menu will appear. Pick an option to generate data or render a heatmap.

## Project Structure

```
generate_hefei_heatmap.py   # Main entry point — interactive menu
sub_progs/
│   ├── gen_trajectories.py     # [Menu 1] Generate small mock dataset
│   ├── gen_200k.py             # [Menu 2] Generate large random dataset
│   ├── gen_highway_200k.py     # [Menu 3] Generate road-network dataset
│   ├── convert_raw.py          # [Menu 4] Convert raw navigation logs to CSV
│   ├── heatmap.py              # [Menu 5] Render heatmap from small dataset
│   └── heatmap_large.py        # [Menu 6] Render heatmap from large dataset
data/
│   ├── hefei_mock_trajectory.csv   # Auto-generated if missing
│   └── trajectories/               # 200 trajectory CSVs (traj_001.csv …)
output/                         # Generated HTML heatmaps
raw_format/                     # Raw NDJSON navigation log files
```

## What Each Program Does

### `generate_hefei_heatmap.py` — Main Menu
The single entry point for the whole project. Displays an interactive numbered menu and launches the chosen sub-program. You never need to run the sub-programs directly.

---

### `sub_progs/gen_trajectories.py` — Small Mock Data Generator
Generates a realistic mock dataset of **100 trajectories** around Hefei city center.

- Defines 35 named routes (high / medium / low / single frequency) covering major roads
- Each route is repeated multiple times to simulate real collection density variation
- Adds ±15 m GPS noise to each point
- Output: `hefei_mock_trajectory.csv` (~8,000 GPS points)

Use this for quick tests and demos.

---

### `sub_progs/gen_200k.py` — Large Random Data Generator
Generates **200,000 random trajectories** (1,000,000 GPS points total) across the whole Hefei metropolitan area.

- 60% of trajectories start in the urban core (higher density zone)
- 40% start in suburban/rural areas
- Each trajectory is 300–1,000 m long with 5 sampled points
- Adds ±15 m GPS noise
- Output: 200 CSV files in `trajectories/` (traj_001.csv … traj_200.csv), 1,000 trajectories each

Use this to simulate a full city-scale collection dataset.

---

### `sub_progs/gen_highway_200k.py` — Road-Network Data Generator
Generates **200,000 trajectories that follow real Hefei motorway and trunk roads**, downloaded from OpenStreetMap.

- Downloads the Hefei road graph via `osmnx` and caches it to `hefei_graph.graphml`
- Trajectories walk the actual road geometry, respecting turn connections
- Length: 300–1,000 m per trajectory, weighted by road length so busier roads appear more
- Adds ±10 m GPS noise
- Output: 200 CSV files in `trajectories/`

Use this for the most realistic simulation. Requires `osmnx` and an internet connection on first run.

---

### `sub_progs/convert_raw.py` — Raw Log Converter
Converts real navigation log files (NDJSON format from iFlytek/Amap) into a heatmap-ready CSV.

- Reads all shape points from `msg.route_link_info.links[].shape_points`
- Deduplicates identical coordinates
- Downsamples to 5 representative points per segment
- Input: `raw_format/iflytek_ehr_amap_navi_info.txt` (default)
- Output: `data/converted_trajectory.csv`

Use this when you have real collected driving data to visualize.

---

### `sub_progs/heatmap.py` — Small Heatmap Renderer
Reads a **single CSV file** and renders an interactive HTML heatmap.

- Input: `data/hefei_mock_trajectory.csv` (auto-generates it if missing)
- Rounds coordinates to 4 decimal places (~11 m grid) to aggregate nearby points
- Normalizes frequency weights to 0–1
- Output: `output/Hefei_Trajectory_Heatmap.html`

---

### `sub_progs/heatmap_large.py` — Large Heatmap Renderer
Reads **all 200 trajectory CSV files** and renders a city-scale heatmap.

- Input: `data/trajectories/traj_*.csv`
- Same aggregation and normalization as the small renderer
- Output: `output/Hefei_200k_Heatmap.html`

---

## Color Scale

| Color | Density |
|---|---|
| Blue | Low |
| Cyan → Lime | Medium |
| Red | High |
| Purple | Extreme |

## Configuration

To change map center, input paths, or output paths, edit the constants at the top of the relevant file in `sub_progs/`.

| Variable | Description |
|---|---|
| `DATA_PATH` | Input CSV path (must have `lat`, `lon` columns, WGS84) |
| `OUTPUT_FILE` | Output HTML path |
| `CENTER_LAT`, `CENTER_LON` | Map center coordinates |
