# -*- coding: utf-8 -*-
"""
Created on Thu May  9 15:40:18 2024

@author: frede
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May  9 14:26:37 2024

@author: frede
"""

import matplotlib.pyplot as plt
import numpy as np

# Data
labels = np.array(['    East', 'Up', 'West    ', 'Down'])



# Sample data provided
#labels = np.array(['    2', '1', '4    ', '3'])
value1 = np.array([8.5, 12.0, 5, 6.5])
value2 = np.array([11.3, 7, 10, 6.5])
#value3 = np.array([10.9, 10.3, 11.7, 44.2])



# Step 2: Calculate the maximum value per direction across all three arrays
max_values = np.max(np.vstack((value1, value2)), axis=0)

# Step 3: Normalize the values by dividing each value by the maximum value for its direction
value1 = value1 / max_values
value2 = value2 / max_values
#value3 = value3 / max_values


value1=np.concatenate((value1,[value1[0]]))
value2=np.concatenate((value2,[value2[0]]))
#value3=np.concatenate((value3,[value3[0]]))

#value4=np.concatenate((value4,[value4[0]]))


# Number of variables we're plotting.
num_vars = len(labels)

# Compute angle each bar is centered on:
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()




angles+=angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, value1, color='red', alpha=0.25, label='Model 1')
ax.fill(angles, value2, color='green', alpha=0.25, label='Model 2')
#ax.fill(angles, value3, color='blue', alpha=0.25, label = 'Sandia')




#ax.fill(angles, value4, color='yellow', alpha=0.25, label = 'Dirint')


# Draw one axe per variable and add labels
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels,fontsize=15)

plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.title('Selection plot', size=15, color='black', y=1.1)
plt.show()

# Comment out the plt.show() when running the final code to avoid automatic plot display.
# plt.show()










"""
#IAM:
    value1 = np.array([11.1, 10.4, 15.2, 49.1])
    value2 = np.array([11.2, 10.3, 11.6, 44.4])
    value3 = np.array([11.5, 10.2, 11.8, 44.4])
    
    # Plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, value1, color='red', alpha=0.25, label='None')
    ax.fill(angles, value3, color='green', alpha=0.25, label='ASHRAE')
    ax.fill(angles, value2, color='blue', alpha=0.25, label = 'SAPM')


# Trans simple
    
    value1 = np.array([20.1, 10.4, 21.6, 93])
    value2 = np.array([12.3, 15.7, 30.9, 88.5])
    value3 = np.array([11.1, 13.3, 31.2, 96.9])

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, value1, color='red', alpha=0.25, label='Isotropic simple')
ax.fill(angles, value2, color='green', alpha=0.25, label='HayDavies simple')
ax.fill(angles, value3, color='blue', alpha=0.25, label = 'PEREZ simple')



# Trans inf:
    
# Sample data provided
labels = np.array(['    East', 'Up', 'West    ', 'Down'])
value1 = np.array([24.7, 10.3, 15.2, 52.2])
value2 = np.array([15.9, 15.3, 24.4, 49.1])
#value3 = np.array([11.1, 13.3, 31.2, 96.9])



# Step 2: Calculate the maximum value per direction across all three arrays
max_values = np.max(np.vstack((value1, value2)), axis=0)

# Step 3: Normalize the values by dividing each value by the maximum value for its direction
value1 = value1 / max_values
value2 = value2 / max_values
#value3 = value3 / max_values


value1=np.concatenate((value1,[value1[0]]))
value2=np.concatenate((value2,[value2[0]]))
#value3=np.concatenate((value3,[value3[0]]))

#value4=np.concatenate((value4,[value4[0]]))


# Number of variables we're plotting.
num_vars = len(labels)

# Compute angle each bar is centered on:
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()




angles+=angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, value1, color='red', alpha=0.25, label='Isotropic inf.')
ax.fill(angles, value2, color='green', alpha=0.25, label='HayDavies inf.')
#ax.fill(angles, value3, color='blue', alpha=0.25, label = 'PEREZ simple')


#ax.fill(angles, value4, color='yellow', alpha=0.25, label = 'Dirint')


# Draw one axe per variable and add labels
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels,fontsize=15)

plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.title('Selection of transposition model inf.', size=15, color='black', y=1.1)
plt.show()


# sensor


# Data
labels = np.array(['    East', 'Up', 'West    ', 'Down'])



# Sample data provided
labels = np.array(['    East', 'Up', 'West    ', 'Down'])
value1 = np.array([25.2, 13.0, 15.0, 73.3])
value2 = np.array([20.1, 10.4, 21.6, 93.0])
#value3 = np.array([11.1, 13.3, 31.2, 96.9])



# Step 2: Calculate the maximum value per direction across all three arrays
max_values = np.max(np.vstack((value1, value2)), axis=0)

# Step 3: Normalize the values by dividing each value by the maximum value for its direction
value1 = value1 / max_values
value2 = value2 / max_values
#value3 = value3 / max_values


value1=np.concatenate((value1,[value1[0]]))
value2=np.concatenate((value2,[value2[0]]))
#value3=np.concatenate((value3,[value3[0]]))

#value4=np.concatenate((value4,[value4[0]]))


# Number of variables we're plotting.
num_vars = len(labels)

# Compute angle each bar is centered on:
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()




angles+=angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, value1, color='red', alpha=0.25, label='CMP6')
ax.fill(angles, value2, color='green', alpha=0.25, label='SPN1')
#ax.fill(angles, value3, color='blue', alpha=0.25, label = 'PEREZ simple')


#ax.fill(angles, value4, color='yellow', alpha=0.25, label = 'Dirint')


# Draw one axe per variable and add labels
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels,fontsize=15)

plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.title('Selection of GHI sensor', size=15, color='black', y=1.1)
plt.show()



#DNI 



# Sample data provided
labels = np.array(['    East', 'Up', 'West    ', 'Down'])
value1 = np.array([25.2, 13, 15.0, 73.3])
value2 = np.array([42.1, 21.8, 27.9, 80.0])
value3 = np.array([42.9, 22.2, 27.8, 80.0])



# Step 2: Calculate the maximum value per direction across all three arrays
max_values = np.max(np.vstack((value1, value2, value3)), axis=0)

# Step 3: Normalize the values by dividing each value by the maximum value for its direction
value1 = value1 / max_values
value2 = value2 / max_values
value3 = value3 / max_values


value1=np.concatenate((value1,[value1[0]]))
value2=np.concatenate((value2,[value2[0]]))
value3=np.concatenate((value3,[value3[0]]))

#value4=np.concatenate((value4,[value4[0]]))


# Number of variables we're plotting.
num_vars = len(labels)

# Compute angle each bar is centered on:
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()




angles+=angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, value3, color='blue', alpha=0.25, label = 'Dirindex turbidity')
ax.fill(angles, value2, color='green', alpha=0.25, label='Dirint')

ax.fill(angles, value1, color='red', alpha=0.25, label='Simple')

#ax.fill(angles, value4, color='yellow', alpha=0.25, label = 'Dirint')


# Draw one axe per variable and add labels
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels,fontsize=15)

plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.title('Selection of DNI model', size=15, color='black', y=1.1)
plt.show()





# Spectral


# Sample data provided
labels = np.array(['    East', 'Up', 'West    ', 'Down'])
value1 = np.array([11.2, 10.3, 11.6, 44.4])
value2 = np.array([10.5, 10.5, 11.9, 43.4])
value3 = np.array([10.9, 10.3, 11.7, 44.2])



# Step 2: Calculate the maximum value per direction across all three arrays
max_values = np.max(np.vstack((value1, value2, value3)), axis=0)

# Step 3: Normalize the values by dividing each value by the maximum value for its direction
value1 = value1 / max_values
value2 = value2 / max_values
value3 = value3 / max_values


value1=np.concatenate((value1,[value1[0]]))
value2=np.concatenate((value2,[value2[0]]))
value3=np.concatenate((value3,[value3[0]]))

#value4=np.concatenate((value4,[value4[0]]))


# Number of variables we're plotting.
num_vars = len(labels)

# Compute angle each bar is centered on:
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()




angles+=angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, value1, color='red', alpha=0.25, label='None')
ax.fill(angles, value2, color='green', alpha=0.25, label='Gueymard')
ax.fill(angles, value3, color='blue', alpha=0.25, label = 'Sandia')




#ax.fill(angles, value4, color='yellow', alpha=0.25, label = 'Dirint')


# Draw one axe per variable and add labels
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels,fontsize=15)

plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.title('Selection of spectral model', size=15, color='black', y=1.1)
plt.show()

# Comment out the plt.show() when running the final code to avoid automatic plot display.
# plt.show()


"""