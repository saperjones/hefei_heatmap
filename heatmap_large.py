"""
Heatmap generator for the 200-file trajectory dataset.
Reads all CSVs from ./trajectories/, aggregates, and renders HTML.
"""
import pandas as pd
import folium
from folium.plugins import HeatMap
import numpy as np
import glob
import time

TRAJ_DIR    = 'trajectories'
OUTPUT_FILE = 'Hefei_200k_Heatmap.html'
CENTER_LAT, CENTER_LON = 31.8206, 117.2272

# ── 1. Load and aggregate ─────────────────────────────────────────────────────
print("Loading all trajectory files...")
t0 = time.time()

files = sorted(glob.glob(f'{TRAJ_DIR}/traj_*.csv'))
print(f"  Found {len(files)} files")

chunks = []
for i, f in enumerate(files):
    chunks.append(pd.read_csv(f, dtype='float32'))
    if (i + 1) % 40 == 0:
        print(f"  Read {i+1}/{len(files)} files  ({time.time()-t0:.1f}s)")

df = pd.concat(chunks, ignore_index=True)
print(f"  Loaded {len(df):,} GPS points  ({time.time()-t0:.1f}s)")

# ── 2. Clean & aggregate into grid cells ─────────────────────────────────────
print("Aggregating...")
df = df.dropna().drop_duplicates()
df['lat_r'] = df['lat'].round(4)    # ~11 m grid
df['lon_r'] = df['lon'].round(4)

heat = df.groupby(['lat_r', 'lon_r']).size().reset_index(name='w')
heat['w'] = heat['w'] / heat['w'].max()   # normalise 0–1

data_points = heat[['lat_r', 'lon_r', 'w']].values.tolist()
print(f"  {len(data_points):,} unique grid cells  ({time.time()-t0:.1f}s)")

# ── 3. Render heatmap ─────────────────────────────────────────────────────────
print("Rendering heatmap...")
m = folium.Map(
    location=[CENTER_LAT, CENTER_LON],
    zoom_start=11,
    tiles='CartoDB positron',
    control_scale=True,
)

HeatMap(
    data_points,
    radius=10,
    blur=8,
    gradient={
        0.2: 'blue',
        0.4: 'cyan',
        0.6: 'lime',
        0.8: 'red',
        1.0: 'purple',
    },
    min_opacity=0.2,
    max_zoom=18,
).add_to(m)

m.save(OUTPUT_FILE)
print(f"Saved → {OUTPUT_FILE}  ({time.time()-t0:.1f}s total)")
