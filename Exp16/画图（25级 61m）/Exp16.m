clear; clc; close all;
time = 0:25;
%中心面热电势
S_center = [36, 43, 56, 78, 104, 132, 160, 189, 218, 247, 275, 304, 331, 360, 387, 415, 442, 470, 497, 523, 550, 576, 603, 629, 655, 680];
T_center = S_center ./ 40;
%加热面热电势
S_heat = [60, 143, 189, 226, 259, 289, 318, 346, 375, 404, 431, 459, 487, 514, 542, 569, 596, 623, 650, 677, 703, 729, 755, 781, 807, 823];
T_heat = S_heat ./ 40;
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