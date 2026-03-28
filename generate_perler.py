#!/usr/bin/env python3
"""
Generate perler bead pixel art for an orange Maine Coon cat.

Produces:
  - perler_cat.png        : 64×64 pixel grid (each cell 16×16 px, with grid lines)
  - perler_cat_legend.png : color legend with bead counts
  - perler_cat_pattern.txt: text character grid pattern

Run:
    python generate_perler.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Color palette  (12 colors — simulating common Perler/Hama bead colors)
# Format:  char -> (rgb_tuple, display_name, perler_color_name)
# ---------------------------------------------------------------------------
PALETTE = {
    'g': ((45,  45,  42),  "Dark Gray",     "Pewter"),
    'K': ((12,  10,   8),  "Black",         "Black"),
    'D': ((90,  50,  20),  "Dark Brown",    "Dark Brown"),
    'B': ((140, 80,  30),  "Brown",         "Brown"),
    'O': ((210, 105, 25),  "Orange",        "Orange"),
    'o': ((235, 155, 55),  "Light Orange",  "Cheddar"),
    'Y': ((248, 210, 120), "Cream",         "Cream"),
    'W': ((250, 246, 238), "White",         "White"),
    'P': ((228, 148, 138), "Pink",          "Blush"),
    'p': ((195,  85,  70), "Dark Pink",     "Salmon"),
    'G': ((155, 175,  90), "Lime Green",    "Kiwi Lime"),
    'A': ((185, 155,  65), "Amber",         "Butterscotch"),
}

GRID_W = 64
GRID_H = 64


# ---------------------------------------------------------------------------
# Helper drawing functions
# ---------------------------------------------------------------------------

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _set(grid, x, y, char):
    if 0 <= x < GRID_W and 0 <= y < GRID_H:
        grid[y][x] = char


def _ellipse(grid, cx, cy, rx, ry, char, overwrite=None):
    """Fill an ellipse; only overwrites cells whose current value is in `overwrite` (None = all)."""
    for y in range(max(0, int(cy - ry) - 1), min(GRID_H, int(cy + ry) + 2)):
        for x in range(max(0, int(cx - rx) - 1), min(GRID_W, int(cx + rx) + 2)):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                if overwrite is None or grid[y][x] in overwrite:
                    grid[y][x] = char


def _ellipse_ring(grid, cx, cy, rx, ry, char, thickness=1):
    """Draw an ellipse ring (outline only)."""
    for y in range(max(0, int(cy - ry) - 2), min(GRID_H, int(cy + ry) + 3)):
        for x in range(max(0, int(cx - rx) - 2), min(GRID_W, int(cx + rx) + 3)):
            dx = (x - cx) / (rx + thickness)
            dy = (y - cy) / (ry + thickness)
            if dx * dx + dy * dy <= 1.0:
                dx2 = (x - cx) / (rx - thickness + 1)
                dy2 = (y - cy) / (ry - thickness + 1)
                if dx2 * dx2 + dy2 * dy2 >= 1.0:
                    grid[y][x] = char


def _rect(grid, x0, y0, x1, y1, char, overwrite=None):
    for y in range(max(0, y0), min(GRID_H, y1 + 1)):
        for x in range(max(0, x0), min(GRID_W, x1 + 1)):
            if overwrite is None or grid[y][x] in overwrite:
                grid[y][x] = char


def _triangle(grid, tip_x, tip_y, bl_x, br_x, base_y, char, overwrite=None):
    """Fill a downward triangle (tip at top, base at bottom)."""
    if base_y <= tip_y:
        return
    for y in range(tip_y, base_y + 1):
        t = (y - tip_y) / (base_y - tip_y)
        lx = int(round(tip_x + t * (bl_x - tip_x)))
        rx = int(round(tip_x + t * (br_x - tip_x)))
        for x in range(max(0, lx), min(GRID_W, rx + 1)):
            if overwrite is None or grid[y][x] in overwrite:
                grid[y][x] = char


# ---------------------------------------------------------------------------
# Build the 64×64 Maine Coon cat pixel grid
# ---------------------------------------------------------------------------

def build_grid():
    # Start with background
    grid = [['g'] * GRID_W for _ in range(GRID_H)]

    # ── EARS ────────────────────────────────────────────────────────────────
    # Left ear (orange triangle, tip at row 3, base rows 14-18)
    _triangle(grid, 13,  3, 6, 20, 17, 'O')
    # Left ear inner (pink)
    _triangle(grid, 13,  6, 9, 17, 14, 'P')
    # Ear tuft tip
    _set(grid, 13, 3, 'D')
    _set(grid, 12, 4, 'D')
    _set(grid, 14, 4, 'D')

    # Right ear
    _triangle(grid, 50,  3, 43, 57, 17, 'O')
    _triangle(grid, 50,  6, 46, 54, 14, 'P')
    _set(grid, 50, 3, 'D')
    _set(grid, 49, 4, 'D')
    _set(grid, 51, 4, 'D')

    # ── HEAD (main ellipse) ─────────────────────────────────────────────────
    # Main head: light orange fill
    _ellipse(grid, 32, 36, 23, 25, 'o')
    # Slightly darker orange border/cheeks
    _ellipse_ring(grid, 32, 36, 23, 25, 'O', thickness=2)

    # ── FOREHEAD TABBY STRIPES ───────────────────────────────────────────────
    # Three horizontal stripes on forehead
    for row_y in [18, 20, 22]:
        for x in range(22, 42):
            if grid[row_y][x] == 'o':
                grid[row_y][x] = 'O'

    # M-mark on forehead
    for x in range(26, 29):
        _set(grid, x, 15, 'D') if grid[15][x] == 'o' else None
    for x in range(29, 31):
        _set(grid, x, 14, 'D') if grid[14][x] == 'o' else None
    for x in range(31, 34):
        _set(grid, x, 15, 'D') if grid[15][x] == 'o' else None
    for x in range(34, 36):
        _set(grid, x, 14, 'D') if grid[14][x] == 'o' else None
    for x in range(36, 38):
        _set(grid, x, 15, 'D') if grid[15][x] == 'o' else None

    # ── EYES ─────────────────────────────────────────────────────────────────
    # Left eye: amber iris, then green rim, then black pupil slit
    _ellipse(grid, 21, 30,  7, 4, 'A', overwrite={'o', 'O'})   # amber iris
    _ellipse(grid, 21, 30,  5, 3, 'G', overwrite={'A'})          # green rim
    # Pupil slit
    for y in range(28, 33):
        for x in range(20, 23):
            if grid[y][x] in ('A', 'G'):
                grid[y][x] = 'K'
    # Eye shine
    _set(grid, 17, 28, 'W')
    # Eye outline
    _ellipse_ring(grid, 21, 30, 7, 4, 'K', thickness=1)

    # Right eye: center (43, 30)
    _ellipse(grid, 43, 30,  7, 4, 'A', overwrite={'o', 'O'})
    _ellipse(grid, 43, 30,  5, 3, 'G', overwrite={'A'})
    for y in range(28, 33):
        for x in range(42, 45):
            if grid[y][x] in ('A', 'G'):
                grid[y][x] = 'K'
    _set(grid, 39, 28, 'W')
    _ellipse_ring(grid, 43, 30, 7, 4, 'K', thickness=1)

    # Eyebrow ridge (darker fur above eyes)
    for x in range(15, 28):
        if grid[24][x] == 'o':
            grid[24][x] = 'O'
    for x in range(37, 50):
        if grid[24][x] == 'o':
            grid[24][x] = 'O'

    # ── MUZZLE (white puffy cheeks) ─────────────────────────────────────────
    _ellipse(grid, 24, 41, 9, 8, 'W', overwrite={'o', 'O', 'Y'})
    _ellipse(grid, 40, 41, 9, 8, 'W', overwrite={'o', 'O', 'Y'})

    # ── NOSE ─────────────────────────────────────────────────────────────────
    # Pink nose (small inverted triangle)
    _triangle(grid, 32, 36, 29, 35, 39, 'p')
    # Nose tip center
    for x in range(30, 34):
        _set(grid, x, 39, 'P')
    _set(grid, 32, 40, 'P')

    # ── MOUTH ────────────────────────────────────────────────────────────────
    _set(grid, 32, 42, 'K')
    _set(grid, 33, 42, 'K')
    for x in [28, 29, 30]:
        _set(grid, x, 43, 'K')
    for x in [34, 35, 36]:
        _set(grid, x, 43, 'K')

    # ── CHIN (white) ─────────────────────────────────────────────────────────
    _ellipse(grid, 32, 48, 9, 6, 'W', overwrite={'o', 'O', 'Y', 'W'})

    # ── FUR RUFF / NECK (cream/pale) ─────────────────────────────────────────
    _ellipse(grid, 32, 57, 16, 8, 'Y', overwrite={'o', 'O', 'g'})

    # ── BODY HINT ────────────────────────────────────────────────────────────
    for y in range(59, 64):
        for x in range(14, 50):
            if grid[y][x] == 'g':
                grid[y][x] = 'o'
    # Body stripes (alternating orange and brown)
    for y in range(60, 64):
        for x in range(20, 24):
            if grid[y][x] == 'o':
                grid[y][x] = 'O'
        for x in range(28, 32):
            if grid[y][x] in ('o', 'Y'):
                grid[y][x] = 'B'
        for x in range(40, 44):
            if grid[y][x] == 'o':
                grid[y][x] = 'O'

    # Brown chin-area line detail
    for x in range(27, 37):
        if grid[49][x] == 'o':
            grid[49][x] = 'B'

    # ── SIDE CHEEK FUR DETAILS ───────────────────────────────────────────────
    for y in range(32, 50):
        for x in range(10, 15):
            d = math.sqrt((x - 32) ** 2 + (y - 36) ** 2)
            if 20 < d < 24 and grid[y][x] == 'o':
                grid[y][x] = 'O'
    for y in range(32, 50):
        for x in range(49, 54):
            d = math.sqrt((x - 32) ** 2 + (y - 36) ** 2)
            if 20 < d < 24 and grid[y][x] == 'o':
                grid[y][x] = 'O'

    return grid


# ---------------------------------------------------------------------------
# Color statistics
# ---------------------------------------------------------------------------

def build_color_index(grid):
    counts = {}
    for row in grid:
        for ch in row:
            counts[ch] = counts.get(ch, 0) + 1
    result = []
    for ch, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        if ch in PALETTE:
            rgb, name, perler = PALETTE[ch]
            result.append((ch, rgb, name, perler, cnt))
    return result


# ---------------------------------------------------------------------------
# Output 1: Pixel grid PNG
# ---------------------------------------------------------------------------

def draw_grid_image(grid, cell=16):
    W = GRID_W * cell
    H = GRID_H * cell
    img = Image.new('RGB', (W, H), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            rgb, _, _ = PALETTE.get(ch, PALETTE['g'])
            x0, y0 = x * cell, y * cell
            # Fill cell with a slight inner padding for a "bead" look
            draw.rectangle([x0 + 1, y0 + 1, x0 + cell - 2, y0 + cell - 2], fill=rgb)

    # Grid lines
    for xi in range(0, W + 1, cell):
        draw.line([(xi, 0), (xi, H)], fill=(70, 70, 70), width=1)
    for yi in range(0, H + 1, cell):
        draw.line([(0, yi), (W, yi)], fill=(70, 70, 70), width=1)

    return img


# ---------------------------------------------------------------------------
# Output 2: Legend PNG
# ---------------------------------------------------------------------------

def draw_legend_image(color_index):
    swatch = 32
    pad = 12
    row_h = 44
    col_w = 330
    ncols = 2
    nrows = (len(color_index) + ncols - 1) // ncols
    W = col_w * ncols + pad * 2
    H = row_h * nrows + pad * 2 + 56

    img = Image.new('RGB', (W, H), (248, 246, 240))
    draw = ImageDraw.Draw(img)

    # Try to load a system font
    try:
        font_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except Exception:
        font_title = ImageFont.load_default()
        font = ImageFont.load_default()

    draw.text((pad, pad),
              "Perler Bead Color Legend — Orange Maine Coon Cat",
              fill=(30, 30, 30), font=font_title)

    for i, (ch, rgb, name, perler, count) in enumerate(color_index):
        col = i % ncols
        row = i // ncols
        x0 = pad + col * col_w
        y0 = 56 + row * row_h

        # Color swatch with border
        draw.rectangle([x0, y0, x0 + swatch, y0 + swatch - 4],
                       fill=rgb, outline=(100, 100, 100), width=1)
        # Char badge
        draw.rectangle([x0 + swatch + 4, y0, x0 + swatch + 22, y0 + swatch - 4],
                       fill=(60, 60, 60))
        draw.text((x0 + swatch + 7, y0 + 4), ch, fill=(255, 255, 255), font=font)

        label = f"{name} / {perler}  ×{count}"
        draw.text((x0 + swatch + 28, y0 + 8), label, fill=(40, 40, 40), font=font)

    return img


# ---------------------------------------------------------------------------
# Output 3: Text pattern TXT
# ---------------------------------------------------------------------------

def write_pattern_txt(grid, color_index, path):
    lines = []
    lines.append("Perler Bead Pattern — Orange Maine Coon Cat")
    lines.append("=" * 70)
    lines.append(f"Grid size: {GRID_W} × {GRID_H}  |  Total beads: {GRID_W * GRID_H}")
    lines.append("")
    lines.append("Color Key:")
    for ch, rgb, name, perler, count in color_index:
        r, g, b = rgb
        lines.append(f"  [{ch}]  {name:<16s} Perler: {perler:<14s}  #{r:02X}{g:02X}{b:02X}  ×{count}")
    lines.append("")
    lines.append("Pattern (each character = 1 bead):")
    lines.append("")
    # Column ruler
    ruler_tens = "   " + "".join(
        str(x // 10) if x % 10 == 0 else " " for x in range(GRID_W))
    ruler_ones = "   " + "".join(str(x % 10) for x in range(GRID_W))
    lines.append(ruler_tens)
    lines.append(ruler_ones)
    lines.append("   " + "-" * GRID_W)
    for y, row in enumerate(grid):
        lines.append(f"{y:2d}|{''.join(row)}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    grid = build_grid()
    color_index = build_color_index(grid)

    out_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Pixel grid image
    img_grid = draw_grid_image(grid, cell=16)
    grid_path = os.path.join(out_dir, "perler_cat.png")
    img_grid.save(grid_path)
    print(f"Saved: {grid_path}  ({img_grid.width}×{img_grid.height} px)")

    # 2. Legend image
    img_legend = draw_legend_image(color_index)
    legend_path = os.path.join(out_dir, "perler_cat_legend.png")
    img_legend.save(legend_path)
    print(f"Saved: {legend_path}  ({img_legend.width}×{img_legend.height} px)")

    # 3. Text pattern
    txt_path = os.path.join(out_dir, "perler_cat_pattern.txt")
    write_pattern_txt(grid, color_index, txt_path)
    print(f"Saved: {txt_path}")

    print(f"\nColors used: {len(color_index)}")
    print("\nColor summary:")
    for ch, rgb, name, perler, count in color_index:
        bar = "█" * min(40, count // 30)
        print(f"  [{ch}] {name:<16s}  {count:4d} beads  {bar}")


if __name__ == "__main__":
    main()
