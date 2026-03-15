"""
Convert raw iflytek/amap navigation NDJSON logs to heatmap-ready CSV.

Input:  NDJSON file where each line is a navigation message with:
        msg.route_link_info.links[].shape_points[].{lat, lon}

Output: Single CSV with columns [lat, lon] compatible with heatmap.py
        and the traj_*.csv files used by heatmap_large.py.

Usage:
    python scripts/convert_raw.py <input.txt> [output.csv]

    Defaults:
        input  — raw_format/iflytek_ehr_amap_navi_info.txt
        output — data/converted_trajectory.csv
"""

import json
import csv
import sys
import os

DEFAULT_INPUT  = os.path.join(os.path.dirname(__file__), '..', 'raw_format', 'iflytek_ehr_amap_navi_info.txt')
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'converted_trajectory.csv')

def extract_points(input_path):
    points = []
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
                        points.append((pt['lat'], pt['lon']))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"  Warning: skipped line {lineno}: {e}")
    return points

def write_csv(points, output_path):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon'])
        writer.writerows(points)

if __name__ == '__main__':
    input_path  = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    print(f"Reading: {input_path}")
    points = extract_points(input_path)
    print(f"  Extracted {len(points):,} GPS points")

    print(f"Writing: {output_path}")
    write_csv(points, output_path)
    print(f"Done. Run heatmap with:")
    print(f"  python heatmap.py  (after setting DATA_PATH = '{output_path}')")
