# -*- coding: utf-8 -*-

#---    Packages
from Functions_ADDE_CL import *
import geopandas as gpd
import pandas as pd
import sys
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

#---    Configure IP and PORT
VM = int(sys.argv[1])

MY_IP = f"10.0.0.{10+VM}"
MY_IP_PORT = f"{MY_IP}:8888"

ITERATION = int(sys.argv[2])
TOTAL_ITERATION = int(sys.argv[3])
FINAL_ITERATION = int(sys.argv[4])

VMS = int(sys.argv[5])

#---    Paths
path_WEAP = r'C:\Users\vagrant\Documents\WEAP Areas\SyntheticProblem_WEAPMODFLOW'
path_model = os.path.join(path_WEAP, 'MODFLOW_model')
path_init_model = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\MODFLOW_model\MODFLOW_model_vinit'
path_nwt_exe = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\MODFLOW-NWT_1.2.0\bin\MODFLOW-NWT_64.exe'       # Need to add the MODFLOW NWT exe
path_GIS = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\GIS'    
path_output = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\ADDE_CL\output'                                       # Need full path for WEAP Export
path_obs_data = r'C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\data\ObservedData'

#---    Initial matriz
HP = ['kx', 'sy'] 
initial_shape_HP = gpd.read_file(path_GIS + '/Elements_initial_unique_value_v2.shp')
active_matriz = initial_shape_HP['Active'].to_numpy().reshape((84,185))             # Matrix of zeros and ones that allows maintaining active area

active_cells = 7536

k_shape_1 = (5,5)                                                                   # HK_1
k_shape_2 = (3,3)                                                                   # SY_1
k_shape_3 = (3,3)                                                                   # HK_2
k_shape_4 = (2,2)                                                                   # SY_2

n_var = active_cells * 2
for k in range(1,5):
    globals()['n_var_' + str(k)] = reduce(lambda x,y: x*y, globals()['k_shape_' + str(k)])
    n_var += globals()['n_var_' + str(k)]
n_var = n_var                                                                       # Number of variables
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
    def __init__(self,x):
        self.x = x                                                              # X represents the kernels
        self.y = 1000000000

pob = Particle(np.around(np.array([0]*(n_var)),4))

if ITERATION == 0:
    with h5py.File('Pre_ADDE_CL_historial.h5', 'r') as f:
        pob.x = np.copy(f["pob_x"][VM-2])
    f.close()

    #---    Initial Sampling - Pob(0)
    y_init = Run_WEAP_MODFLOW(path_output, str(ITERATION), initial_shape_HP, HP, active_cells, pob.x, n_var_1, n_var_2, n_var_3, n_var, 
                              k_shape_1, k_shape_2, k_shape_3, k_shape_4, active_matriz, path_init_model, path_model, path_nwt_exe, 
                              path_obs_data)
    pob.y = y_init

    # send xi to the server
    send_request_py(MY_IP_PORT, 1, pob.x)
    time.sleep(60)

    file = open(f"ind_{MY_IP}_8888.txt", "w")
    file.write(f"{ITERATION},{pob.y}\n")
    file.close()

    filename = open(f"ind_{MY_IP}_relation.txt", "w")
    filename.close()

    #---    Create iteration register file
    with h5py.File('ADDE_CL_historial.h5', 'w') as f:
        iter_h5py = f.create_dataset("iteration", (FINAL_ITERATION, 1))
        pob_x_h5py = f.create_dataset("pob_x", (FINAL_ITERATION, n_var))
        pob_y_h5py = f.create_dataset("pob_y", (FINAL_ITERATION, 1))

    #---    Iteration register
        iter_h5py[0] = ITERATION
        pob_x_h5py[0] = np.copy(pob.x)
        pob_y_h5py[0] = pob.y
    f.close()    

else:
    #---    DDE 
    α = 0.8         # Step size [0, 0.9] - [0.45, 0.95]
    pc = 0.8        # Crossover probability - [0.1, 0.8]

    with h5py.File('ADDE_CL_historial.h5', 'r') as f:
        pob.x = np.copy(f["pob_x"][ITERATION - 1])
        pob.y = f["pob_y"][ITERATION - 1]

        id_iter = 2
        while pob.y == 0:
            pob.x = np.copy(f["pob_x"][ITERATION - id_iter])
            pob.y = f["pob_y"][ITERATION - id_iter]
            id_iter += 1
    f.close()
    
    #---    Randomly pick 3 candidate solution using indexes ids_vms
    # Generate IP_PORT_POOL
    IP_POOL = [f"10.0.0.{12+i}" for i in range(VMS)]        # vm1 is the server  machine
    IP_POOL.remove(MY_IP)

    IP_PORT_POOL = [f"{ip}:8888" for ip in IP_POOL]
    
    xa_ip_port = np.random.choice(IP_PORT_POOL, 1)
    IP_PORT_POOL.remove(xa_ip_port)

    xb_ip_port = np.random.choice(IP_PORT_POOL, 1)
    IP_PORT_POOL.remove(xb_ip_port)

    xc_ip_port = np.random.choice(IP_PORT_POOL, 1)

    time.sleep(np.random.randint(20,40,size = 1)[0])
    V1 = np.copy(send_request_py(xa_ip_port[0], 0, [])) 
    time.sleep(np.random.randint(20,40,size = 1)[0])   
    V2 = np.copy(send_request_py(xb_ip_port[0], 0, []))
    time.sleep(np.random.randint(20,40,size = 1)[0])
    Vb = np.copy(send_request_py(xc_ip_port[0], 0, []))

    Vd = V1 - V2                                            # The difference vector        
    Vm = Vb + α*Vd                                          # The mutant vector         
    Vm = np.clip(Vm,l_bounds,u_bounds)                      # make sure the mutant vector is in [lb,ub]
    
    # Create a trial vector by recombination
    Vt = np.zeros(n_var)
    rj = np.random.rand()                                   # index of the dimension that will under crossover regardless of pc
    for id_dim in range(n_var):
        rc = np.random.rand()
        if rc < pc or id_dim == rj:
            Vt[id_dim] = Vm[id_dim]                         # Perform recombination
        else:
            Vt[id_dim] = pob.x[id_dim]                      # copy from Vb
    
    # Obtain the OF of the trial vector
    vt_of = Run_WEAP_MODFLOW(path_output, str(ITERATION), initial_shape_HP, HP, active_cells, Vt, n_var_1, n_var_2, n_var_3, n_var, 
                             k_shape_1, k_shape_2, k_shape_3, k_shape_4, active_matriz, path_init_model, path_model, path_nwt_exe, 
                             path_obs_data)
    
    # Select the id_pop individual for the next generation
    if vt_of < pob.y:
        pob.x = np.copy(Vt)
        pob.y = vt_of

        # Send xi to the server
        send_request_py(MY_IP_PORT, 1, pob.x)

    # Register
    filename = open(f"ind_{MY_IP}_relation.txt", "a")
    filename.write(f"{ITERATION},{xa_ip_port}\n")
    filename.write(f"{ITERATION},{xb_ip_port}\n")
    filename.write(f"{ITERATION},{xc_ip_port}\n")
    filename.close()

    file = open(f"ind_{MY_IP}_8888.txt", "a")
    file.write(f"{ITERATION},{pob.y}\n")
    file.close()

    #---    Iteration register
    with h5py.File('ADDE_CL_historial.h5', 'a') as f:
        f["iteration"][ITERATION] = ITERATION
        f["pob_x"][ITERATION] = np.copy(pob.x)
        f["pob_y"][ITERATION] = pob.y
    f.close()
