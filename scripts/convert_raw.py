"""
Convert raw iflytek/amap navigation NDJSON logs to heatmap-ready CSV.

Input:  NDJSON file where each line is one route segment with:
        msg.route_link_info.links[].shape_points[].{lat, lon}

Each line = one segment, which may contain many shape_points across all links.
All points from a segment are collected, then downsampled to MAX_POINTS
evenly-spaced representative points to save space.

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
    """Pick n evenly-spaced points from a list, always including first and last."""
    if len(points) <= n:
        return points
    indices = [round(i * (len(points) - 1) / (n - 1)) for i in range(n)]
    return [points[i] for i in indices]


def convert(input_path, output_path):
    all_points = []
    skipped = 0

    with open(input_path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                links = record['msg']['route_link_info']['links']

                # Collect all shape_points from this segment (one JSON line = one segment)
                segment_pts = []
                for link in links:
                    for pt in link.get('shape_points', []):
                        segment_pts.append((pt['lat'], pt['lon']))

                if segment_pts:
                    all_points.extend(downsample(segment_pts, MAX_POINTS))

            except (json.JSONDecodeError, KeyError) as e:
                skipped += 1
                print(f"  Warning: skipped line {lineno}: {e}")

    if skipped:
        print(f"  Skipped {skipped} malformed lines")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon'])
        writer.writerows(all_points)

    return len(all_points)


if __name__ == '__main__':
    input_path  = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    print(f"Reading:      {input_path}")
    print(f"Max points per segment: {MAX_POINTS}")
    count = convert(input_path, output_path)
    print(f"Output points: {count:,}")
    print(f"Written to:   {output_path}")
