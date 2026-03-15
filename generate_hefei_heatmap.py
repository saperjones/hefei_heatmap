#!/usr/bin/env python3
# 合肥自动驾驶轨迹热力图生成系统 —— 主程序入口

import os
import subprocess
import sys

# 项目根目录（即本文件所在目录）
ROOT = os.path.dirname(os.path.abspath(__file__))
SUB  = os.path.join(ROOT, 'sub_progs')


def run(script, *args):
    """在项目根目录下运行指定子程序"""
    cmd = [sys.executable, os.path.join(SUB, script)] + list(args)
    subprocess.run(cmd, cwd=ROOT)


def print_menu():
    print()
    print("=" * 52)
    print("    合肥自动驾驶轨迹热力图生成系统")
    print("=" * 52)
    print("  数据生成")
    print("  [1] 生成小型模拟数据（100 条轨迹）")
    print("  [2] 生成大型随机模拟数据（20 万条轨迹）")
    print("  [3] 生成路网模拟数据（20 万条，沿合肥高速路网）")
    print()
    print("  数据转换")
    print("  [4] 转换原始导航日志（NDJSON → CSV）")
    print()
    print("  热力图渲染")
    print("  [5] 生成热力图")
    print()
    print("  [0] 退出")
    print("=" * 52)


def main():
    while True:
        print_menu()
        choice = input("请输入选项编号: ").strip()

        if choice == '1':
            # 生成 100 条模拟轨迹，保存为 hefei_mock_trajectory.csv
            print("\n>>> 生成小型模拟数据（100 条轨迹）...")
            run('gen_trajectories.py')

        elif choice == '2':
            # 随机生成 20 万条轨迹，输出到 trajectories/（200 个文件）
            print("\n>>> 生成大型随机模拟数据（20 万条轨迹）...")
            run('gen_200k.py')

        elif choice == '3':
            # 沿 OSM 合肥高速路网生成 20 万条轨迹，首次运行需下载路网数据
            print("\n>>> 生成路网模拟数据（需要 osmnx，首次运行将从 OpenStreetMap 下载路网）...")
            run('gen_highway_200k.py')

        elif choice == '4':
            # 将原始 NDJSON 导航日志转换为热力图可用的 CSV
            print("\n>>> 转换原始导航日志（NDJSON → CSV）")
            inp = input("  输入文件路径（回车使用默认路径）: ").strip()
            out = input("  输出文件路径（回车使用默认路径）: ").strip()
            args = []
            if inp:
                args.append(inp)
            if out:
                args.append(out)
            run('convert_raw.py', *args)

        elif choice == '5':
            # 读取 data/trajectories/ 下所有 CSV，渲染热力图
            print("\n>>> 生成热力图...")
            run('heatmap.py')

        elif choice == '0':
            print("\n再见！")
            break

        else:
            print("\n  无效选项，请重新输入。")
            continue

        input("\n按回车键返回菜单...")


if __name__ == '__main__':
    main()
