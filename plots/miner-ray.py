import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

x = ['minerBlock', 'No Coin', 'Outgard', 'CMTracker', 'MineSweeper', 'MinerRay']
y1 = np.array([838, 742, 810, 809, 900, 901])
y2 = np.array([63, 159, 91, 92, 1, 0])
y3 = np.array([0, 0, 0, 0, 1406, 6])

# increase figure size
plt.figure(figsize = (8,6))

# add labels to each color
plt.bar(x, y1, color='Green', label = 'True positives')
plt.bar(x, y2, color='#e6ad12', bottom=y1, label = 'False negatives')
plt.bar(x, y3, color='Red', bottom=y1+y2, label = 'False positives')
plt.legend(loc = 0, fontsize = 15)

# plt.show()
plt.savefig('miner-ray.pdf')
