# 🐱 拼豆图案生成器 (Perler Bead Pattern Generator)

将真实照片（如猫咪照片）进行**扁平化处理**，然后转换为**拼豆图案**（Perler Bead Pattern），
生成带有颜色代码、行列编号和豆子统计的 HTML 网格。

## 效果说明

1. **高精度处理管线**: 先缩放到目标网格，再逐像素映射到拼豆色（不做预量化以保留最大信息量）
2. **CIELAB 感知色差**: 使用 CIEDE2000 算法在 Lab 色彩空间中匹配最近颜色，比 RGB 距离准确得多
3. **Floyd-Steinberg 抖动**: 将量化误差扩散到相邻像素，大幅提升细节还原度
4. **32 色扩展调色板**: 覆盖白/灰/黑、肤色、棕色梯度、黄/橙、粉/红、蓝/灰蓝、绿、紫、暖灰系列
5. **网格输出**: 生成类似手工拼豆图纸的 HTML 页面

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

# 禁用抖动（更"干净"但细节更少）
python perler_bead_pattern.py my_cat.jpg --no-dither

# 更强的平滑（柔化噪点）
python perler_bead_pattern.py my_cat.jpg --smooth 2
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
| `--no-dither` | 禁用 Floyd-Steinberg 抖动 | 否（默认开启抖动） |
| `--smooth, -s` | 平滑程度: 0=无, 1=轻微, 2=中等, 3=强 | 1 |

### 依赖安装

```bash
pip install Pillow numpy
```

## 精度优化说明

相比简单实现，本工具做了以下优化来保证高保真度：

| 方面 | 简单方式 | 本工具 |
|------|----------|--------|
| 色差计算 | RGB 欧几里得距离 | CIEDE2000 (CIELAB) |
| 处理顺序 | 模糊→量化→缩放→映射 | 缩放→轻微平滑→直接映射 |
| 抖动 | 无 | Floyd-Steinberg 误差扩散 |
| 调色板 | 20 色 | 32 色（含暖灰/棕色梯度） |
| 预处理 | 强模糊 + 饱和度拉升 | 最小化干预，保留原始信息 |

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
| 更多... | ... | 共 32 种颜色 |

## 输出格式

生成的 HTML 文件包含:
- **效果预览**: 圆点缩略图，直观展示最终效果
- **详细网格**: 带行列编号的颜色代码网格（可用于对照拼豆）
- **颜色图例**: 各颜色的使用数量统计
