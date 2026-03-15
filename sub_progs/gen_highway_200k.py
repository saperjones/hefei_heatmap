"""
Generate 200,000 trajectories following Hefei motorway/trunk road network.
- Road data fetched from OpenStreetMap (cached to hefei_graph.graphml)
- Each trajectory: 5 GPS points, 300–1000 m, following actual road geometry
- Distributed proportionally to road length
- 1,000 trajectories per file → 200 files in ./trajectories/
"""
import osmnx as ox
import numpy as np
import pandas as pd
import os, time

np.random.seed(42)
rng = np.random.default_rng(42)

N_TOTAL    = 200_000
N_PER_FILE = 1_000
N_FILES    = N_TOTAL // N_PER_FILE
N_PTS      = 5
GPS_NOISE  = 0.00010   # ~10 m std dev
MIN_LEN    = 300.0     # metres
MAX_LEN    = 1000.0

LAT_PER_M  = 1.0 / 111_320.0

# ── 1. Load or download graph ─────────────────────────────────────────────────
CACHE = 'hefei_graph.graphml'
t0 = time.time()

if os.path.exists(CACHE):
    print(f"Loading cached graph from {CACHE}...")
    G = ox.load_graphml(CACHE)
else:
    print("Downloading Hefei motorway/trunk network from OpenStreetMap...")
    G = ox.graph_from_place(
        "Hefei, Anhui, China",
        custom_filter='["highway"~"motorway|motorway_link|trunk|trunk_link"]',
        retain_all=False,
    )
    ox.save_graphml(G, CACHE)
    print(f"  Saved to {CACHE}")

print(f"  Graph ready ({time.time()-t0:.1f}s) — "
      f"{len(G.nodes)} nodes, {len(G.edges)} edges")

# ── 2. Build edge data using WGS84 only (avoids UTM coord-count mismatch) ────
print("Building edge data...")
edges_gdf = ox.graph_to_gdfs(G, nodes=False).reset_index()

edge_data = []

for i in range(len(edges_gdf)):
    geom = edges_gdf.iloc[i]['geometry']
    if geom is None or geom.is_empty:
        edge_data.append(None)
        continue

    coords = np.array(geom.coords)          # (k, 2) = lon, lat  — WGS84 only
    diffs  = np.diff(coords, axis=0)        # (k-1, 2)

    # Approximate arc-length in metres using equirectangular projection
    mid_lat = np.radians(coords[:-1, 1])
    dlat_m  = diffs[:, 1] * 111_320.0
    dlon_m  = diffs[:, 0] * 111_320.0 * np.cos(mid_lat)
    seg_lens = np.sqrt(dlat_m ** 2 + dlon_m ** 2)

    cum_lens  = np.concatenate([[0.0], np.cumsum(seg_lens)])
    total_len = float(cum_lens[-1])

    edge_data.append({
        'coords':    coords,        # (k, 2) lon/lat
        'diffs':     diffs,         # (k-1, 2)
        'cum_lens':  cum_lens,      # (k,)
        'seg_lens':  seg_lens,      # (k-1,)
        'total_len': total_len,
        'v':         int(edges_gdf.iloc[i]['v']),
    })

# ── 3. Build adjacency (end node → outgoing edge indices) ────────────────────
adjacency = {}
for idx, ed in enumerate(edge_data):
    if ed is None:
        continue
    adjacency.setdefault(ed['v'], []).append(idx)

# Eligible start edges
start_indices = [i for i, ed in enumerate(edge_data)
                 if ed is not None and ed['total_len'] >= MIN_LEN]
start_lengths = np.array([edge_data[i]['total_len'] for i in start_indices])
start_weights = start_lengths / start_lengths.sum()

print(f"  {len(edge_data)} edges | {len(start_indices)} start-eligible "
      f"| {start_lengths.sum()/1000:.0f} km eligible road")

# ── 4. Fast point sampling on an edge ────────────────────────────────────────
def point_at_dist(ed, d):
    d   = float(np.clip(d, 0.0, ed['total_len']))
    idx = int(np.searchsorted(ed['cum_lens'], d, side='right')) - 1
    idx = int(np.clip(idx, 0, len(ed['seg_lens']) - 1))   # clamp to valid range
    sl  = ed['seg_lens'][idx]
    t   = float(np.clip((d - ed['cum_lens'][idx]) / sl, 0.0, 1.0)) if sl > 0 else 0.0
    return ed['coords'][idx] + t * ed['diffs'][idx]       # (2,) = lon, lat

# ── 5. Generate 200k trajectories ────────────────────────────────────────────
print("Generating trajectories...")
all_lats = np.empty(N_TOTAL * N_PTS, dtype=np.float64)
all_lons = np.empty(N_TOTAL * N_PTS, dtype=np.float64)

chosen_start = np.random.choice(len(start_indices), N_TOTAL, p=start_weights)
traj_lengths = np.random.uniform(MIN_LEN, MAX_LEN, N_TOTAL)

for i in range(N_TOTAL):
    tlen     = traj_lengths[i]
    curr_idx = start_indices[chosen_start[i]]
    ed       = edge_data[curr_idx]

    max_start = max(0.0, ed['total_len'] - tlen)
    curr_pos  = rng.uniform(0.0, max_start) if max_start > 0 else 0.0

    # Walk network, accumulating segments
    segments  = []
    remaining = tlen

    while remaining > 0.5:
        ed    = edge_data[curr_idx]
        avail = ed['total_len'] - curr_pos

        if avail >= remaining:
            segments.append((curr_idx, curr_pos, curr_pos + remaining))
            remaining = 0.0
        else:
            if avail > 0.1:
                segments.append((curr_idx, curr_pos, ed['total_len']))
                remaining -= avail
            nexts = adjacency.get(ed['v'], [])
            if not nexts:
                break
            curr_idx = nexts[int(rng.integers(len(nexts)))]
            curr_pos = 0.0

    if not segments:
        ei = start_indices[chosen_start[i]]
        segments = [(ei, 0.0, edge_data[ei]['total_len'])]

    # Sample 5 evenly-spaced points
    total_cov = sum(e - s for _, s, e in segments)
    if total_cov <= 0:
        total_cov = 1.0

    pts = []
    cum, si = 0.0, 0
    for sd in np.linspace(0.0, total_cov, N_PTS):
        while si < len(segments) - 1 and cum + (segments[si][2] - segments[si][1]) < sd:
            cum += segments[si][2] - segments[si][1]
            si  += 1
        eidx, seg_s, _ = segments[si]
        pts.append(point_at_dist(edge_data[eidx], seg_s + (sd - cum)))

    pts = np.array(pts)   # (5, 2) = lon, lat
    base = i * N_PTS
    all_lons[base:base+N_PTS] = pts[:, 0] + rng.normal(0, GPS_NOISE, N_PTS)
    all_lats[base:base+N_PTS] = pts[:, 1] + rng.normal(0, GPS_NOISE, N_PTS)

    if (i + 1) % 25_000 == 0:
        print(f"  {i+1:,}/{N_TOTAL:,}  ({time.time()-t0:.0f}s)")

print(f"  Generation complete  ({time.time()-t0:.1f}s)")

# ── 6. Save 200 CSV files ─────────────────────────────────────────────────────
print("Saving trajectory files...")
out_dir = 'trajectories'
os.makedirs(out_dir, exist_ok=True)

for i in range(N_FILES):
    s = i * N_PER_FILE * N_PTS
    e = s + N_PER_FILE * N_PTS
    pd.DataFrame({'lat': all_lats[s:e], 'lon': all_lons[s:e]}).to_csv(
        f'{out_dir}/traj_{i+1:03d}.csv', index=False
    )
    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{N_FILES} files saved")

print(f"\nDone — {N_FILES} files | {N_TOTAL:,} trajectories | "
      f"{N_TOTAL*N_PTS:,} GPS points  ({time.time()-t0:.1f}s total)")
