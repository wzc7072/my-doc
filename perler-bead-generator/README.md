# 🐱 拼豆图案生成器 (Perler Bead Pattern Generator)

将真实照片（如猫咪照片）进行**扁平化处理**，然后转换为**拼豆图案**（Perler Bead Pattern），
生成带有颜色代码、行列编号和豆子统计的 HTML 网格。

## 效果说明

1. **扁平化处理**: 对输入照片进行模糊去噪、饱和度增强、对比度调整、色彩量化
2. **颜色映射**: 将每个像素映射到最接近的拼豆颜色（基于感知色差距离）
3. **网格输出**: 生成类似手工拼豆图纸的 HTML 页面

## 使用方法

### 基本用法

```bash
# 使用内置示例猫咪
python perler_bead_pattern.py

# 指定输入图片
python perler_bead_pattern.py my_cat.jpg

# 自定义网格大小和输出文件
python perler_bead_pattern.py my_cat.jpg --width 29 --height 46 --output cat_pattern.html

# 指定标题
python perler_bead_pattern.py my_cat.jpg --title "豆画/我的猫咪"
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入图片路径（可选，不提供则使用示例） | - |
| `--width, -W` | 网格宽度（列数） | 29 |
| `--height, -H` | 网格高度（行数） | 46 |
| `--output, -o` | 输出 HTML 文件路径 | `bead_pattern.html` |
| `--title, -t` | 图案标题 | `豆画/Cat` |
| `--show-bg` | 是否显示背景区域 | 否 |

### 依赖安装

```bash
pip install Pillow numpy
```

## 拼豆颜色表

| 代码 | 颜色 | 说明 |
|------|------|------|
| C3 | ⬜ | 白色 |
| H1 | 🟨 | 肤色/米色 |
| E8 | 🟫 | 浅棕 |
| A3 | 💛 | 黄色 |
| E2 | 💗 | 粉色 |
| H7 | ⬛ | 黑色 |
| H18 | 🔵 | 灰蓝 |
| 更多... | ... | 共 20 种颜色 |

## 输出格式

生成的 HTML 文件包含:
- **效果预览**: 圆点缩略图，直观展示最终效果
- **详细网格**: 带行列编号的颜色代码网格（可用于对照拼豆）
- **颜色图例**: 各颜色的使用数量统计

## 示例

```bash
# 生成示例猫咪的拼豆图案
python perler_bead_pattern.py --output cat_example.html --title "豆画/Mard"
```

然后用浏览器打开 `cat_example.html` 即可查看结果。
