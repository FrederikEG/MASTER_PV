# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 13:04:22 2024

@author: frede
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle



def draw_shadow(x, y, module_width, module_length,shadow_vertical,shadow_horizontal,solar_azimuth):
    fig, ax = plt.subplots()

    # Draw outer rectangle
    outer_rectangle = Rectangle((x, y), module_length, module_width, color='blue', alpha=0.5)
    ax.add_patch(outer_rectangle)
    
    if solar_azimuth<90:
    # Draw inner square
        inner_square = Rectangle((x+module_length,y), -shadow_vertical, module_width, color='red', alpha=0.5)
        ax.add_patch(inner_square)
    else:
        inner_square = Rectangle((x,y), shadow_vertical, module_width, color='red', alpha=0.5)
        ax.add_patch(inner_square)
        
    
    # Draw 2nd inner square
    top_square = Rectangle((0+shadow_vertical,module_width), module_length-shadow_vertical, shadow_horizontal)
    ax.add_patch(top_square)

    # Set axis limits
    ax.set_xlim(x - 1, x + module_length + 1)
    ax.set_ylim(y - 1, y + module_width + 1)

    # Show plot
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Shadows on panel')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()

# Example usage
#draw_shadow(0, 0, 2, 6,2,-1)
