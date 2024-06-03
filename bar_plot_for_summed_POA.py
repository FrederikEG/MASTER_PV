# -*- coding: utf-8 -*-
"""
Created on Sat May 18 10:42:43 2024

@author: frede
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

colors = sns.color_palette('muted')

# Sample summed data for the POA components for two different orientations
POA_sky_diffuse_grid_1 = 78.76  # example value in KWh/m2
POA_ground_diffuse_grid_1 = 28.99  # example value in KWh/m2
POA_direct_grid_1 = 97.14  # example value in KWh/m2

POA_sky_diffuse_grid_2 = 80.56  # example value in KWh/m2
POA_ground_diffuse_grid_2 = 31.98  # example value in KWh/m2
POA_direct_grid_2 = 79.16  # example value in KWh/m2

# Summing the components to get the totals
total_1 = POA_sky_diffuse_grid_1 + POA_ground_diffuse_grid_1 + POA_direct_grid_1
total_2 = POA_sky_diffuse_grid_2 + POA_ground_diffuse_grid_2 + POA_direct_grid_2

# Calculate the percentages
sky_diffuse_pct_1 = (POA_sky_diffuse_grid_1 / total_1) * 100
ground_diffuse_pct_1 = (POA_ground_diffuse_grid_1 / total_1) * 100
direct_pct_1 = (POA_direct_grid_1 / total_1) * 100

sky_diffuse_pct_2 = (POA_sky_diffuse_grid_2 / total_2) * 100
ground_diffuse_pct_2 = (POA_ground_diffuse_grid_2 / total_2) * 100
direct_pct_2 = (POA_direct_grid_2 / total_2) * 100

# Data for the plot
orientations = ['Tilted', 'Vertical']
sky_diffuse = [POA_sky_diffuse_grid_1, POA_sky_diffuse_grid_2]
ground_diffuse = [POA_ground_diffuse_grid_1, POA_ground_diffuse_grid_2]
direct = [POA_direct_grid_1, POA_direct_grid_2]

# Create the figure and the axes
fig, ax1 = plt.subplots(figsize=(10, 6))

# Primary y-axis (absolute values)
ax1.bar(orientations, direct, label='Direct', color=colors[0])
ax1.bar(orientations, sky_diffuse, bottom=direct, label='Sky diffuse', color=colors[1])
ax1.bar(orientations, ground_diffuse, bottom=[i+j for i,j in zip(direct, sky_diffuse)], label='Ground diffuse', color=colors[2])

# Adding percentage values text on the bars
for i, (d, sd, gd) in enumerate(zip(direct, sky_diffuse, ground_diffuse)):
    ax1.text(i, d / 2, f'{direct_pct_1 if i == 0 else direct_pct_2:.1f}%', color='black', fontweight='bold', ha='center', va='center', fontsize=12)
    ax1.text(i, d + sd / 2, f'{sky_diffuse_pct_1 if i == 0 else sky_diffuse_pct_2:.1f}%', color='black', fontweight='bold', ha='center', va='center', fontsize=12)
    ax1.text(i, d + sd + gd / 2, f'{ground_diffuse_pct_1 if i == 0 else ground_diffuse_pct_2:.1f}%', color='black', fontweight='bold', ha='center', va='center', fontsize=12)

# Adding labels and title with larger font sizes
ax1.set_ylabel('Solar insolation (kWh/m2)', fontsize=14)
ax1.set_title('POA solar insolation over the long interval', fontsize=16)
ax1.legend(loc='upper right', fontsize=10)

# Set larger font sizes for tick labels
ax1.tick_params(axis='both', which='major', labelsize=12)

# Show the plot
plt.show()
