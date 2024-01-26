# -*- coding: utf-8 -*-

#---    Packages
#import matplotlib as mpl
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
import math
import hydroeval as he
import warnings
warnings.filterwarnings('ignore')

#---    Initial information

#---    DPSO
methodology = 'DPSO'        
configuration = 'n = 50'
best_experiment = 'E2'
best_result = 'vm41'
best_iteration = 199
best_shape = 'Elements_iter_' + str(best_iteration) + '.shp'
best_q = 'iter_' + str(best_iteration) + '_Streamflow_gauges.csv'
best_w = 'iter_' + str(best_iteration) + '_Wells_simulation.csv'
path_results = os.path.join(r'D:\1_PaperI', methodology, configuration) 

#---    DDE
methodology_2 = 'DDE'        
configuration_2 = 'n = 35'
best_experiment_2 = 'E7'
best_result_2 = 'vm27'
best_iteration_2 = 192
best_shape_2 = 'Elements_iter_' + str(best_iteration_2) + '.shp'
best_q_2 = 'iter_' + str(best_iteration_2) + '_Streamflow_gauges.csv'
best_w_2 = 'iter_' + str(best_iteration_2) + '_Wells_simulation.csv'
path_results_2 = os.path.join(r'D:\1_PaperI', methodology_2, configuration_2) 

elements_init = 'Elements_initial_unique_value_v2'

variables = ['kx', 'sy'] #

#---    Streamflow analysis
df_q = pd.read_csv(os.path.join(path_results, best_experiment, best_result, 'iter_' + str(best_iteration), best_q), skiprows = 3)
df_q = df_q.set_index('Statistic')
df_q = df_q.set_index(pd.to_datetime(df_q.index))
df_q = df_q.iloc[36:,:]
#print(df_q)

df_q_2 = pd.read_csv(os.path.join(path_results_2, best_experiment_2, best_result_2, 'iter_' + str(best_iteration_2), best_q_2), skiprows = 3)
df_q_2 = df_q_2.set_index('Statistic')
df_q_2 = df_q_2.set_index(pd.to_datetime(df_q_2.index))
df_q_2 = df_q_2.iloc[36:,:]
#print(df_q_2)

df_q_obs = pd.read_csv(r'..\data\ObservedData\StreamflowGauges_KPR_vf.csv', skiprows = 2)
df_q_obs = df_q_obs.iloc[36:,:]
#print(df_q_obs)

DF_q = pd.DataFrame()
DF_q['Modeled - ADPSO-CL'] = np.array(df_q['Modeled'])
DF_q['Modeled - ADDE-CL'] = np.array(df_q_2['Modeled'])
DF_q['Observed'] = np.array(df_q_obs['Observed'])
DF_q = DF_q.set_index(pd.to_datetime(df_q.index))

#---    Metrics
rmse_q = mean_squared_error(np.array(df_q_obs['Observed']), np.array(df_q['Modeled']), squared = False)
nse_q = he.evaluator(he.nse,np.array(df_q['Modeled']), np.array(df_q_obs['Observed']))
kge_q, r, alpha, beta = he.evaluator(he.kge, np.array(df_q['Modeled']), np.array(df_q_obs['Observed'])) # kge, r, alpha, beta
pbias_q = he.evaluator(he.pbias, np.array(df_q['Modeled']), np.array(df_q_obs['Observed']))
mae_q = mean_absolute_error(np.array(df_q_obs['Observed']), np.array(df_q['Modeled']))
corr_matrix = np.corrcoef(np.array(df_q_obs['Observed']), np.array(df_q['Modeled']))[0,1]
r_sq = corr_matrix**2
print('DPSO-Q', round(rmse_q,3), round(mae_q,3), round(kge_q[0],3))

rmse_q_2 = he.evaluator(he.rmse, np.array(df_q_2['Modeled']), np.array(df_q_obs['Observed']))
nse_q_2 = he.evaluator(he.nse, np.array(df_q_2['Modeled']), np.array(df_q_obs['Observed']))
kge_q_2, r_2, alpha_2, beta_2 = he.evaluator(he.kge, np.array(df_q_2['Modeled']), np.array(df_q_obs['Observed'])) # kge, r, alpha, beta
pbias_q_2 = he.evaluator(he.pbias, np.array(df_q_2['Modeled']), np.array(df_q_obs['Observed']))
mae_q_2 = mean_absolute_error(np.array(df_q_obs['Observed']), np.array(df_q_2['Modeled']))
corr_matrix_2 = np.corrcoef(np.array(df_q_obs['Observed']), np.array(df_q_2['Modeled']))[0,1]
r_sq_2 = corr_matrix_2**2
print('DDE-Q', round(rmse_q_2[0],3), round(mae_q_2,3), round(kge_q_2[0],3),)

#---    Graph
fig = plt.subplots(figsize=(14, 7))
plt.plot(DF_q['Observed'], label = 'Obs', color = "black", linewidth = 0.75)
plt.plot(DF_q['Modeled - ADPSO-CL'], label = 'ADPSO-CL', color = "red", linewidth = 0.75)
plt.plot(DF_q['Modeled - ADDE-CL'], label = 'ADDE-CL', color = "blue", linewidth = 0.75)
#plt.plot(DF_q['Initial value'], label = 'Init', color = "blue", linewidth = 0.25)

ymin = min(DF_q['Modeled - ADPSO-CL'].to_numpy().min(), DF_q['Modeled - ADDE-CL'].to_numpy().min(), DF_q['Observed'].to_numpy().min())
ymax = max(DF_q['Modeled - ADPSO-CL'].to_numpy().max(), DF_q['Modeled - ADDE-CL'].to_numpy().max(), DF_q['Observed'].to_numpy().max())
dif_v = ymax - ymin

plt.ylim(0, round(ymax + dif_v/2))
plt.ylabel('Streamflow ($m^{3}/s$)', fontsize = 18)
plt.xlabel('Years', fontsize = 18)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)
plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')
plt.title('Streamflow gauge', fontsize = 21, fontweight='bold')
plt.legend(loc='upper right', fontsize = 18)

plt.savefig(os.path.join(r'D:\1_PaperI\Graphs', 'Obs_vs_Sim_Q_.png'))
plt.clf()

#---    Observation wells
obs_well = pd.read_csv(r'..\data\ObservedData\Wells_observed.csv', skiprows = 3)
obs_well = obs_well.iloc[36:,:]
obs_well = obs_well.set_index(pd.to_datetime(df_q.index))
#print(obs_well)

ow = obs_well.columns

#---    ADPSO-CL
sim_well = pd.read_csv(os.path.join(path_results, best_experiment, best_result, 'iter_' + str(best_iteration), best_w), skiprows = 3)
sim_well = sim_well.iloc[36:,:]
sim_well = sim_well.set_index(pd.to_datetime(df_q.index))

#---    ADDE-CL
sim_well_2 = pd.read_csv(os.path.join(path_results_2, best_experiment_2, best_result_2, 'iter_' + str(best_iteration_2), best_w_2), skiprows = 3)
sim_well_2 = sim_well_2.iloc[36:,:]
sim_well_2 = sim_well_2.set_index(pd.to_datetime(df_q_2.index))
#print(sim_well)

for p in ow[1:]:
    #---    Metrics
    rmse_w = he.evaluator(he.rmse, sim_well[p], obs_well[p])
    nse_w = he.evaluator(he.nse, sim_well[p], obs_well[p])
    kge_w, r, alpha, beta = he.evaluator(he.kge, sim_well[p], obs_well[p]) # kge, r, alpha, beta
    pbias_w = he.evaluator(he.pbias, sim_well[p], obs_well[p])
    mae_w = mean_absolute_error(obs_well[p], sim_well[p])
    corr_matrix_w = np.corrcoef(np.array(obs_well[p]), np.array(sim_well[p]))
    corr_w = corr_matrix_w[0,1]
    r_sq_w = corr_w**2
    print('DPSO-'+p, round(rmse_w[0],3), round(mae_w,3), round(kge_w[0],3))

    #---    Metrics
    rmse_w_2 = he.evaluator(he.rmse, sim_well_2[p], obs_well[p])
    nse_w_2 = he.evaluator(he.nse, sim_well_2[p], obs_well[p])
    kge_w_2, r_2, alpha_2, beta_2 = he.evaluator(he.kge, sim_well_2[p], obs_well[p]) # kge, r, alpha, beta
    pbias_w_2 = he.evaluator(he.pbias, sim_well_2[p], obs_well[p])
    mae_w_2 = mean_absolute_error(obs_well[p], sim_well_2[p])
    corr_matrix_w_2 = np.corrcoef(np.array(obs_well[p]), np.array(sim_well_2[p]))
    corr_w_2 = corr_matrix_w_2[0,1]
    r_sq_w_2 = corr_w_2**2
    print('DDE-'+p, round(rmse_w_2[0],3), round(mae_w_2,3), round(kge_w_2[0],3))

    #---    Graph
    fig = plt.subplots(figsize=(14, 7))
    plt.plot(obs_well[p], label = 'Obs', color = "black", linewidth = 0.75)
    plt.plot(sim_well[p], label = 'ADPSO-CL', color = "red", linewidth = 0.75)
    plt.plot(sim_well_2[p], label = 'ADDE-CL', color = "blue", linewidth = 0.75)

    ymin = min(obs_well[p].to_numpy().min(), sim_well[p].to_numpy().min(), sim_well_2[p].to_numpy().min())
    ymax = max(obs_well[p].to_numpy().max(), sim_well[p].to_numpy().max(), sim_well_2[p].to_numpy().max())
    dif_v = ymax - ymin

    plt.ylim(ymin - (dif_v/10), ymax + dif_v)
    plt.ylabel('Groundwater table (m)', fontsize = 18)
    plt.xlabel('Years', fontsize = 18)
    plt.xticks(fontsize = 18)
    plt.yticks(fontsize = 18)
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')
    plt.title('Observation well - ' + str(p), fontsize = 21, fontweight='bold')
    plt.legend(loc='upper right', fontsize = 18)

    plt.savefig(os.path.join(r'D:\1_PaperI\Graphs', 'Obs_vs_Sim_Well_' + str(p) + '.png'))
    plt.clf()