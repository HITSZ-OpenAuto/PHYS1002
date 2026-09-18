# -*- coding: utf-8 -*-

"""
实验14：自组光栅光谱仪
Hg灯标定光谱绘制

输入文件：
    data.csv

CSV格式：
    第一列：CCD位置(pixel)
    第二列：相对强度

说明：
    列的顺序可以互换，程序会自动识别哪一列是CCD位置。
    有没有表头都可以，程序会自动判断。

    程序会在“扣除基线后的光谱”上自动寻找Hg谱峰，
    自动与标准波长配对并完成标定，不需要手工填写峰位置。
    自动标定失败时会退回使用脚本内置的手工峰位置。

输出：
    Hg灯标定光谱.png
"""

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter


# ============================================================
# 零、路径设置
# ============================================================

# 以脚本所在目录为基准，避免依赖“当前工作目录”
# 这样在 PowerShell 和 VSCode 中运行结果一致

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# 一、CSV文件
# ============================================================

CSV_FILE = BASE_DIR / "data.csv"
OUTPUT_PNG = BASE_DIR / "Hg灯标定光谱.png"


# ============================================================
# 二、Hg灯标准谱线
# ============================================================

# 本次实验数据中可以可靠识别的Hg谱线
# 用于建立CCD像素位置与波长之间的标定关系

HG_WAVELENGTH = np.array([
    365.48,
    404.66,
    435.84,
    546.07,
    576.96
])


# ============================================================
# 三、自动寻峰与标定参数
# ============================================================

# 默认在“扣除基线后的光谱”上自动寻找Hg谱峰，
# 再自动与上面的标准波长配对，不需要手工填写峰位置。

# 峰与峰之间的最小像素间距。
#
# 取值依据：
#   434.75nm / 435.83nm 这一对双线的间距约 11~19 pixel，
#   而相邻的不同Hg谱线间距约 198 pixel，
# 因此取 40 既能合并双线，又不会把不同谱线误并成一个。

MIN_PEAK_DISTANCE = 40

# 寻峰的高度阈值（相对于校正后光谱的最大值）。
#
# 不同同学的数据整体强弱差别可以很大，用相对值比用绝对值稳。
# 若发现漏掉 365.48nm 那条弱线，可以适当调小；
# 若出现很多杂峰，可以适当调大。

PEAK_HEIGHT_RATIO = 0.02

# 认为标定结果可信的均方根残差上限（nm）。
#
# 用半高宽中点定位峰位时，本实验数据下正确配对的残差约 0.86nm，
# 而次优（错误）配对约 1.76nm，取 1.5 能清楚区分两者。
# 如果你的数据整体偏差偏大而被误判为“不可信”，可以适当放宽。

MAX_FIT_RMS_NM = 1.5

# 参与配对搜索的峰值上限。
#
# 杂峰极多时组合数会爆炸，这里只保留最高的若干个峰。

MAX_PEAKS_FOR_MATCH = 20


# ------------------------------------------------------------
# 手工兜底峰位置
# ------------------------------------------------------------

# 自动寻峰失败（峰太少或配对残差过大）时使用下列常量。
# 这是原作者那一次实验的峰位置，只对同一台仪器、同一批调校有效。

CCD_PIXEL_MANUAL = np.array([
    644.46,
    872.47,
    1070.09,
    1730.14,
    1927.43
])

# 改为 True 可以强制使用上面的手工峰位置，跳过自动寻峰

USE_MANUAL_PEAKS = False


# ============================================================
# 四、设置中文字体
# ============================================================

# 优先使用Windows常见中文字体

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Arial Unicode MS",
    "DejaVu Sans"
]

# 解决负号显示问题

plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 五、读取CSV文件
# ============================================================

encodings = [
    "gb18030",
    "gbk",
    "utf-8-sig",
    "utf-8"
]

# 先按“没有表头”读取，之后再来判断第一行到底是不是表头。
#
# 导出软件有的写表头、有的不写，而 pandas 默认把第一行当表头，
# 遇到没有表头的文件就会悄悄吃掉一个数据点。这里统一处理。

raw = None
used_encoding = None
last_error = None

for encoding in encodings:

    try:

        raw = pd.read_csv(
            CSV_FILE,
            encoding=encoding,
            header=None
        )

        used_encoding = encoding

        break

    except FileNotFoundError as error:

        # 文件不存在时换编码也没有意义，直接抛出并提示真实路径

        raise FileNotFoundError(
            f"找不到数据文件：{CSV_FILE}\n"
            f"请确认文件存在，或修改程序中的 CSV_FILE 路径。"
        ) from error

    except Exception as error:

        last_error = error


# 如果读取失败

if raw is None:

    raise RuntimeError(
        f"无法读取数据文件：{CSV_FILE}\n"
        f"已尝试的编码：{encodings}\n"
        f"最后一次错误：{last_error}"
    )


print("CSV文件读取成功")
print("使用编码：", used_encoding)


# 判断首行是否为表头：
# 只要首行出现无法转成数值的单元格，就说明它是表头，丢掉即可。

if pd.to_numeric(raw.iloc[0], errors="coerce").isna().any():

    raw = raw.iloc[1:].reset_index(drop=True)

    print("检测到表头，已跳过首行")

else:

    print("未检测到表头，全部行按数据处理")


# ============================================================
# 六、识别CCD位置列和相对强度列
# ============================================================

# 先找出所有“整列都能转成数值”的列，非数值列（例如文字备注）直接排除

numeric_columns = []

for column_index in range(raw.shape[1]):

    column_values = pd.to_numeric(
        raw.iloc[:, column_index],
        errors="coerce"
    ).values

    if np.isfinite(column_values).all():

        numeric_columns.append(column_index)


if len(numeric_columns) < 2:

    raise RuntimeError(
        "数据文件中至少需要两列纯数值（CCD位置、相对强度），"
        f"当前只识别到 {len(numeric_columns)} 列。"
    )


# CCD位置列的特征是“等步长且单调”。
# 光栅光谱仪的CCD像素是按顺序编号的，这一点可以用来区分两列。

pixel_column = None

for column_index in numeric_columns:

    column_values = pd.to_numeric(
        raw.iloc[:, column_index],
        errors="coerce"
    ).values

    steps = np.diff(column_values)

    monotonic = (
        np.all(steps > 0)
        or
        np.all(steps < 0)
    )

    evenly_spaced = (
        len(steps) > 0
        and np.allclose(steps, steps[0])
    )

    if monotonic and evenly_spaced:

        pixel_column = column_index

        break


if pixel_column is None:

    # 没有明显等步长的列，退回“第一列位置、第二列强度”的老做法

    pixel_column = numeric_columns[0]

    print("警告：未找到等步长的CCD位置列，按第一列=位置、第二列=强度处理")

else:

    print("CCD位置列：第", pixel_column + 1, "列")


# 剩下的数值列中取第一列作为相对强度

intensity_candidates = [
    column_index
    for column_index in numeric_columns
    if column_index != pixel_column
]

intensity_column = intensity_candidates[0]


if len(intensity_candidates) > 1:

    print(
        "警告：存在多个可选强度列，使用第",
        intensity_column + 1,
        "列"
    )


# 取出CCD位置和相对强度

x = pd.to_numeric(
    raw.iloc[:, pixel_column],
    errors="coerce"
).values

y = pd.to_numeric(
    raw.iloc[:, intensity_column],
    errors="coerce"
).values


# 去掉无效数据

valid = (
    np.isfinite(x)
    &
    np.isfinite(y)
)

x = x[valid]
y = y[valid]


if len(x) < 10:

    raise RuntimeError(
        f"有效数据点只有 {len(x)} 个，数据量太少，无法完成标定。"
    )


# 如果CCD位置是递减的，整体翻转为递增，便于后续处理

if x[0] > x[-1]:

    x = x[::-1]
    y = y[::-1]

    print("检测到CCD位置递减，已翻转为递增顺序")


print("有效数据点数量：", len(x))
print("CCD位置范围：", x.min(), "~", x.max())


# ============================================================
# 七、光谱平滑
# ============================================================

# Savitzky-Golay平滑
#
# 21个数据点作为平滑窗口
# 三阶多项式

SMOOTH_WINDOW = 21


def safe_odd_window(target, length, minimum=5):
    """把窗口长度调整成 savgol_filter 能接受的合法值。

    savgol_filter 要求 window_length 为奇数，
    且不能大于数据点个数，否则直接报错。
    数据点很少时（例如只导出了几十行）自动缩小窗口。
    """

    # 数据点个数允许的最大奇数窗口

    largest_odd = length if length % 2 == 1 else length - 1

    window = min(target, largest_odd)

    if window % 2 == 0:

        window -= 1

    # 窗口太小会让 savgol_filter 报错，这里保证一个下限

    if window < minimum:

        window = min(minimum, largest_odd)

        if window % 2 == 0:

            window -= 1

    return window


SMOOTH_WINDOW = safe_odd_window(SMOOTH_WINDOW, len(y))


# ============================================================
# 八、估计光谱背景
# ============================================================

# 使用较大的窗口估计缓慢变化的背景

BASELINE_WINDOW = 501


# 防止窗口超过数据长度（数据点少时自动缩小）

BASELINE_WINDOW = safe_odd_window(BASELINE_WINDOW, len(y))


baseline = savgol_filter(
    y,
    window_length=BASELINE_WINDOW,
    polyorder=2
)


# ============================================================
# 九、扣除背景
# ============================================================

y_corrected = y - baseline


# 小于0的值设置成0

y_corrected[
    y_corrected < 0
] = 0


# 再做一次轻微平滑

y_corrected = savgol_filter(
    y_corrected,
    window_length=SMOOTH_WINDOW,
    polyorder=3
)


# ============================================================
# 十、自动寻找Hg谱峰
# ============================================================

# 注意：必须在“扣除基线后的光谱上”寻峰。
#
# 原始光谱的基线本身就有很大起伏（本实验数据从几十一直爬到上方），
# 直接在原始曲线上找极大值会得到错误的位置。


# 寻峰高度阈值用“最大值的若干倍”这种相对值，
# 这样不同同学数据整体强弱不同也能通用。


def detect_peaks(height_ratio):
    """按给定的相对高度阈值寻峰，返回（峰序号, 属性, 实际阈值）。"""

    threshold = max(y_corrected.max() * height_ratio, 1e-9)

    found, found_properties = find_peaks(
        y_corrected,
        distance=MIN_PEAK_DISTANCE,
        height=threshold,
        prominence=threshold
    )

    return found, found_properties, threshold


peaks, peak_properties, PEAK_HEIGHT = detect_peaks(PEAK_HEIGHT_RATIO)


# 谱线较弱时可能漏峰，降低阈值再试一次

if len(peaks) < len(HG_WAVELENGTH):

    retry = detect_peaks(PEAK_HEIGHT_RATIO * 0.25)

    if len(retry[0]) > len(peaks):

        print("初次寻峰数量不足，已降低阈值重试")

        peaks, peak_properties, PEAK_HEIGHT = retry


# 杂峰太多时组合数会爆炸，只保留最高的若干个

if len(peaks) > MAX_PEAKS_FOR_MATCH:

    keep = np.sort(
        np.argsort(y_corrected[peaks])[-MAX_PEAKS_FOR_MATCH:]
    )

    peaks = peaks[keep]

    peak_properties = {
        name: np.asarray(values)[keep]
        for name, values in peak_properties.items()
    }

    print(
        "检测到峰数过多，只保留最高的",
        MAX_PEAKS_FOR_MATCH,
        "个参与配对"
    )


def refine_peak_position(index):
    """用半高宽中点作为峰位估计。

    直接用最大值的位置会明显偏移，因为谱峰并不对称
    （404.66nm与407.78nm、434.75nm与435.83nm都是双线）。
    半高宽中点比最大值位置更接近谱线中心，
    实测可把标定残差从1.28nm降到0.86nm。
    """

    half = y_corrected[index] / 2.0

    left = index

    while left > 0 and y_corrected[left] > half:

        left -= 1

    right = index

    while right < len(y_corrected) - 1 and y_corrected[right] > half:

        right += 1

    # 半高位置落在数据范围外（例如峰骑在更强的峰肩上），
    # 退回用最大值位置，交由后面的残差检查判断是否可信

    if y_corrected[left] > half or y_corrected[right] > half:

        return float(x[index])

    return (x[left] + x[right]) / 2.0


peak_positions = np.array(
    [refine_peak_position(peak) for peak in peaks]
)


print()
print("==========================================")
print("自动寻峰结果")
print("==========================================")
print(f"寻峰高度阈值：{PEAK_HEIGHT:.4f}")
print("检出峰数量：", len(peaks))

for peak_index, peak in enumerate(peaks):

    prominence = peak_properties["prominences"][peak_index]

    print(
        f"  峰{peak_index + 1}：CCD位置 = {peak_positions[peak_index]:.2f}，"
        f"强度 = {y_corrected[peak]:.2f}，"
        f"显著度 = {prominence:.2f}"
    )


# ============================================================
# 十一、把谱峰与Hg标准波长配对
# ============================================================


def fit_rms(pixel_positions):
    """对给定峰位做二次拟合，返回（系数, 均方根残差nm）。"""

    fitted = np.polyfit(pixel_positions, HG_WAVELENGTH, 2)

    residual = HG_WAVELENGTH - np.polyval(fitted, pixel_positions)

    return fitted, float(np.sqrt(np.mean(residual ** 2)))


# 枚举所有“5个峰↔5条谱线”的配对，取残差最小的一组。
#
# Hg谱线的波长随CCD位置单调增加，
# 所以只要从检出的峰里挑出5个，按像素升序与波长升序的谱线一一对应即可。
#
# 这里只允许“5条全部参与”是有意为之：
#   二次多项式有3个参数，如果允许只用4条谱线拟合，就只剩1个自由度，
#   很容易“恰好穿过”得到残差≈0的假结果。
#   实测中曾出现错误配对给出0.01nm残差、而正确配对照1.28nm的情况，
#   因此“残差最小”必须在同样多的谱线数量下比较才有意义。

candidates = []

for peak_choice in combinations(range(len(peaks)), len(HG_WAVELENGTH)):

    pixel_choice = np.array(
        sorted(peak_positions[peak] for peak in peak_choice)
    )

    fitted, rms = fit_rms(pixel_choice)

    candidates.append((rms, pixel_choice, fitted))


candidates.sort(key=lambda item: item[0])


# 判断自动标定是否可信

auto_ok = (
    len(candidates) > 0
    and candidates[0][0] <= MAX_FIT_RMS_NM
)

use_manual = USE_MANUAL_PEAKS or not auto_ok


if len(candidates) == 0:

    print()
    print(
        "警告：检出的谱峰不足",
        len(HG_WAVELENGTH),
        "个，无法与Hg标准谱线一一配对。"
    )

elif not auto_ok:

    print()
    print(
        f"警告：最佳配对的均方根残差为 {candidates[0][0]:.4f} nm，"
        f"超过上限 {MAX_FIT_RMS_NM} nm，自动标定结果不可信。"
    )


# 把残差最小的前几组列出来，方便人工核对

if len(candidates) > 1:

    print()
    print("残差最小的前几组配对（可用于人工核对）：")

    for index, (rms, pixel_choice, _) in enumerate(candidates[:3], start=1):

        positions = "，".join(f"{value:.2f}" for value in pixel_choice)

        print(f"  {index}. RMS = {rms:.4f} nm，峰位 = {positions}")


if use_manual:

    print()
    print("已退回使用脚本内置的手工峰位置 CCD_PIXEL_MANUAL。")

    calibration_pixel = np.array(CCD_PIXEL_MANUAL)

    if len(calibration_pixel) != len(HG_WAVELENGTH):

        raise RuntimeError(
            "手工峰位置数量与Hg标准谱线数量不一致，无法完成标定。"
        )

    coefficients, match_rms = fit_rms(calibration_pixel)

else:

    match_rms, calibration_pixel, coefficients = candidates[0]

    print()
    print("自动配对结果：")

    for pixel, wavelength in zip(calibration_pixel, HG_WAVELENGTH):

        print(f"  CCD位置 {pixel:>9.2f}  ↔  {wavelength:>7.2f} nm")


# ============================================================
# 十二、建立CCD像素—波长标定方程
# ============================================================

# 使用二次多项式：
#
# λ = ax² + bx + c

a = coefficients[0]
b = coefficients[1]
c = coefficients[2]


# ============================================================
# 十三、输出标定方程
# ============================================================

print()
print("==========================================")
print("CCD像素—波长标定方程")
print("==========================================")

print(
    f"λ = {a:.10e} × x² "
    f"+ {b:.10e} × x "
    f"+ {c:.6f}"
)

print("其中：")
print("x 为CCD像素位置")
print("λ 的单位为nm")
print(f"标定均方根残差 RMS = {match_rms:.4f} nm")


# ============================================================
# 十四、将CCD像素坐标转换为波长坐标
# ============================================================

wavelength = np.polyval(
    coefficients,
    x
)


# ============================================================
# 十五、绘制最终Hg灯标定光谱
# ============================================================

plt.figure(
    figsize=(10, 5.5)
)


plt.plot(
    wavelength,
    y_corrected,
    linewidth=1.2
)


# ============================================================
# 十六、设置中文坐标轴
# ============================================================

plt.xlabel(
    "波长 λ / nm",
    fontsize=13
)


plt.ylabel(
    "相对强度",
    fontsize=13
)


plt.title(
    "Hg灯标定光谱",
    fontsize=15
)


# ============================================================
# 十七、根据实际数据自动设置横坐标范围
# ============================================================

xmin = wavelength.min()
xmax = wavelength.max()

margin = 0.02 * (xmax - xmin)

plt.xlim(
    xmin - margin,
    xmax + margin
)


# ============================================================
# 十八、自动设置横坐标刻度
# ============================================================

plt.locator_params(
    axis="x",
    nbins=8
)


# ============================================================
# 十九、网格
# ============================================================

plt.grid(
    alpha=0.25
)


# ============================================================
# 二十、调整图像布局
# ============================================================

plt.tight_layout()


# ============================================================
# 二十一、保存图片
# ============================================================

plt.savefig(
    OUTPUT_PNG,
    dpi=300,
    bbox_inches="tight"
)


# ============================================================
# 二十二、显示图片
# ============================================================

plt.show()


# ============================================================
# 二十三、程序结束
# ============================================================

print()
print("==========================================")
print("数据处理完成")
print("==========================================")
print("输出图片：", OUTPUT_PNG)