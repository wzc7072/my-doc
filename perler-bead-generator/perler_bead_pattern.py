#!/usr/bin/env python3
"""
拼豆图案生成器 (Perler Bead Pattern Generator)

将真实照片（如猫咪照片）扁平化处理，然后转换为拼豆图案。
输出为 HTML 网格，包含颜色代码、行列编号和豆子统计信息。

用法:
    python perler_bead_pattern.py <input_image> [--width 29] [--height 46] [--output output.html]
"""

import argparse
import math
import os
import sys
from collections import Counter

from PIL import Image, ImageFilter, ImageEnhance

# ============================================================
# 拼豆颜色表 (Perler Bead Color Palette)
# 格式: code -> (R, G, B, 中文名, 英文名, CSS显示色, 文字颜色)
# 扩展调色板，覆盖更多中间色调以提高还原精度
# ============================================================
BEAD_PALETTE = {
    # 白/灰/黑 系列
    "C3": (255, 255, 255, "白色", "White", "#FFFFFF", "#333333"),
    "C5": (255, 245, 220, "奶白", "Cream", "#FFF5DC", "#333333"),
    "H3": (200, 200, 200, "浅灰", "Light Grey", "#C8C8C8", "#333333"),
    "H5": (160, 160, 160, "中灰", "Medium Grey", "#A0A0A0", "#333333"),
    "H8": (80, 80, 80, "深灰", "Dark Grey", "#505050", "#FFFFFF"),
    "H7": (30, 30, 30, "黑色", "Black", "#1E1E1E", "#FFFFFF"),
    # 肤色/米色 系列
    "H1": (245, 228, 200, "肤色/米色", "Flesh/Beige", "#F5E4C8", "#333333"),
    "H2": (235, 215, 185, "深肤色", "Sand", "#EBD7B9", "#333333"),
    # 棕色 系列 (丰富梯度)
    "E8": (220, 195, 162, "浅棕", "Light Brown", "#DCC3A2", "#333333"),
    "E1": (210, 170, 130, "棕色", "Brown", "#D2AA82", "#333333"),
    "E3": (180, 140, 100, "中棕", "Medium Brown", "#B48C64", "#333333"),
    "E4": (150, 110, 75, "深中棕", "Tan", "#966E4B", "#FFFFFF"),
    "E5": (120, 80, 50, "深棕", "Dark Brown", "#785032", "#FFFFFF"),
    "E6": (90, 55, 35, "巧克力", "Chocolate", "#5A3723", "#FFFFFF"),
    # 黄色 系列
    "A1": (255, 240, 100, "浅黄", "Light Yellow", "#FFF064", "#333333"),
    "A3": (255, 255, 130, "黄色", "Yellow", "#FFFF82", "#333333"),
    "A4": (240, 220, 80, "深黄", "Dark Yellow", "#F0DC50", "#333333"),
    # 橙色 系列
    "D1": (255, 165, 80, "橙色", "Orange", "#FFA550", "#333333"),
    "D2": (230, 140, 60, "深橙", "Dark Orange", "#E68C3C", "#333333"),
    # 粉/红 系列
    "E2": (255, 182, 193, "粉色", "Pink", "#FFB6C1", "#333333"),
    "C1": (255, 100, 100, "红色", "Red", "#FF6464", "#FFFFFF"),
    "C2": (200, 60, 60, "深红", "Dark Red", "#C83C3C", "#FFFFFF"),
    # 蓝/灰蓝 系列
    "H18": (140, 160, 180, "灰蓝", "Grey Blue", "#8CA0B4", "#333333"),
    "H19": (110, 130, 155, "深灰蓝", "Dark Grey Blue", "#6E829B", "#FFFFFF"),
    "B1": (100, 180, 255, "蓝色", "Blue", "#64B4FF", "#333333"),
    "B2": (70, 130, 200, "深蓝", "Dark Blue", "#4682C8", "#FFFFFF"),
    # 绿色 系列
    "G1": (100, 200, 100, "绿色", "Green", "#64C864", "#333333"),
    "G2": (60, 140, 60, "深绿", "Dark Green", "#3C8C3C", "#FFFFFF"),
    # 紫色 系列
    "F1": (180, 130, 200, "紫色", "Purple", "#B482C8", "#333333"),
    # 暖灰/灰棕 (照片中常见的中间色)
    "H10": (180, 170, 155, "暖灰", "Warm Grey", "#B4AA9B", "#333333"),
    "H11": (155, 145, 130, "中暖灰", "Med Warm Grey", "#9B9182", "#333333"),
    "H12": (130, 120, 105, "深暖灰", "Dark Warm Grey", "#827869", "#FFFFFF"),
}


# ============================================================
# CIELAB 色彩空间转换与感知色差计算
# ============================================================

def _srgb_to_linear(c):
    """sRGB 分量 [0,255] → 线性 [0,1]"""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lab_f(t):
    """CIE Lab 转换辅助函数"""
    delta = 6.0 / 29.0
    if t > delta ** 3:
        return t ** (1.0 / 3.0)
    return t / (3 * delta * delta) + 4.0 / 29.0


def rgb_to_lab(r, g, b):
    """将 sRGB (0-255) 转换为 CIELAB (L*, a*, b*)"""
    # sRGB → linear RGB
    rl = _srgb_to_linear(r)
    gl = _srgb_to_linear(g)
    bl = _srgb_to_linear(b)
    # linear RGB → XYZ (D65 illuminant)
    x = 0.4124564 * rl + 0.3575761 * gl + 0.1804375 * bl
    y = 0.2126729 * rl + 0.7151522 * gl + 0.0721750 * bl
    z = 0.0193339 * rl + 0.1191920 * gl + 0.9503041 * bl
    # D65 white point
    xn, yn, zn = 0.95047, 1.00000, 1.08883
    fx = _lab_f(x / xn)
    fy = _lab_f(y / yn)
    fz = _lab_f(z / zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return L, a, b_val


def ciede2000(lab1, lab2):
    """
    CIEDE2000 色差公式 — 目前最准确的感知色差度量。
    简化实现，足够用于拼豆颜色匹配。
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    # 加权因子
    kL, kC, kH = 1.0, 1.0, 1.0

    C1 = math.sqrt(a1 * a1 + b1 * b1)
    C2 = math.sqrt(a2 * a2 + b2 * b2)
    C_avg = (C1 + C2) / 2.0

    C_avg7 = C_avg ** 7
    G = 0.5 * (1.0 - math.sqrt(C_avg7 / (C_avg7 + 25.0 ** 7)))

    a1p = a1 * (1.0 + G)
    a2p = a2 * (1.0 + G)

    C1p = math.sqrt(a1p * a1p + b1 * b1)
    C2p = math.sqrt(a2p * a2p + b2 * b2)

    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360

    dLp = L2 - L1
    dCp = C2p - C1p

    if C1p * C2p == 0:
        dhp = 0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360
    else:
        dhp = h2p - h1p + 360

    dHp = 2.0 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2.0))

    Lp_avg = (L1 + L2) / 2.0
    Cp_avg = (C1p + C2p) / 2.0

    if C1p * C2p == 0:
        hp_avg = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hp_avg = (h1p + h2p) / 2.0
    elif h1p + h2p < 360:
        hp_avg = (h1p + h2p + 360) / 2.0
    else:
        hp_avg = (h1p + h2p - 360) / 2.0

    T = (1.0
         - 0.17 * math.cos(math.radians(hp_avg - 30))
         + 0.24 * math.cos(math.radians(2 * hp_avg))
         + 0.32 * math.cos(math.radians(3 * hp_avg + 6))
         - 0.20 * math.cos(math.radians(4 * hp_avg - 63)))

    SL = 1.0 + 0.015 * (Lp_avg - 50) ** 2 / math.sqrt(20 + (Lp_avg - 50) ** 2)
    SC = 1.0 + 0.045 * Cp_avg
    SH = 1.0 + 0.015 * Cp_avg * T

    Cp_avg7 = Cp_avg ** 7
    RT = (-2.0 * math.sqrt(Cp_avg7 / (Cp_avg7 + 25.0 ** 7))
          * math.sin(math.radians(60.0 * math.exp(-((hp_avg - 275) / 25.0) ** 2))))

    dE = math.sqrt(
        (dLp / (kL * SL)) ** 2
        + (dCp / (kC * SC)) ** 2
        + (dHp / (kH * SH)) ** 2
        + RT * (dCp / (kC * SC)) * (dHp / (kH * SH))
    )
    return dE


# 预计算调色板的 Lab 值缓存
_palette_lab_cache = {}


def _get_palette_lab(palette):
    """获取或计算调色板的 Lab 值缓存"""
    cache_id = id(palette)
    if cache_id not in _palette_lab_cache:
        lab_map = {}
        for code, (r, g, b, *_) in palette.items():
            lab_map[code] = rgb_to_lab(r, g, b)
        _palette_lab_cache[cache_id] = lab_map
    return _palette_lab_cache[cache_id]


def find_nearest_bead(pixel_color, palette):
    """使用 CIEDE2000 在 CIELAB 空间中找到最接近的拼豆颜色"""
    lab_map = _get_palette_lab(palette)
    pixel_lab = rgb_to_lab(*pixel_color[:3])
    min_dist = float("inf")
    best_code = "C3"
    for code, bead_lab in lab_map.items():
        dist = ciede2000(pixel_lab, bead_lab)
        if dist < min_dist:
            min_dist = dist
            best_code = code
    return best_code


def flatten_image(img, smooth_level=1):
    """
    轻度扁平化处理：仅做最小程度的平滑，保留尽可能多的细节。
    smooth_level: 0=无平滑, 1=轻微, 2=中等, 3=强
    """
    img = img.convert("RGB")

    if smooth_level >= 3:
        img = img.filter(ImageFilter.SMOOTH_MORE)
    elif smooth_level == 2:
        img = img.filter(ImageFilter.SMOOTH)
    elif smooth_level == 1:
        # 最轻微的模糊 — 3x3 高斯近似核，仅去除极细噪点
        img = img.filter(ImageFilter.Kernel(
            size=(3, 3),
            kernel=[1, 2, 1, 2, 4, 2, 1, 2, 1],
            scale=16,
            offset=0,
        ))

    # 轻微提升对比度帮助区分颜色区域
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)

    return img


# Floyd-Steinberg 误差扩散权重: (dx, dy, weight)
_FS_OFFSETS = [(1, 0, 7/16), (-1, 1, 3/16), (0, 1, 5/16), (1, 1, 1/16)]


def image_to_bead_grid(image_path, grid_width=29, grid_height=46,
                       palette=None, dither=True, smooth_level=1):
    """
    将图片转换为拼豆网格 — 高精度版本

    处理流程（优化后的顺序）:
    1. 打开原图 → 2. 缩放到网格大小 → 3. 轻微平滑
    → 4. 逐像素映射到最近拼豆色（可选 Floyd-Steinberg 抖动）

    Args:
        image_path: 输入图片路径
        grid_width: 网格宽度（列数）
        grid_height: 网格高度（行数）
        palette: 拼豆颜色表
        dither: 是否使用 Floyd-Steinberg 抖动来提高视觉精度
        smooth_level: 平滑程度 (0-3)

    Returns:
        grid: 二维列表，每个元素是拼豆颜色代码
        bead_counts: 各颜色的使用数量
    """
    if palette is None:
        palette = BEAD_PALETTE

    img = Image.open(image_path)
    img = img.convert("RGB")

    # 先缩放到目标网格大小 — 使用高质量 LANCZOS 重采样
    # 保留缩放时的全部颜色信息，不做预量化
    img = img.resize((grid_width, grid_height), Image.Resampling.LANCZOS)

    # 轻度扁平化（仅去噪，不做色彩量化）
    img = flatten_image(img, smooth_level=smooth_level)

    # 获取像素数据为可修改的浮点数组（用于抖动误差扩散）
    pixels = []
    for y in range(grid_height):
        row = []
        for x in range(grid_width):
            r, g, b = img.getpixel((x, y))[:3]
            row.append([float(r), float(g), float(b)])
        pixels.append(row)

    # 逐像素映射 + 可选 Floyd-Steinberg 抖动
    grid = []
    bead_counts = Counter()

    for y in range(grid_height):
        row = []
        for x in range(grid_width):
            # 当前像素（可能含扩散误差）
            pr = max(0, min(255, pixels[y][x][0]))
            pg = max(0, min(255, pixels[y][x][1]))
            pb = max(0, min(255, pixels[y][x][2]))
            old_pixel = (int(round(pr)), int(round(pg)), int(round(pb)))

            # 找到最近的拼豆颜色
            bead_code = find_nearest_bead(old_pixel, palette)
            row.append(bead_code)
            bead_counts[bead_code] += 1

            if dither:
                # 计算量化误差
                new_r, new_g, new_b = palette[bead_code][:3]
                err_r = pr - new_r
                err_g = pg - new_g
                err_b = pb - new_b

                # Floyd-Steinberg 扩散到邻近像素
                for dx, dy, weight in _FS_OFFSETS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < grid_width and 0 <= ny < grid_height:
                        pixels[ny][nx][0] += err_r * weight
                        pixels[ny][nx][1] += err_g * weight
                        pixels[ny][nx][2] += err_b * weight

        grid.append(row)

    return grid, bead_counts


def detect_background(grid, margin=2):
    """
    检测并标记背景区域（图案边缘的空白区域）
    返回一个与 grid 同样大小的 mask，True 表示是背景
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    # 找出最常出现在边缘的颜色作为背景色
    edge_colors = Counter()
    for y in range(height):
        for x in range(width):
            if x < margin or x >= width - margin or y < margin or y >= height - margin:
                edge_colors[grid[y][x]] += 1

    if not edge_colors:
        return [[False] * width for _ in range(height)]

    bg_color = edge_colors.most_common(1)[0][0]

    # 从边缘进行洪水填充，标记连续的背景区域
    mask = [[False] * width for _ in range(height)]
    visited = [[False] * width for _ in range(height)]

    stack = []
    # 从所有边缘点开始
    for y in range(height):
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                if grid[y][x] == bg_color:
                    stack.append((x, y))

    while stack:
        x, y = stack.pop()
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if visited[y][x]:
            continue
        visited[y][x] = True
        if grid[y][x] == bg_color:
            mask[y][x] = True
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    return mask


def generate_html(grid, bead_counts, title="豆画", palette=None, show_background=True):
    """生成 HTML 格式的拼豆图案"""
    if palette is None:
        palette = BEAD_PALETTE

    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    total_beads = sum(bead_counts.values())

    # 检测背景
    bg_mask = detect_background(grid) if not show_background else None

    # 如果不显示背景，重新计算数量
    if bg_mask:
        bead_counts = Counter()
        for y in range(height):
            for x in range(width):
                if not bg_mask[y][x]:
                    bead_counts[grid[y][x]] += 1
        total_beads = sum(bead_counts.values())

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐱 {title}</title>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}
body {{
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    background: #f5f5f5;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}}
h1 {{
    font-size: 24px;
    margin-bottom: 10px;
    color: #333;
}}
.subtitle {{
    color: #666;
    margin-bottom: 20px;
    font-size: 14px;
}}
.grid-container {{
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 15px;
    overflow-x: auto;
    margin-bottom: 20px;
}}
table {{
    border-collapse: collapse;
    font-size: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
}}
td {{
    width: 28px;
    height: 22px;
    text-align: center;
    vertical-align: middle;
    border: 1px solid #ddd;
    font-weight: bold;
    font-size: 9px;
    white-space: nowrap;
}}
td.empty {{
    background: #FAFAFA;
    border-color: #eee;
    color: transparent;
}}
td.row-num {{
    background: #f8f8f8;
    color: #999;
    font-weight: normal;
    border: 1px solid #eee;
    width: 24px;
    font-size: 10px;
}}
td.col-num {{
    background: #f8f8f8;
    color: #999;
    font-weight: normal;
    border: 1px solid #eee;
    height: 20px;
    font-size: 10px;
}}
.legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
    margin-top: 15px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}
.legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 13px;
}}
.legend-color {{
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid #ddd;
    display: inline-block;
}}
.legend-text {{
    font-weight: bold;
}}
.legend-count {{
    color: #888;
    font-size: 12px;
}}
.preview-container {{
    margin-bottom: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 15px;
}}
.preview-container h3 {{
    text-align: center;
    margin-bottom: 10px;
    color: #555;
}}
.preview-grid {{
    display: grid;
    grid-template-columns: repeat({width}, 12px);
    gap: 1px;
}}
.preview-cell {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
}}
</style>
</head>
<body>
<h1>🐱 {title} ({total_beads})</h1>
<p class="subtitle">{width} × {height} 网格 | 共 {len(bead_counts)} 种颜色</p>

<!-- 缩略预览 -->
<div class="preview-container">
<h3>效果预览</h3>
<div class="preview-grid">
"""

    # 生成缩略预览（圆点版）
    for y in range(height):
        for x in range(width):
            code = grid[y][x]
            is_bg = bg_mask[y][x] if bg_mask else False
            if is_bg:
                html += f'<div class="preview-cell" style="background:#f5f5f5;"></div>\n'
            else:
                css_color = palette[code][5] if code in palette else "#CCC"
                html += f'<div class="preview-cell" style="background:{css_color};"></div>\n'

    html += """</div>
</div>

<!-- 详细网格 -->
<div class="grid-container">
<table>
"""

    # 列号头部
    html += "<tr><td class='col-num'></td>"
    for x in range(1, width + 1):
        html += f"<td class='col-num'>{x}</td>"
    html += "<td class='col-num'></td></tr>\n"

    # 网格数据
    for y in range(height):
        html += f"<tr><td class='row-num'>{y + 1}</td>"
        for x in range(width):
            code = grid[y][x]
            is_bg = bg_mask[y][x] if bg_mask else False
            if is_bg:
                html += "<td class='empty'>&nbsp;</td>"
            else:
                if code in palette:
                    css_color = palette[code][5]
                    text_color = palette[code][6]
                else:
                    css_color = "#CCC"
                    text_color = "#333"
                html += f"<td style='background:{css_color};color:{text_color};'>{code}</td>"
        html += f"<td class='row-num'>{y + 1}</td></tr>\n"

    # 列号底部
    html += "<tr><td class='col-num'></td>"
    for x in range(1, width + 1):
        html += f"<td class='col-num'>{x}</td>"
    html += "<td class='col-num'></td></tr>\n"

    html += "</table>\n</div>\n"

    # 图例
    html += '<div class="legend">\n'
    for code, count in sorted(bead_counts.items(), key=lambda x: -x[1]):
        if code in palette:
            css_color = palette[code][5]
            cn_name = palette[code][3]
        else:
            css_color = "#CCC"
            cn_name = "未知"
        html += f"""<div class="legend-item">
    <span class="legend-color" style="background:{css_color};"></span>
    <span class="legend-text">{code}</span>
    <span class="legend-count">({count}) {cn_name}</span>
</div>\n"""

    html += """</div>
</body>
</html>"""

    return html


def generate_sample_cat():
    """生成一个示例猫咪图片用于测试"""
    import numpy as np

    width, height = 290, 460
    img = Image.new("RGB", (width, height), (200, 220, 240))
    pixels = np.array(img, dtype=np.int32)

    # 画一个简单的猫脸
    cy, cx = height // 2, width // 2

    for y in range(height):
        for x in range(width):
            dx = x - cx
            dy = y - cy

            # 身体 - 椭圆形
            if (dx / 110) ** 2 + (dy / 160) ** 2 < 1:
                pixels[y, x] = (240, 210, 170)  # 橘色猫

            # 脸部 - 圆形
            if (dx / 90) ** 2 + ((dy + 40) / 80) ** 2 < 1:
                pixels[y, x] = (245, 220, 180)

            # 耳朵 - 左
            ear_lx, ear_ly = cx - 65, cy - 140
            edx, edy = x - ear_lx, y - ear_ly
            if edy < 0 and abs(edx) < 35 + edy * 0.5 and edy > -60:
                pixels[y, x] = (230, 190, 140)

            # 耳朵 - 右
            ear_rx, ear_ry = cx + 65, cy - 140
            edx, edy = x - ear_rx, y - ear_ry
            if edy < 0 and abs(edx) < 35 + edy * 0.5 and edy > -60:
                pixels[y, x] = (230, 190, 140)

            # 眼睛 - 左
            eye_lx, eye_ly = cx - 30, cy - 30
            if (x - eye_lx) ** 2 + (y - eye_ly) ** 2 < 12 ** 2:
                pixels[y, x] = (30, 30, 30)

            # 眼睛 - 右
            eye_rx, eye_ry = cx + 30, cy - 30
            if (x - eye_rx) ** 2 + (y - eye_ry) ** 2 < 12 ** 2:
                pixels[y, x] = (30, 30, 30)

            # 鼻子
            nose_x, nose_y = cx, cy + 5
            if (x - nose_x) ** 2 + (y - nose_y) ** 2 < 6 ** 2:
                pixels[y, x] = (255, 150, 160)

            # 条纹 (虎斑)
            stripe_check = False
            for sy_offset in [-80, -50, -20, 10, 40, 70, 100]:
                sy = cy + sy_offset
                if abs(y - sy) < 8 and (dx / 110) ** 2 + ((y - cy) / 160) ** 2 < 0.85:
                    if (x % 40 < 20):
                        stripe_check = True

            if stripe_check and (dx / 110) ** 2 + (dy / 160) ** 2 < 0.9:
                r, g, b = pixels[y, x]
                pixels[y, x] = (max(0, r - 50), max(0, g - 50), max(0, b - 40))

    pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    return img


def main():
    parser = argparse.ArgumentParser(
        description="🐱 拼豆图案生成器 - 将照片转换为拼豆（Perler Bead）图案"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="输入图片路径（如果不提供，将使用内置示例猫咪）",
    )
    parser.add_argument(
        "--width", "-W", type=int, default=29, help="网格宽度/列数 (默认: 29)"
    )
    parser.add_argument(
        "--height", "-H", type=int, default=46, help="网格高度/行数 (默认: 46)"
    )
    parser.add_argument(
        "--output", "-o", default="bead_pattern.html", help="输出 HTML 文件路径"
    )
    parser.add_argument(
        "--title", "-t", default="豆画/Cat", help="图案标题"
    )
    parser.add_argument(
        "--show-bg",
        action="store_true",
        default=False,
        help="显示背景区域（默认隐藏）",
    )
    parser.add_argument(
        "--no-dither",
        action="store_true",
        default=False,
        help="禁用 Floyd-Steinberg 抖动（默认启用抖动以提高精度）",
    )
    parser.add_argument(
        "--smooth", "-s",
        type=int,
        default=1,
        choices=[0, 1, 2, 3],
        help="平滑程度: 0=无, 1=轻微(默认), 2=中等, 3=强",
    )

    args = parser.parse_args()

    # 如果没有提供输入图片，生成示例
    if args.input is None:
        print("📷 未提供输入图片，生成示例猫咪...")
        sample_path = "/tmp/sample_cat.png"
        sample_img = generate_sample_cat()
        sample_img.save(sample_path)
        args.input = sample_path
        print(f"   示例图片已保存到: {sample_path}")

    if not os.path.exists(args.input):
        print(f"❌ 找不到输入文件: {args.input}")
        sys.exit(1)

    use_dither = not args.no_dither
    print(f"🎨 正在处理图片: {args.input}")
    print(f"   网格大小: {args.width} × {args.height}")
    print(f"   抖动: {'开启' if use_dither else '关闭'}")
    print(f"   平滑: {args.smooth}")

    # 转换为拼豆网格
    grid, bead_counts = image_to_bead_grid(
        args.input, args.width, args.height,
        dither=use_dither, smooth_level=args.smooth,
    )

    total = sum(bead_counts.values())
    print(f"   总豆数: {total}")
    print(f"   颜色种类: {len(bead_counts)}")
    print()
    print("📊 颜色统计:")
    for code, count in sorted(bead_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        entry = BEAD_PALETTE.get(code)
        name = entry[3] if entry else "未知"
        bar = "█" * int(pct / 2)
        print(f"   {code:4s} ({name:6s}): {count:4d} ({pct:5.1f}%) {bar}")

    # 生成 HTML
    html = generate_html(
        grid, bead_counts, title=args.title, show_background=args.show_bg
    )

    output_path = args.output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ 拼豆图案已生成: {output_path}")
    print(f"   用浏览器打开即可查看！")


if __name__ == "__main__":
    main()
