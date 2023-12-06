# -*- coding: utf-8 -*-

#---    Packages
from Functions_ADDE_CL import *
import numpy as np
import h5py
import os
from functools import reduce
import warnings
warnings.filterwarnings('ignore')

#---    Initial matriz
n = 50                                        # Population size: 20, 35, 50

active_cells = 7536

k_shape_1 = (5,5)                             # HK_1
k_shape_2 = (3,3)                             # SY_1
k_shape_3 = (3,3)                             # HK_2
k_shape_4 = (2,2)                             # SY_2

n_var = active_cells * 2
for k in range(1,5):
    globals()['n_var_' + str(k)] = reduce(lambda x,y: x*y, globals()['k_shape_' + str(k)])
    n_var += globals()['n_var_' + str(k)]
n_var = n_var    
print (n_var)

#---    Create iteration register file
with h5py.File('Pre_ADDE_CL_historial.h5', 'w') as f:
    pob_x_h5py = f.create_dataset("pob_x", (n, n_var))

#---    Bounds
lb_kx, ub_kx = 0.015, 3.8
lb_sy, ub_sy = 0.278, 3.57

lb_1_kx, ub_1_kx = 0.001, 0.1
lb_1_sy, ub_1_sy = 0.365, 0.45
lb_2_kx, ub_2_kx = 0.002, 0.3
lb_2_sy, ub_2_sy = 0.125, 0.15

l_bounds = np.concatenate((np.around(np.repeat(lb_kx, active_cells),4), np.around(np.repeat(lb_sy, active_cells),4), 
                           np.around(np.repeat(lb_1_kx, n_var_1),4), np.around(np.repeat(lb_1_sy, n_var_2),4), 
                           np.around(np.repeat(lb_2_kx, n_var_3),4), np.around(np.repeat(lb_2_sy, n_var_4),4)), axis = 0)
u_bounds = np.concatenate((np.around(np.repeat(ub_kx, active_cells),4), np.around(np.repeat(ub_sy, active_cells),4), 
                           np.around(np.repeat(ub_1_kx, n_var_1),4), np.around(np.repeat(ub_1_sy, n_var_2),4), 
                           np.around(np.repeat(ub_2_kx, n_var_3),4), np.around(np.repeat(ub_2_sy, n_var_4),4)), axis = 0) 

#---    Initial Sampling (Latyn Hypercube)
sample_scaled = get_sampling_LH(n_var, n, l_bounds, u_bounds)
print(sample_scaled)

#---    Iteration register
for i in range(n):
    with h5py.File('Pre_ADDE_CL_historial.h5', 'a') as f:
        f["pob_x"][i] = np.copy(sample_scaled[i])
    f.close()

#---    Read file to verify
with h5py.File('Pre_ADDE_CL_historial.h5', 'r') as f:
    x = f["pob_x"][:]
print(x[0])
print(len(x))