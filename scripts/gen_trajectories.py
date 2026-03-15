"""
Generate 100 trajectories around Hefei city center.
Some routes are duplicated to produce varied heat colors.
500 meters ≈ 0.0045° latitude / ~0.005° longitude at this latitude.
"""
import numpy as np
import pandas as pd

np.random.seed(7)

CENTER_LAT, CENTER_LON = 31.8206, 117.2272
OUTPUT = 'hefei_mock_trajectory.csv'
GPS_NOISE = 0.00015   # ~15 m standard deviation

def make_route(lat_start, lon_start, lat_end, lon_end, n_points=80):
    """Interpolate a straight route with GPS noise."""
    lats = np.linspace(lat_start, lat_end, n_points) + np.random.normal(0, GPS_NOISE, n_points)
    lons = np.linspace(lon_start, lon_end, n_points) + np.random.normal(0, GPS_NOISE, n_points)
    return lats, lons

# ── Define unique routes ──────────────────────────────────────────────────────
# Each entry: (lat_start, lon_start, lat_end, lon_end, repeat_count)
# 500 m ≈ 0.0045° lat, so all spans are well above that threshold.

routes = [
    # ── HIGH FREQUENCY – 8-10 passes → red / purple ─────────────────────────
    # R01  East-West trunk road (长江中路 style), 3.6 km
    (31.8206, 117.2000, 31.8206, 117.2400, 10),
    # R02  North-South trunk road (徽州大道 style), 4.5 km
    (31.8000, 117.2272, 31.8400, 117.2272,  9),
    # R03  Diagonal connector, 2.8 km
    (31.8100, 117.2100, 31.8350, 117.2450,  8),
    # R04  Inner ring segment, 2.2 km
    (31.8300, 117.2150, 31.8300, 117.2550,  8),

    # ── MEDIUM FREQUENCY – 4-5 passes → lime / cyan ──────────────────────────
    # R05  Secondary E-W road (north side), 2.0 km
    (31.8350, 117.2100, 31.8350, 117.2480,  5),
    # R06  Secondary E-W road (south side), 2.0 km
    (31.8060, 117.2080, 31.8060, 117.2450,  5),
    # R07  Secondary N-S road (east side), 2.5 km
    (31.8050, 117.2450, 31.8350, 117.2450,  4),
    # R08  Secondary N-S road (west side), 2.5 km
    (31.8050, 117.2100, 31.8350, 117.2100,  4),
    # R09  Short connector near center, 1.2 km
    (31.8206, 117.2272, 31.8310, 117.2390,  4),
    # R10  Diagonal southwest-northeast, 3 km
    (31.8000, 117.2000, 31.8320, 117.2400,  5),

    # ── LOW FREQUENCY – 2-3 passes → cyan / blue ─────────────────────────────
    # R11
    (31.8150, 117.2200, 31.8150, 117.2600,  3),
    # R12
    (31.8400, 117.2200, 31.8400, 117.2600,  3),
    # R13
    (31.8050, 117.2300, 31.8400, 117.2300,  3),
    # R14
    (31.8050, 117.2380, 31.8400, 117.2380,  2),
    # R15
    (31.8180, 117.2050, 31.8180, 117.2500,  2),
    # R16
    (31.8250, 117.2050, 31.8250, 117.2500,  2),
    # R17
    (31.8100, 117.2150, 31.8400, 117.2150,  2),
    # R18
    (31.8100, 117.2350, 31.8380, 117.2200,  2),
    # R19
    (31.8000, 117.2150, 31.8150, 117.2050,  2),
    # R20
    (31.8350, 117.2480, 31.8200, 117.2600,  2),

    # ── SINGLE PASS – 1 pass → blue (sparse) ─────────────────────────────────
    (31.8050, 117.2480, 31.8200, 117.2600,  1),
    (31.8300, 117.2050, 31.8450, 117.2200,  1),
    (31.8420, 117.2300, 31.8420, 117.2600,  1),
    (31.8000, 117.2400, 31.8100, 117.2600,  1),
    (31.8100, 117.2480, 31.8300, 117.2600,  1),
    (31.8000, 117.2050, 31.8100, 117.2150,  1),
    (31.8430, 117.2100, 31.8430, 117.2400,  1),
    (31.8000, 117.2320, 31.8100, 117.2200,  1),
    (31.8380, 117.2480, 31.8480, 117.2300,  1),
    (31.8050, 117.2550, 31.8250, 117.2600,  1),
    (31.8150, 117.2600, 31.8350, 117.2500,  1),
    (31.8460, 117.2400, 31.8460, 117.2600,  1),
    (31.7980, 117.2200, 31.8080, 117.2400,  1),
    (31.8480, 117.2150, 31.8320, 117.2050,  1),
    (31.8120, 117.2600, 31.8420, 117.2580,  1),
]

# ── Accumulate all points ─────────────────────────────────────────────────────
all_lats, all_lons = [], []
total_trajectories = 0

for (ls, lo_s, le, lo_e, repeats) in routes:
    for _ in range(repeats):
        lats, lons = make_route(ls, lo_s, le, lo_e, n_points=80)
        all_lats.extend(lats)
        all_lons.extend(lons)
        total_trajectories += 1

print(f"Total trajectories generated: {total_trajectories}")
assert total_trajectories == 100, f"Expected 100, got {total_trajectories}"

df = pd.DataFrame({'lat': all_lats, 'lon': all_lons})
df = df.sample(frac=1).reset_index(drop=True)
df.to_csv(OUTPUT, index=False)
print(f"Saved {len(df)} GPS points to {OUTPUT}")
