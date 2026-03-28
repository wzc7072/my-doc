#!/usr/bin/env python3
"""
猫猫拼豆图生成器 - Cat Perler Bead Pattern Image Generator

生成一张可爱的猫猫拼豆图（像素风格），并保存为 PNG 图片。
每个色块代表一颗拼豆珠子，可以直接作为拼豆手工制作的参考图。

使用方法:
    python generate_cat_beads.py [--output FILE] [--bead-size SIZE] [--gap GAP]

依赖:
    pip install Pillow
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# 猫猫图案定义（像素矩阵）
# 每个字符对应一颗拼豆珠子的颜色
# ---------------------------------------------------------------------------
#   '.' = 背景（透明/白色）
#   'B' = 黑色 (轮廓 / 眼睛)
#   'W' = 白色 (身体高光)
#   'O' = 橙色 (橘猫主体)
#   'P' = 粉色 (鼻子 / 耳内)
#   'G' = 灰色 (阴影)
#   'Y' = 黄色 (铃铛)
#   'R' = 红色 (项圈)

CAT_PATTERN = [
    "......BBBB..........BBBB......",
    ".....BOPPOB........BOPPOB.....",
    "....BOOPPOB........BOOPPOB....",
    "...BOOOPPOB........BOOOPPOB...",
    "..BOOOOPPBB........BBOOOOPOB..",
    ".BOOOOOOBBB........BBBOOOOOOB.",
    ".BOOOOOOOOBB......BBOOOOOOOOB.",
    "BOOOOOOOOOOBB....BBOOOOOOOOOOB",
    "BOOOOOOOOOOOBB..BBOOOOOOOOOOOB",
    "BOOOOOOOOOOOOBBBBOOOOOOOOOOOOB",
    "BOOOOOOOOOOOOOBBOOOOOOOOOOOOOB",
    "BOOOOOOOOOOOOOOOOOOOOOOOOOOOOB",
    "BOOOOOOOBBOOOOOOOOOOBBOOOOOOB.",
    ".BOOOOBWWWBOOOOOOOOBWWWBOOOOB.",
    ".BOOOOBWBWBOOOOOOOOBWBWBOOOOB.",
    "..BOOOBBBBBOOOOOOOOBBBBBOOOB..",
    "..BOOOOOOOOOOBPPBOOOOOOOOOOB..",
    "..BOOOOOOOOOBPPPPBOOOOOOOOB...",
    "...BOOOOOOOBBOOOOBBOOOOOOOB...",
    "...BOOOOOOOBOOOOOOBOOOOOOOB...",
    "....BOOOOOOOBOOOOBOOOOOOOB....",
    "....BOOOOOOOOBBBBOOOOOOOB.....",
    ".....BOOOOOOOOOOOOOOOOOOB.....",
    ".....BOORRRRRRRRRRRRRROOB.....",
    ".....BOORRRRRRYYRRRRRROOB.....",
    "......BORRRRRYYYYRRRROB.......",
    "......BOORRRRRYYRRRRROOB......",
    ".......BOORRRRRRRRRRROOB......",
    ".......BOOOOOOOOOOOOOOOOB.....",
    "........BOOOOOOOOOOOOOOB......",
    ".........BOOOOOOOOOOOOB.......",
    "..........BBBBBBBBBBBB........",
    "........BBOOOOOOOOOOOOBB......",
    ".......BOOOOOOOOOOOOOOOOOB....",
    ".......BOOOOOOBBBBOOOOOOB.....",
    ".......BOOOOOOB..BOOOOOOB.....",
    ".......BBBBBBB....BBBBBBB.....",
]

# 颜色映射
COLOR_MAP = {
    ".": None,  # 背景（透明）
    "B": (30, 30, 30),       # 黑色
    "W": (255, 255, 255),    # 白色
    "O": (255, 165, 60),     # 橙色
    "P": (255, 140, 160),    # 粉色
    "G": (180, 180, 180),    # 灰色
    "Y": (255, 215, 0),      # 黄色
    "R": (220, 40, 40),      # 红色
}

BACKGROUND_COLOR = (245, 240, 230)  # 温暖的米色背景


def generate_cat_beads_image(
    bead_size: int = 20,
    gap: int = 2,
    output_path: str = "cat_beads.png",
) -> Path:
    """
    根据猫猫拼豆图案生成 PNG 图片。

    Args:
        bead_size: 每颗拼豆珠子的直径（像素）。
        gap:       珠子之间的间隔（像素）。
        output_path: 输出图片路径。

    Returns:
        生成图片的路径。
    """
    pattern = CAT_PATTERN
    rows = len(pattern)
    cols = max(len(row) for row in pattern)

    cell = bead_size + gap
    padding = cell  # 四周留一格的空白

    img_width = cols * cell + gap + 2 * padding
    img_height = rows * cell + gap + 2 * padding

    img = Image.new("RGBA", (img_width, img_height), (*BACKGROUND_COLOR, 255))
    draw = ImageDraw.Draw(img)

    # 绘制底板网格线（浅灰色）
    grid_color = (210, 205, 195, 255)
    for r in range(rows + 1):
        y = padding + r * cell
        draw.line([(padding, y), (padding + cols * cell + gap, y)], fill=grid_color, width=1)
    for c in range(cols + 1):
        x = padding + c * cell
        draw.line([(x, padding), (x, padding + rows * cell + gap)], fill=grid_color, width=1)

    # 绘制每颗拼豆
    for r, row in enumerate(pattern):
        for c, ch in enumerate(row):
            color = COLOR_MAP.get(ch)
            if color is None:
                continue  # 空白格不画珠子
            x0 = padding + c * cell + gap
            y0 = padding + r * cell + gap
            x1 = x0 + bead_size
            y1 = y0 + bead_size
            # 圆形珠子
            draw.ellipse([x0, y0, x1, y1], fill=(*color, 255))
            # 添加轻微高光效果，使珠子看起来更立体
            highlight_offset = bead_size // 5
            highlight_size = bead_size // 4
            hx = x0 + highlight_offset
            hy = y0 + highlight_offset
            highlight_color = tuple(min(255, v + 80) for v in color) + (90,)
            draw.ellipse(
                [hx, hy, hx + highlight_size, hy + highlight_size],
                fill=highlight_color,
            )

    out = Path(output_path)
    img.save(out, "PNG")
    return out.resolve()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="猫猫拼豆图生成器 - 生成可爱猫猫拼豆图案的 PNG 图片",
    )
    parser.add_argument(
        "--output", "-o",
        default="cat_beads.png",
        help="输出图片路径 (默认: cat_beads.png)",
    )
    parser.add_argument(
        "--bead-size", "-s",
        type=int,
        default=20,
        help="每颗珠子的直径像素 (默认: 20)",
    )
    parser.add_argument(
        "--gap", "-g",
        type=int,
        default=2,
        help="珠子之间的间隔像素 (默认: 2)",
    )
    args = parser.parse_args()

    result = generate_cat_beads_image(
        bead_size=args.bead_size,
        gap=args.gap,
        output_path=args.output,
    )
    print(f"✅ 猫猫拼豆图已生成: {result}")


if __name__ == "__main__":
    main()
