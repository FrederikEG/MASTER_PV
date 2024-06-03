# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 14:15:40 2024

@author: frede
"""

import pvlib
import numpy as np
import matplotlib.pyplot as plt


sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod') 
module_sandia = sandia_modules['LG_LG290N1C_G3__2013_'] # module LG290N1C - mono crystalline si 


tilt= np.arange(0, 91, 1).astype(float)
iam_diffuse_ashrae =pvlib.iam.marion_diffuse(model='ashrae', surface_tilt=tilt)
iam_diffuse_sapm =pvlib.iam.marion_diffuse(model='sapm', module = module_sandia, surface_tilt=tilt)
iam_direct_ashrae = pvlib.iam.ashrae(tilt)
iam_direct_sapm = pvlib.iam.sapm(tilt, module = module_sandia)



fig1, ax1 = plt.subplots()
fig1.suptitle('IAM sky diffuse')
ax1.plot(tilt,iam_diffuse_ashrae['sky'],label='ashrae')
ax1.plot(tilt,iam_diffuse_sapm['sky'],label='sapm')
plt.axvline(x=25, color='black', linestyle='--')  # Red line at x=25
ax1.text(25, 0.965, 'Tilt \n 25 deg', fontsize=10, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
plt.axvline(x=90, color='black', linestyle='--')  # Red line at x=25
ax1.text(90, 0.965, 'Tilt \n 90 deg', fontsize=10, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.set_ylim([0.95, 0.97])
ax1.set_xlim([0, 100])
ax1.set(ylabel='IAM (-)')
ax1.set(xlabel='PV module tilt (deg)')
plt.grid(True)
plt.legend()


fig1, ax1 = plt.subplots()
fig1.suptitle('IAM ground and horizon diffuse')
ax1.plot(tilt,iam_diffuse_ashrae['ground'],label='ashrae ground')
ax1.plot(tilt,iam_diffuse_sapm['ground'],label='sapm ground')
ax1.plot(tilt,iam_diffuse_ashrae['horizon'],label='ashrae horizon')
ax1.plot(tilt,iam_diffuse_sapm['horizon'],label='sapm horizon')
plt.axvline(x=25, color='black', linestyle='--')  # Red line at x=25
ax1.text(25, 0.4, 'Tilt \n 25 deg', fontsize=10, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
plt.axvline(x=90, color='black', linestyle='--')  # Red line at x=25
ax1.text(90, 0.4, 'Tilt \n 90 deg', fontsize=10, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.set_ylim([0, 1])
ax1.set_xlim([0, 100])
ax1.set(ylabel='IAM (-)')
ax1.set(xlabel='PV module tilt (deg)')
plt.grid(True)
plt.legend()



fig1, ax1 = plt.subplots()
fig1.suptitle('IAM direct and circumsolar')
ax1.plot(tilt,iam_direct_ashrae,label='ashrae')
ax1.plot(tilt,iam_direct_sapm,label='sapm')
ax1.set_ylim([0, 1.2])
ax1.set_xlim([0, 90])
ax1.set(ylabel='IAM (-)')
ax1.set(xlabel='Incidence angle (deg)')
plt.grid(True)
plt.legend()