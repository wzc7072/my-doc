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
# ============================================================
BEAD_PALETTE = {
    "C3": (255, 255, 255, "白色", "White", "#FFFFFF", "#333333"),
    "H1": (245, 228, 200, "肤色/米色", "Flesh/Beige", "#F5E4C8", "#333333"),
    "E8": (220, 195, 162, "浅棕", "Light Brown", "#DCC3A2", "#333333"),
    "A3": (255, 255, 130, "黄色", "Yellow", "#FFFF82", "#333333"),
    "E2": (255, 182, 193, "粉色", "Pink", "#FFB6C1", "#333333"),
    "H7": (30, 30, 30, "黑色", "Black", "#1E1E1E", "#FFFFFF"),
    "H18": (140, 160, 180, "灰蓝", "Grey Blue", "#8CA0B4", "#333333"),
    "C1": (255, 100, 100, "红色", "Red", "#FF6464", "#FFFFFF"),
    "D1": (255, 165, 80, "橙色", "Orange", "#FFA550", "#333333"),
    "B1": (100, 180, 255, "蓝色", "Blue", "#64B4FF", "#333333"),
    "G1": (100, 200, 100, "绿色", "Green", "#64C864", "#333333"),
    "F1": (180, 130, 200, "紫色", "Purple", "#B482C8", "#333333"),
    "E1": (210, 170, 130, "棕色", "Brown", "#D2AA82", "#333333"),
    "H8": (80, 80, 80, "深灰", "Dark Grey", "#505050", "#FFFFFF"),
    "H3": (200, 200, 200, "浅灰", "Light Grey", "#C8C8C8", "#333333"),
    "H5": (160, 160, 160, "中灰", "Medium Grey", "#A0A0A0", "#333333"),
    "C5": (255, 245, 220, "奶白", "Cream", "#FFF5DC", "#333333"),
    "E3": (180, 140, 100, "中棕", "Medium Brown", "#B48C64", "#333333"),
    "E5": (120, 80, 50, "深棕", "Dark Brown", "#785032", "#FFFFFF"),
    "A1": (255, 240, 100, "浅黄", "Light Yellow", "#FFF064", "#333333"),
}


def color_distance(c1, c2):
    """计算两个颜色之间的感知距离 (加权欧几里得距离)"""
    # 使用加权的欧几里得距离，对人眼感知更准确
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    rmean = (r1 + r2) / 2
    dr = r1 - r2
    dg = g1 - g2
    db = b1 - b2
    return math.sqrt(
        (2 + rmean / 256) * dr * dr
        + 4 * dg * dg
        + (2 + (255 - rmean) / 256) * db * db
    )


def find_nearest_bead(pixel_color, palette):
    """找到最接近像素颜色的拼豆颜色"""
    min_dist = float("inf")
    best_code = "C3"
    for code, (r, g, b, *_) in palette.items():
        dist = color_distance(pixel_color, (r, g, b))
        if dist < min_dist:
            min_dist = dist
            best_code = code
    return best_code


def flatten_image(img, saturation_boost=1.3, contrast_boost=1.2, brightness_boost=1.05):
    """
    扁平化处理图片：
    1. 轻微模糊去噪
    2. 提升饱和度让颜色更鲜明
    3. 提升对比度
    4. 减少色彩数量（色彩量化）
    """
    # 确保是RGB模式
    img = img.convert("RGB")

    # 轻微模糊去除细节噪点
    img = img.filter(ImageFilter.SMOOTH_MORE)

    # 提升饱和度
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_boost)

    # 提升对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_boost)

    # 提升亮度
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness_boost)

    # 色彩量化 - 减少到与拼豆调色板相当的有限颜色
    img = img.quantize(colors=len(BEAD_PALETTE), method=Image.Quantize.MEDIANCUT)
    img = img.convert("RGB")

    return img


def image_to_bead_grid(image_path, grid_width=29, grid_height=46, palette=None):
    """
    将图片转换为拼豆网格

    Args:
        image_path: 输入图片路径
        grid_width: 网格宽度（列数）
        grid_height: 网格高度（行数）
        palette: 拼豆颜色表

    Returns:
        grid: 二维列表，每个元素是拼豆颜色代码
        bead_counts: 各颜色的使用数量
    """
    if palette is None:
        palette = BEAD_PALETTE

    # 打开并扁平化图片
    img = Image.open(image_path)
    img = flatten_image(img)

    # 缩放到目标网格大小
    img = img.resize((grid_width, grid_height), Image.Resampling.LANCZOS)

    # 再次锐化让边缘更清晰
    img = img.filter(ImageFilter.SHARPEN)

    # 转换每个像素到最近的拼豆颜色
    grid = []
    bead_counts = Counter()

    for y in range(grid_height):
        row = []
        for x in range(grid_width):
            pixel = img.getpixel((x, y))
            if len(pixel) == 4:  # RGBA
                pixel = pixel[:3]
            bead_code = find_nearest_bead(pixel, palette)
            row.append(bead_code)
            bead_counts[bead_code] += 1
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

    print(f"🎨 正在处理图片: {args.input}")
    print(f"   网格大小: {args.width} × {args.height}")

    # 转换为拼豆网格
    grid, bead_counts = image_to_bead_grid(
        args.input, args.width, args.height
    )

    total = sum(bead_counts.values())
    print(f"   总豆数: {total}")
    print(f"   颜色种类: {len(bead_counts)}")
    print()
    print("📊 颜色统计:")
    for code, count in sorted(bead_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        name = BEAD_PALETTE.get(code, ("", "", "", "未知"))[3]
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
