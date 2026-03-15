"""
Generate 200,000 trajectories across Hefei city.
- Each trajectory: 5 GPS points, 300–1000 m long
- 1,000 trajectories per file → 200 files in ./trajectories/
- Density bias: 60% urban core, 40% suburban, to produce varied heat colors
"""
import numpy as np
import pandas as pd
import os
import time

np.random.seed(42)

N_TOTAL    = 200_000
N_PER_FILE = 1_000
N_FILES    = N_TOTAL // N_PER_FILE   # 200
N_PTS      = 5                        # sample points per trajectory
GPS_NOISE  = 0.00015                  # ~15 m std dev

# At latitude 31.8°, meters → degrees
M_PER_DEG_LAT = 111_320.0
M_PER_DEG_LON = 111_320.0 * np.cos(np.radians(31.8))   # ≈ 94 700 m

# ── Hefei coverage bounds ─────────────────────────────────────────────────────
LAT_MIN, LAT_MAX = 31.50, 32.20
LON_MIN, LON_MAX = 116.70, 117.80

# Urban core (higher density)
U_LAT_MIN, U_LAT_MAX = 31.72, 32.00
U_LON_MIN, U_LON_MAX = 117.05, 117.45

# ── Generate start points ─────────────────────────────────────────────────────
n_urban = int(N_TOTAL * 0.60)
n_suburban = N_TOTAL - n_urban

urban_lats = np.random.uniform(U_LAT_MIN, U_LAT_MAX, n_urban)
urban_lons = np.random.uniform(U_LON_MIN, U_LON_MAX, n_urban)

suburban_lats = np.random.uniform(LAT_MIN, LAT_MAX, n_suburban)
suburban_lons = np.random.uniform(LON_MIN, LON_MAX, n_suburban)

start_lats = np.concatenate([urban_lats, suburban_lats])
start_lons = np.concatenate([urban_lons, suburban_lons])

# Shuffle so urban/suburban are interleaved across files
perm = np.random.permutation(N_TOTAL)
start_lats = start_lats[perm]
start_lons = start_lons[perm]

# ── Direction & length ────────────────────────────────────────────────────────
angles  = np.random.uniform(0, 2 * np.pi, N_TOTAL)
lengths = np.random.uniform(300, 1000, N_TOTAL)          # metres

dlat = (lengths * np.cos(angles)) / M_PER_DEG_LAT
dlon = (lengths * np.sin(angles)) / M_PER_DEG_LON

end_lats = start_lats + dlat
end_lons = start_lons + dlon

# ── Interpolate 5 points along each trajectory ───────────────────────────────
# Result shapes: (N_TOTAL, N_PTS)
t = np.linspace(0, 1, N_PTS)   # [0, 0.25, 0.5, 0.75, 1.0]

all_lats = start_lats[:, None] + t * (end_lats - start_lats)[:, None]
all_lons = start_lons[:, None] + t * (end_lons - start_lons)[:, None]

all_lats += np.random.normal(0, GPS_NOISE, all_lats.shape)
all_lons += np.random.normal(0, GPS_NOISE, all_lons.shape)

# ── Save 200 files ────────────────────────────────────────────────────────────
out_dir = 'trajectories'
os.makedirs(out_dir, exist_ok=True)

t0 = time.time()
for i in range(N_FILES):
    s = i * N_PER_FILE
    e = s + N_PER_FILE

    # Flatten: 1000 trajectories × 5 points = 5000 rows per file
    batch_lats = all_lats[s:e].ravel()
    batch_lons = all_lons[s:e].ravel()

    pd.DataFrame({'lat': batch_lats, 'lon': batch_lons}).to_csv(
        f'{out_dir}/traj_{i+1:03d}.csv', index=False
    )
    if (i + 1) % 40 == 0:
        print(f"  {i+1}/{N_FILES} files saved  ({time.time()-t0:.1f}s)")

print(f"Done – {N_FILES} files, {N_TOTAL} trajectories, "
      f"{N_TOTAL * N_PTS:,} GPS points  ({time.time()-t0:.1f}s total)")
