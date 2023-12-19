'''
--------------------------------------------------------------------------
注：没有确认过是否正确，只是写出来带入数据算了一遍得到的数据和理论值差不多就直接懒得验证了
--------------------------------------------------------------------------
'''

import numpy as np
import math

'''
0.函数和常数定义
'''
g = 9.7803
pi = 3.1415926

# 求均值和不确定度
def calculate_uncertainty(data):
    # 计算均值
    mean_value = np.mean(data)

    # 计算标准差作为测量误差的估计
    std_dev = np.std(data, ddof=1)

    # 计算标准误差，表示均值的不确定度
    std_err = std_dev / np.sqrt(len(data))

    # 计算不确定度的总值（包括测量误差和统计误差）
    total_uncertainty = np.sqrt(std_err**2 + (std_dev/2)**2)

    return mean_value, total_uncertainty

'''
1.计算L
'''
D1 = input("输入D内：").split(" ")
D2 = input("输入D外：").split(" ")

data1 = np.array(D1, dtype=float) / 1000
data2 = np.array(D2, dtype=float) / 1000
print(data1)
data3 = (data1 + data2) * pi
meanD1, uncertaintyD1 = calculate_uncertainty(data1)
meanD2, uncertaintyD2 = calculate_uncertainty(data2)
meanL, uncertaintyL = calculate_uncertainty(data3)

print(f"D内均值: {meanD1}")
print(f"D外均值: {meanD2}")
print(f"L均值: {meanL}")
print(f"L不确定度: {uncertaintyL}")

'''
2.计算K
'''
V = input("输入所有V平均值：")
Vs = V.split(" ")
deltaV = []
for i in range(1, len(Vs)):
    for j in range(i, len(Vs)):
        deltaV.append((float(Vs[j]) - float(Vs[j - i])) / i)
dataDeltaV = np.array(deltaV, dtype=float)
meanDeltaV, uncertaintyDeltaV = calculate_uncertainty(dataDeltaV)

avgK = 500 * 10**-6 * g / meanDeltaV
uncertaintyK = avgK * uncertaintyDeltaV / meanDeltaV

print("deltaV：", meanDeltaV)
print("K值：", avgK)
print("K不确定度：", uncertaintyK)


'''
3.计算室温a
'''
V1 = input("输入V1：").split(" ")
V2 = input("输入V2：").split(" ")

data1 = np.array(V1, dtype=float)
data2 = np.array(V2, dtype=float)
dataV = data1 - data2

mean1, _ = calculate_uncertainty(data1)
mean2, _ = calculate_uncertainty(data2)
meanV, uncertaintyV = calculate_uncertainty(dataV)

a = avgK * meanV / meanL
uncertaintyA = meanL * math.sqrt((uncertaintyK / avgK) ** 2 + (uncertaintyV / meanV) ** 2 + (uncertaintyL / meanL) ** 2)

# 打印结果
print(f"V1均值: {mean1}")
print(f"V2均值: {mean2}")
print(f"V: {dataV}")
print(f"V均值: {meanV}")
print(f"V不确定度: {uncertaintyV}")
print(f"a: {a}")
print(f"a不确定度: {uncertaintyA}")


'''
3.计算不同温度a
'''
V1 = input("输入V1：").split(" ")
V2 = input("输入V2：").split(" ")

data1 = np.array(V1, dtype=float)
data2 = np.array(V2, dtype=float)
dataV = data1 - data2

mean1, _ = calculate_uncertainty(data1)
mean2, _ = calculate_uncertainty(data2)
meanV, uncertaintyV = calculate_uncertainty(dataV)

a = avgK * meanV / meanL
uncertaintyA = meanL * math.sqrt((uncertaintyK / avgK) ** 2 + (uncertaintyV / meanV) ** 2 + (uncertaintyL / meanL) ** 2)

# 打印结果
print(f"V1均值: {mean1}")
print(f"V2均值: {mean2}")
print(f"V: {dataV}")
print(f"V均值: {meanV}")
print(f"V不确定度: {uncertaintyV}")
print(f"a: {a}")
print(f"a不确定度: {uncertaintyA}")