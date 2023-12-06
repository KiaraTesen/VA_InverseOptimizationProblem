# -*- coding: utf-8 -*-

#---    Packages
from Functions_ADPSO_CL import *
import geopandas as gpd
import pandas as pd
import numpy as np
import h5py
import matplotlib.pyplot as plt
import os
from functools import reduce
import time
import sys
from request_server.request_server import send_request_py
import warnings
warnings.filterwarnings('ignore')

IP_SERVER_ADD = sys.argv[1]
ITERATION = int(sys.argv[2])
TOTAL_ITERATION = int(sys.argv[3])
FINAL_ITERATION = int(sys.argv[4])

VM = int(sys.argv[5])

#---    Paths
path_WEAP = r'C:\Users\vagrant\Documents\WEAP Areas\SyntheticProblem_WEAPMODFLOW'
path_model = os.path.join(path_WEAP, 'MODFLOW_model')
path_init_model = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\MODFLOW_model\MODFLOW_model_vinit'
path_nwt_exe = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\MODFLOW-NWT_1.2.0\bin\MODFLOW-NWT_64.exe'        # Need to add the MODFLOW NWT exe
path_GIS = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\GIS'    
path_output = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\ADPSO_CL\output'                                       # Need full path for WEAP Export
path_obs_data = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\ObservedData'

#---    Initial matriz
HP = ['kx', 'sy'] 
initial_shape_HP = gpd.read_file(path_GIS + '/Elements_initial_unique_value_v2.shp')   
active_matriz = initial_shape_HP['Active'].to_numpy().reshape((84,185))                                                         # Matrix of zeros and ones that allows maintaining active area

active_cells = 7536

k_shape_1 = (5,5)                           # HK_1
k_shape_2 = (3,3)                           # SY_1
k_shape_3 = (3,3)                           # HK_2
k_shape_4 = (2,2)                           # SY_2

n_var = active_cells * 2
for k in range(1,5):
    globals()['n_var_' + str(k)] = reduce(lambda x,y: x*y, globals()['k_shape_' + str(k)])
    n_var += globals()['n_var_' + str(k)]
n_var = n_var                               # Number of variables
print (n_var)

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
class Particle:
    def __init__(self,x,v,y):
        self.x = x                          # X represents the kernels
        self.v = v                          # initial velocity = zeros
        self.y = y
        self.x_best = np.copy(x)                 
        self.y_best = y

pob = Particle(np.around(np.array([0]*(n_var)),4),np.around(np.array([0]*(n_var)),4),10000000000)

if ITERATION == 0:
    with h5py.File('Pre_ADPSO_CL_historial.h5', 'r') as f:
        pob.x = np.copy(f["pob_x"][VM-2])
    f.close()

    #---    Initial Sampling - Pob(0)
    y_init = Run_WEAP_MODFLOW(path_output, str(ITERATION), initial_shape_HP, HP, active_cells, pob.x, n_var_1, n_var_2, n_var_3, n_var, 
                              k_shape_1, k_shape_2, k_shape_3, k_shape_4, active_matriz, path_init_model, path_model, path_nwt_exe, 
                              path_obs_data)
    pob.x_best = np.copy(pob.x)
    pob.y = y_init
    pob.y_best = y_init

    #---    Create iteration register file
    with h5py.File('ADPSO_CL_historial.h5', 'w') as f:
        iter_h5py = f.create_dataset("iteration", (FINAL_ITERATION, 1))
        pob_x_h5py = f.create_dataset("pob_x", (FINAL_ITERATION, n_var))
        pob_y_h5py = f.create_dataset("pob_y", (FINAL_ITERATION, 1))
        pob_v_h5py = f.create_dataset("pob_v", (FINAL_ITERATION, n_var))
        pob_x_best_h5py = f.create_dataset("pob_x_best", (FINAL_ITERATION, n_var))
        pob_y_best_h5py = f.create_dataset("pob_y_best", (FINAL_ITERATION, 1))
        pob_w_h5py = f.create_dataset("w", (FINAL_ITERATION, 1))

    #---    Iteration register
        iter_h5py[0] = ITERATION
        pob_x_h5py[0] = np.copy(pob.x)
        pob_y_h5py[0] = pob.y
        pob_v_h5py[0] = np.copy(pob.v)
        pob_x_best_h5py[0] = np.copy(pob.x_best)
        pob_y_best_h5py[0] = pob.y_best
        pob_w_h5py[0] = 0.5
    f.close()

else:
    #---    PSO
    α = 0.8                                                     # Cognitive scaling parameter  # 0.8 # 1.49
    β = 0.8                                                     # Social scaling parameter     # 0.8 # 1.49                       
    w_min = 0.4                                                 # minimum value for the inertia velocity
    w_max = 0.9                                                 # maximum value for the inertia velocity
    vMax = np.around(np.multiply(u_bounds-l_bounds,0.8),4)      # Max velocity # De 0.8 a 0.4
    vMin = -vMax                                                # Min velocity

    with h5py.File('ADPSO_CL_historial.h5', 'r') as f:
        pob.x = np.copy(f["pob_x"][ITERATION - 1])
        pob.y = f["pob_y"][ITERATION - 1]
        pob.v = np.copy(f["pob_v"][ITERATION - 1])
        pob.x_best = np.copy(f["pob_x_best"][ITERATION - 1])
        pob.y_best = f["pob_y_best"][ITERATION - 1]

        w = f["w"][ITERATION - 1]                               # inertia velocity
    f.close()
    
    time.sleep(np.random.randint(10,30,size = 1)[0])
    gbest = send_request_py(IP_SERVER_ADD, pob.y, pob.x)        # Update global particle

    #---    Update particle velocity
    ϵ1,ϵ2 = np.around(np.random.uniform(),4), np.around(np.random.uniform(),4)            # [0, 1]

    pob.v = np.around(np.around(w*pob.v,4) + np.around(α*ϵ1*(pob.x_best - pob.x),4) + np.around(β*ϵ2*(gbest - pob.x),4),4)

    #---    Adjust particle velocity
    index_vMax = np.where(pob.v > vMax)
    index_vMin = np.where(pob.v < vMin)

    if np.array(index_vMax).size > 0:
        pob.v[index_vMax] = vMax[index_vMax]
    if np.array(index_vMin).size > 0:
        pob.v[index_vMin] = vMin[index_vMin]

    #---    Update particle position
    pob.x += pob.v

    #---    Adjust particle position
    index_pMax = np.where(pob.x > u_bounds)
    index_pMin = np.where(pob.x < l_bounds)

    if np.array(index_pMax).size > 0:
        pob.x[index_pMax] = u_bounds[index_pMax]
    if np.array(index_pMin).size > 0:
        pob.x[index_pMin] = l_bounds[index_pMin]

    #---    Evaluate the fitnness function
    y = Run_WEAP_MODFLOW(path_output, str(ITERATION), initial_shape_HP, HP, active_cells, pob.x, n_var_1, n_var_2, n_var_3, n_var, 
                         k_shape_1, k_shape_2, k_shape_3, k_shape_4, active_matriz, path_init_model, path_model, path_nwt_exe, 
                         path_obs_data)
    
    if y < pob.y_best:
        pob.x_best = np.copy(pob.x)
        pob.y_best = y
        pob.y = y
    else:
        pob.y = y

    #---    Update the inertia velocity
    w = w_max - (ITERATION) * ((w_max-w_min)/FINAL_ITERATION)

    #---    Iteration register
    with h5py.File('ADPSO_CL_historial.h5', 'a') as f:
        f["iteration"][ITERATION] = ITERATION
        f["pob_x"][ITERATION] = np.copy(pob.x)
        f["pob_y"][ITERATION] = pob.y
        f["pob_v"][ITERATION] = np.copy(pob.v)
        f["pob_x_best"][ITERATION] = np.copy(pob.x_best)
        f["pob_y_best"][ITERATION] = pob.y_best

        f["w"][ITERATION] = w
    f.close()