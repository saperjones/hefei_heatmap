# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A standalone Python script that generates interactive HTML heatmaps of autonomous vehicle GPS trajectory data for Hefei (合肥), China. Visualizes collection density to identify coverage gaps and over-collection areas.

## Running the Project

```bash
pip install pandas folium numpy
python heatmap.py
```

If `hefei_mock_trajectory.csv` does not exist, the script auto-generates sample data before producing `Hefei_Trajectory_Heatmap.html`.

## Configuration

All user-configurable parameters are at the top of `heatmap.py` (lines 7–10):

- `DATA_PATH` — input CSV path (must have `lat` and `lon` columns, WGS84)
- `OUTPUT_FILE` — output HTML filename
- `CENTER_LAT`, `CENTER_LON` — map center coordinates

## Architecture

Single-file pipeline: `generate_sample_data()` → `process_gps_data()` → `generate_heatmap()`

**Data processing logic in `process_gps_data()`:**
- Rounds coordinates to 4 decimal places (~11m grid) to aggregate nearby points and reduce GPS noise
- Groups by rounded coordinates, counts frequency as weight, normalizes to 0–1

**Heatmap rendering in `generate_heatmap()`:**
- Uses Folium with CartoDB Positron basemap
- Color gradient: blue (low) → cyan → lime → red → purple (high density)

## Requirements Spec

`requirements.litcoffee` is a Chinese-language specification document (not executable code) describing the original feature requirements for this tool.
