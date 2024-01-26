# -*- coding: utf-8 -*-

#---    Packages
#import matplotlib as mpl
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import geopandas as gpd
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
import math
import hydroeval as he
import warnings
warnings.filterwarnings('ignore')

#---    Initial information
methodology = 'DPSO'                #'DDE'
configuration = 'n = 50'
path_results = os.path.join(r'D:\1_PaperI', methodology, configuration) 
elements_init = 'Elements_initial_unique_value_v2'

best_experiment = 'E2'
best_result = 'vm41'
best_iteration = 199

best_shape = 'Elements_iter_' + str(best_iteration) + '.shp'
best_q = 'iter_' + str(best_iteration) + '_Streamflow_gauges.csv'
best_w = 'iter_' + str(best_iteration) + '_Wells_simulation.csv'

variables = ['kx', 'sy'] #

#---    ERROR PORCENTUAL - K y Sy
shape = gpd.read_file(os.path.join(path_results, best_experiment, best_result, 'iter_' + str(best_iteration), best_shape))
shape_obs = gpd.read_file(r'..\data\GIS\Final_version\Elements_FA_vf.shp')

for n in variables:
    globals()[n + '_obs'] = shape_obs[n]
    globals()[n + '_sim'] = shape[n]

    locals()['dif_' + n] = abs(globals()[n + '_sim'] - globals()[n + '_obs'])   
    globals()['error_' + n] = (locals()['dif_' + n] / globals()[n + '_obs']) * 100
    print(globals()['error_' + n])
    #globals()['error_' + n] = globals()['error_' + n].fillna(0)

    globals()['matriz_error_' + n] = (globals()['error_' + n].to_numpy()).reshape((84, 185))

    globals()['MAPE_e2' + n] = np.where(globals()['error_' + n] == np.inf, 0, globals()['error_' + n])
    sum_MAPE_epre = np.sum(globals()['MAPE_e2' + n])
    MAPE_e = sum_MAPE_epre / 7536
    print(MAPE_e)

    #---    Graph
    plt.figure(figsize = (14,7))
    im = plt.imshow(globals()['matriz_error_' + n], cmap = 'viridis', norm = colors.LogNorm())

    im_ratio = globals()['matriz_error_' + n].shape[0]/globals()['matriz_error_' + n].shape[1]
    plt.colorbar(im)
    plt.text(140, 4.75, 'MAPE: ' + str(round(MAPE_e,2)) + '%', fontsize = 18)
    plt.xticks(fontsize = 18)
    plt.yticks(fontsize = 18)
    #plt.colorbar(fraction=0.047*im_ratio, extend='max')
    plt.clim(0.001, 10000)

    if n == 'kx':
        plt.title('RE (%) - K', fontsize = 21, weight = "bold")
    else:
        plt.title('RE (%) - Sy', fontsize = 21, weight = "bold")
    plt.xlabel('Column', fontsize = 18)
    plt.ylabel('Row', fontsize = 18 )
    
    plt.savefig(os.path.join(r'D:\1_PaperI', 'Graphs', 'Error_relativo_' + n + '_' + methodology + '_best_experiment.png'))
    #plt.show()
    plt.clf()

#---    Initial information
methodology = 'DDE'                #'DDE'
configuration = 'n = 35'
path_results = os.path.join(r'D:\1_PaperI', methodology, configuration) 
elements_init = 'Elements_initial_unique_value_v2'

best_experiment = 'E7'
best_result = 'vm27'
best_iteration = 192

best_shape = 'Elements_iter_' + str(best_iteration) + '.shp'
best_q = 'iter_' + str(best_iteration) + '_Streamflow_gauges.csv'
best_w = 'iter_' + str(best_iteration) + '_Wells_simulation.csv'

variables = ['kx', 'sy'] #

#---    ERROR PORCENTUAL - K y Sy
shape = gpd.read_file(os.path.join(path_results, best_experiment, best_result, 'iter_' + str(best_iteration), best_shape))
shape_obs = gpd.read_file(r'..\data\GIS\Final_version\Elements_FA_vf.shp')

for n in variables:
    globals()[n + '_obs'] = shape_obs[n]
    globals()[n + '_sim'] = shape[n]

    locals()['dif_' + n] = abs(globals()[n + '_sim'] - globals()[n + '_obs'])   
    globals()['error_' + n] = (locals()['dif_' + n] / globals()[n + '_obs']) * 100
    print(globals()['error_' + n])
    #globals()['error_' + n] = globals()['error_' + n].fillna(0)

    globals()['matriz_error_' + n] = (globals()['error_' + n].to_numpy()).reshape((84, 185))

    globals()['MAPE_e2' + n] = np.where(globals()['error_' + n] == np.inf, 0, globals()['error_' + n])
    sum_MAPE_epre = np.sum(globals()['MAPE_e2' + n])
    MAPE_e = sum_MAPE_epre / 7536
    print(MAPE_e)

    #---    Graph
    plt.figure(figsize = (14,7))
    im = plt.imshow(globals()['matriz_error_' + n], cmap = 'viridis', norm = colors.LogNorm())

    im_ratio = globals()['matriz_error_' + n].shape[0]/globals()['matriz_error_' + n].shape[1]
    plt.colorbar(im)
    plt.text(140, 4.75, 'MAPE: ' + str(round(MAPE_e,2)) + '%', fontsize = 18)
    plt.xticks(fontsize = 18)
    plt.yticks(fontsize = 18)
    #plt.colorbar(fraction=0.047*im_ratio, extend='max')
    plt.clim(0.001, 10000)

    if n == 'kx':
        plt.title('RE (%) - K', fontsize = 21, weight = "bold")
    else:
        plt.title('RE (%) - Sy', fontsize = 21, weight = "bold")
    plt.xlabel('Column', fontsize = 18)
    plt.ylabel('Row', fontsize = 18 )
    
    plt.savefig(os.path.join(r'D:\1_PaperI', 'Graphs', 'Error_relativo_' + n + '_' + methodology + '_best_experiment.png'))
    #plt.show()
    plt.clf()