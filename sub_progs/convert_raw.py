"""
Convert raw iflytek/amap navigation NDJSON logs to heatmap-ready CSV.

Input:  One NDJSON file = one driving segment.
        All lines together describe the same route via repeated nav updates.
        Each line: msg.route_link_info.links[].shape_points[].{lat, lon}

Processing:
        1. Collect all shape_points from all lines in the file
        2. Deduplicate
        3. Downsample to MAX_POINTS evenly-spaced representative points

Output: data/converted_trajectory.csv with columns [lat, lon],
        compatible with heatmap.py and heatmap_large.py.

Usage:
    python scripts/convert_raw.py [input.txt] [output.csv]

    Defaults:
        input  — raw_format/iflytek_ehr_amap_navi_info.txt
        output — data/converted_trajectory.csv
"""

import json
import csv
import sys
import os

MAX_POINTS = 5

DEFAULT_INPUT  = os.path.join(os.path.dirname(__file__), '..', 'raw_format', 'iflytek_ehr_amap_navi_info.txt')
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'converted_trajectory.csv')


def downsample(points, n):
    """Pick n evenly-spaced points, always including first and last."""
    if len(points) <= n:
        return points
    indices = [round(i * (len(points) - 1) / (n - 1)) for i in range(n)]
    return [points[i] for i in indices]


def convert(input_path, output_path):
    # Collect all shape_points from the entire file (= one segment)
    seen = set()
    all_points = []

    with open(input_path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                links = record['msg']['route_link_info']['links']
                for link in links:
                    for pt in link.get('shape_points', []):
                        key = (pt['lat'], pt['lon'])
                        if key not in seen:
                            seen.add(key)
                            all_points.append(key)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"  Warning: skipped line {lineno}: {e}")

    print(f"  Unique points in segment: {len(all_points):,}")

    representative = downsample(all_points, MAX_POINTS)
    print(f"  Downsampled to: {len(representative)} points")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon'])
        writer.writerows(representative)

    return representative


if __name__ == '__main__':
    input_path  = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    print(f"Reading:  {input_path}")
    pts = convert(input_path, output_path)
    print(f"Written:  {output_path}")
    print(f"Points:   {pts}")
