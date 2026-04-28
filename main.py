import requests
import apimoex
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import log10
from fractal.fractal import box_counting
from scipy.ndimage import gaussian_filter1d

# Получить цены акции с тикером security в промежуток с start='YYYY-MM-DD' до end='YYYY-MM-DD'
def get_prices(security, start, end):
    prices = np.array([])
    with requests.Session() as session:
        data = apimoex.get_board_history(session, security, start, end)
        df = pd.DataFrame(data)
        df.set_index('TRADEDATE', inplace=True)
        prices = df['CLOSE'].to_numpy()
    return prices

security = 'SBER'
start_date = '2022-01-01'
end_date = '2025-12-31'

y_coords = get_prices(security, start_date, end_date)
y_coords = y_coords[~np.isnan(y_coords)]
sample_size = len(y_coords)
x_coords = np.linspace(0, sample_size - 1, sample_size)

#Нормализация данных
x_coords_norm = (x_coords) / (x_coords.max() - x_coords.min())
y_coords_norm = (y_coords) / (y_coords.max() - y_coords.min())


# Калибровка scales (Здесь я подкручиваю число p в log10(sample_size*p) так, чтобы размерность прямой была как можно ближе к 1)
scales = np.logspace(log10(0.001), log10(0.55), 17)

# points = np.empty((sample_size, 2))
# for i in range (sample_size):
#     points[i] = [x_coords_norm[i], x_coords_norm[i]]
# points = points[~np.isnan(points).any(axis=1)]

points = np.empty((sample_size, 2))
for i in range (sample_size):
    points[i] = [x_coords_norm[i], y_coords_norm[i]]
points = points[~np.isnan(points).any(axis=1)]

# dim = box_counting(points, scales)['fd']
# print(dim)

sigma = 10.0
y_coords_regularized = gaussian_filter1d(y_coords_norm, sigma=sigma)

dy_dx = np.gradient(y_coords_regularized)

# VISUALIZATION OF THE PRICE CHART
plt.figure(figsize=(10, 6))
# plt.plot(x_coords_norm, y_coords_norm, color='red')
# plt.plot(x_coords_norm, y_coords_regularized, color='green')
plt.plot(x_coords_norm, dy_dx, color='blue')
plt.xlabel('Шаг по дате')
plt.ylabel('Цена')
plt.grid(True, alpha=0.3)
plt.show()

# TODO: Поработать над вычислением размерности
# TODO: Добавить вычисление производной тренда и маркера купить/продать
# TODO: Запилить бота