import numpy as np
import math

'''
1.常数及函数
'''
g = 9.7803
pi = 3.1415926
g = 9.78

uL = 0.8 * 10**-3 / math.sqrt(3) # L的不确定度（只有卷尺误差所以是常数）
uH = uL # 同理只有卷尺误差
uD = 0.02 * 10**-3 / math.sqrt(3) # 同理只有游标卡尺误差


# 求均值和不确定度
def calculate_uncertainty(data, UL):
    # 计算均值
    mean_value = np.mean(data)

    # 计算标准差作为测量误差的估计
    std_dev = np.std(data, ddof=1)

    # 计算标准误差，表示均值的不确定度SL
    std_err = std_dev / np.sqrt(len(data))

    # 计算不确定度的总值（包括测量误差和统计误差）
    total_uncertainty = np.sqrt(std_err**2 + UL**2)

    return mean_value, total_uncertainty

'''
2.计算杨氏模量（单位均为公制单位）
'''
m = 5 # 以5kg为间隔
L = 0.7375
H = 0.671
D = 0.04628
avgd = 0.000598
avgDeltaX = 0.01881 # 自己算

E = 8 * m * g * L * H / (pi * avgd * avgd * D * avgDeltaX)
print("杨氏模量：", E)

'''
3.计算杨氏模量的不确定度
'''
deltaX = np.array([18.9, 18.8, 18.75, 18.95, 18.65]) * 10**-3
d = np.array([0.599, 0.595, 0.595, 0.594, 0.605, 0.600]) * 10**-3
_, uncertaintydeltaX = calculate_uncertainty(deltaX, 0.02 * 10**-3) # deltaX的不确定度用近似了（后面是游标卡尺精度）
_, uncertaintyd = calculate_uncertainty(d, 0.01 * 10 ** -3) # 螺旋测微器精度

ue = E * math.sqrt((uL/L) ** 2 + (uH/H) ** 2 + (2 * uncertaintyd/avgd) ** 2 + (uD/D) ** 2 + (uncertaintydeltaX/avgDeltaX) ** 2)

print(uL, L, uH, H, uncertaintyd, avgd, uD, D, uncertaintydeltaX, avgDeltaX)
print("△x的不确定度：", uncertaintydeltaX)
print("d的不确定度：", uncertaintyd)
print("E的不确定度：", ue)
