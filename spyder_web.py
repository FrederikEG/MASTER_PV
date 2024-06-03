# -*- coding: utf-8 -*-
"""
Created on Thu May  9 14:26:37 2024

@author: frede
"""

import matplotlib.pyplot as plt
import numpy as np

# Data
labels = np.array(['    East', 'Up', 'West    ', 'Down'])
value2 = np.array([11.2, 10.3, 11.6, 44.4])
value1 = np.array([11.1, 10.4, 15.2, 49.1])
value3 = np.array([11.5, 10.2, 11.8, 44.4])
#value4 = np.array([24, 22, 18, 20])







# Number of variables we're plotting.
num_vars = len(labels)

# Compute angle each bar is centered on:
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# Repeat the first value to close the circle
value2=np.concatenate((value2,[value2[0]]))
value1=np.concatenate((value1,[value1[0]]))
value3=np.concatenate((value3,[value3[0]]))
#value4=np.concatenate((value4,[value4[0]]))


angles+=angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, value1, color='red', alpha=0.25, label='None')
ax.fill(angles, value3, color='green', alpha=0.25, label='ASHRAE')
ax.fill(angles, value2, color='blue', alpha=0.25, label = 'SAPM')


#ax.fill(angles, value4, color='yellow', alpha=0.25, label = 'Dirint')


# Draw one axe per variable and add labels
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels,fontsize=15)

plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.title('Selection of IAM model', size=15, color='black', y=1.1)
plt.show()

# Comment out the plt.show() when running the final code to avoid automatic plot display.
# plt.show()
