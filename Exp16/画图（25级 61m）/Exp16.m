clear; clc; close all;
time = 0:25;
%电动势与温度关系（μV/K）
sensitivity = 40;
%中心面热电势（将0改为实验数据）
S_center = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
T_center = S_center ./ sensitivity;
%加热面热电势（将0改为实验数据）
S_heat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
T_heat = S_heat ./ sensitivity;
%△T
T_delta = T_heat - T_center;
%画图
plot(time, T_center, 'Color', [202/255, 97/255, 77/255], 'Linestyle', '-', 'LineWidth', 1);
hold on;
plot(time, T_heat, 'Color', [196/255, 42/255, 28/255], 'Linestyle', '-', 'LineWidth', 2);
plot(time, T_delta, 'Color', [149/255, 214/255, 208/255], 'Linestyle', '-', 'LineWidth', 1);
hold off;
%表头样品：有机玻璃/橡胶
title('有机玻璃');
xlabel('加热时间τ/min');
ylabel('温度/K');
legend('中心面', '加热面', '△T');
grid on;
