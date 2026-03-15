import pandas as pd
import folium
from folium.plugins import HeatMap
import numpy as np
import os

# ================= 配置区 =================
DATA_PATH = 'data/hefei_mock_trajectory.csv'
OUTPUT_FILE = 'output/Hefei_Trajectory_Heatmap.html'
CENTER_LAT, CENTER_LON = 31.8206, 117.2272 # 合肥市中心坐标 (WGS84)

# ================= 0. 模拟数据生成器 =================
def generate_sample_data(file_path):
    print("正在生成合肥市街道的模拟轨迹数据...")
    
    # 设定随机种子以保证每次生成的轨迹一致
    np.random.seed(42)
    
    # 模拟路线 1：东西向主干道（类似长江中路），密集采集
    # 经度跨度，纬度基本不变但加入正态分布的 GPS 误差（约 15-20 米偏移）
    lons1 = np.linspace(117.2000, 117.2500, 800)
    lats1 = np.full(800, 31.8206) + np.random.normal(0, 0.00015, 800)
    
    # 模拟路线 2：南北向主干道（类似徽州大道），中等密度采集
    lats2 = np.linspace(31.8000, 31.8400, 600)
    lons2 = np.full(600, 117.2272) + np.random.normal(0, 0.00015, 600)
    
    # 模拟区域 3：两条路交汇处的极高密度采集区（例如反复绕行的路口或停车场）
    lats3 = np.random.normal(31.8206, 0.0004, 400)
    lons3 = np.random.normal(117.2272, 0.0004, 400)
    
    # 合并数据
    lats = np.concatenate([lats1, lats2, lats3])
    lons = np.concatenate([lons1, lons2, lons3])
    
    # 创建 DataFrame 并保存为 CSV
    df = pd.DataFrame({'lat': lats, 'lon': lons})
    
    # 随机打乱数据顺序，模拟真实的时间乱序流
    df = df.sample(frac=1).reset_index(drop=True)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
    print(f"模拟数据已成功生成并保存至: {file_path}，共 {len(df)} 个点位。")

# ================= 1. 数据读取与处理 =================
def process_gps_data(file_path):
    print("正在加载数据并进行误差降噪聚合...")
    df = pd.read_csv(file_path)
    
    # a. 自动去重与缺失值处理
    df = df.dropna(subset=['lat', 'lon']).drop_duplicates()
    
    # b. 轨迹平滑与聚合准备 (保留4位小数，约11米精度，将误差散点归算到同一网格)
    df['lat_round'] = df['lat'].round(4)
    df['lon_round'] = df['lon'].round(4)
    
    # c. 统计每个微小区域的采集频次（权重）
    heatmap_data = df.groupby(['lat_round', 'lon_round']).size().reset_index(name='weight')
    
    # d. 标准化权重至 0-1 之间
    max_weight = heatmap_data['weight'].max()
    heatmap_data['weight_norm'] = heatmap_data['weight'] / max_weight
    
    return heatmap_data[['lat_round', 'lon_round', 'weight_norm']].values.tolist()

# ================= 2. 可视化渲染 =================
def generate_heatmap(data_points):
    print("正在生成可交互热力图...")
    
    # 创建底图 (CartoDB Positron 浅色底图)
    m = folium.Map(
        location=[CENTER_LAT, CENTER_LON],
        zoom_start=14, # 调大初始缩放级别以便看清街道
        tiles='CartoDB positron',
        control_scale=True
    )
    
    # 定义颜色梯度：冷色(蓝) -> 暖色(红) -> 极高密度(紫)
    color_gradient = {
        0.2: 'blue',   
        0.4: 'cyan',   
        0.6: 'lime',   
        0.8: 'red',    
        1.0: 'purple'  
    }
    
    # 叠加热力图层
    HeatMap(
        data_points,
        radius=12,         
        blur=8,            
        gradient=color_gradient,
        min_opacity=0.2,   
        max_zoom=16
    ).add_to(m)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    m.save(OUTPUT_FILE)
    print(f"热力图渲染完成！请用浏览器打开当前目录下的 '{OUTPUT_FILE}' 查看效果。")

# ================= 主程序执行 =================
if __name__ == "__main__":
    # 1. 检查是否存在数据文件，如果不存在则自动生成合肥的模拟数据
    if not os.path.exists(DATA_PATH):
        generate_sample_data(DATA_PATH)
    
    # 2. 处理数据
    points = process_gps_data(DATA_PATH)
    
    # 3. 生成并保存热力图
    generate_heatmap(points)