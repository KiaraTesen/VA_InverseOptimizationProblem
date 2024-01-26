# -*- coding: utf-8 -*-

#---    Packages
import h5py
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

#---    Initial information
methodology = ['DPSO', 'DDE']
configuration = ['n = 20', 'n = 35', 'n = 50']                                          # 'n = 35', 'n = 50'
experiments = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7']                        # 'E4', 'E5'
iterations = list(range(201))

path_results = os.path.join(r'D:\1_PaperI') 

alpha_value = [90, 95, 99]

df_mean = pd.DataFrame()

fs_title = 21
fs_others = 18

for a in methodology:
    for b in configuration: 
        if b == 'n = 20':
            machines = list(range(2,22))
        elif b == 'n = 35':
            machines = list(range(2,37))
        elif b == 'n = 50':
            machines = list(range(2,52))
        
        df_y = pd.DataFrame()

        for i in experiments:
            for j in machines:
                path_experiment = os.path.join(path_results, a, b, i, str(a) + '_historial_vm' + str(j) + '.h5')

                #---    Lectura archivos h5
                with h5py.File(path_experiment, 'r') as f:
                    x = f["pob_x"][:]
                    #v = f["pob_v"][:]
                    y = f["pob_y"][:]
                    #x_best = f["pob_x_best"][:]
                    #y_best = f["pob_y_best"][:]
                    #w = f["w"][:]

                for k in iterations:
                    df_y.loc[k,"Y-vm" + str(j) + '-' + str(i)] = y[k, 0]
                    df_y.loc[df_y["Y-vm" + str(j) + '-' + str(i)] == 0, "Y-vm" + str(j) + '-' + str(i)] = np.nan

        #---    Resultados en escala logarítmica
        df_y_log = np.log(df_y)
        df_y_log.to_csv(os.path.join(path_results, 'Graphs', 'df_y_log_' + str(a) + '_' + str(b) + '.csv'))
    
        #---    Transpose to reorder
        df_y_log_T = df_y_log.transpose()
        print(df_y_log)
        """
        #---    BOXPLOT
        df = df_y
        column_list = df.columns
        df_concat = df.iloc[:,0]
        for m in range(len(column_list)-1):
            df_concat = pd.concat([df_concat, df.iloc[:,m+1]])
        df_concat = df_concat.reset_index()
        print(df_concat)
        del df_concat['index']
        df_concat = df_concat.dropna()
        print(df_concat)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.boxplot(df_concat)
        plt.savefig(os.path.join(path_results, 'Graphs', 'Boxplot_error_' + str(a) + '_' + str(b) + '.png'))       ## GENERAL
        plt.clf()
        """
        #---    Confidence Intervals
        for c in alpha_value:
            df_register = pd.DataFrame(index = ['Upper CI - ' + str(c) + '%', 'Lower CI - ' + str(c) + '%', 'Mean'])

            for m in iterations:
                df_value = df_y_log_T.iloc[:,m]
                df_value = df_value.dropna()

                CI = st.norm.interval(alpha = c/100, loc = np.mean(df_value), scale = st.sem(df_value))
                mean_value = np.mean(df_value)
                #print(m, mean_value, CI, df_value.size)

                Lower_CI, Upper_CI = CI[0], CI[1]
                
                df_register.loc['Upper CI - ' + str(c) + '%', str(m)] = Upper_CI
                df_register.loc['Lower CI - ' + str(c) + '%', str(m)] = Lower_CI
                df_register.loc['Mean', str(m)] = mean_value

            df_register_T = df_register.transpose()
            print(df_register_T)

            df_mean[str(a) + '; ' + str(b)] = df_register_T['Mean']

            #---    Graph 1
            Lower_bound = 3.5
            Upper_bound = 6.0

            fig, ax = plt.subplots(figsize=(14, 7))
            ax.plot(range(len(df_register_T)), df_register_T.loc[:,'Upper CI - ' + str(c) + '%'], color = "black", linewidth = 0.75, linestyle = 'dashed', label = 'Upper CI - ' + str(c) + '%')
            ax.plot(range(len(df_register_T)), df_register_T.loc[:,'Lower CI - ' + str(c) + '%'], color = "black", linewidth = 0.75, linestyle = 'dotted', label = 'Lower CI - ' + str(c) + '%')
            ax.plot(range(len(df_register_T)), df_register_T.loc[:,'Mean'], color = "#A52A2A", linewidth = 0.75, linestyle = 'solid', label = 'Mean')
            #ax.fill_between(x = range(len(df_register_T)), y1 = df_register_T.loc[:,'Upper CI - ' + str(alpha_value) + '%'], y2 =  df_register_T.loc[:,'Lower CI - ' + str(alpha_value) + '%'],  alpha = 0.2, color = "#1f77b4") # Polígono

            xlim = len(iterations)
            plt.xticks(range(0, xlim, 20), fontsize = fs_others)
            plt.xlim(0, xlim)
            plt.yticks(fontsize = fs_others)
            plt.ylim(Lower_bound, Upper_bound)

            if b == 'n = 20':
                title = 'NP = 20'
            elif b == 'n = 35':
                title = 'NP = 35'
            elif b == 'n = 50':
                title = 'NP = 50'
            plt.title(str(title), fontsize = fs_title, weight = "bold")
            plt.xlabel("Iterations", fontsize = fs_others, weight = "bold")
            plt.ylabel("log E", fontsize = fs_others, weight = "bold")
            plt.legend(loc='upper right', fontsize = fs_others)

            plt.savefig(os.path.join(path_results, 'Graphs', 'LogE_vs_iter_' + str(a) + '_' + str(b) + '_' + str(c) + '.png'), dpi = 1200)
            plt.savefig(os.path.join(path_results, 'Graphs', 'LogE_vs_iter_' + str(a) + '_' + str(b) + '_' + str(c) + '.eps'), format = 'eps', dpi = 1200)
            plt.clf()

print(df_mean)

#---    Graph 2
fig2, ax2 = plt.subplots(figsize = (16, 8))
ax2.plot(range(len(df_mean)), df_mean.loc[:, 'DPSO; n = 20'], color = "black", linewidth = 0.75, linestyle = 'solid', label = 'DPSO; n = 20')
ax2.plot(range(len(df_mean)), df_mean.loc[:, 'DDE; n = 20'], color = "#A52A2A", linewidth = 0.75, linestyle = 'solid', label = 'DDE; n = 20')
ax2.plot(range(len(df_mean)), df_mean.loc[:, 'DPSO; n = 35'], color = "black", linewidth = 0.75, linestyle = 'dashed', label = 'DPSO; n = 35')
ax2.plot(range(len(df_mean)), df_mean.loc[:, 'DDE; n = 35'], color = "#A52A2A", linewidth = 0.75, linestyle = 'dashed', label = 'DDE; n = 35')
ax2.plot(range(len(df_mean)), df_mean.loc[:, 'DPSO; n = 50'], color = "black", linewidth = 0.75, linestyle = 'dotted', label = 'DPSO; n = 50')
ax2.plot(range(len(df_mean)), df_mean.loc[:, 'DDE; n = 50'], color = "#A52A2A", linewidth = 0.75, linestyle = 'dotted', label = 'DDE; n = 50')

plt.xticks(range(0, xlim, 20), fontsize = fs_others)
plt.xlim(0, xlim)
plt.yticks(fontsize = fs_others)
plt.ylim(Lower_bound, Upper_bound)

plt.xlabel("Iteration", fontsize = fs_others, weight = "bold")
plt.ylabel("Log E", fontsize = fs_others, weight = "bold")
plt.legend(bbox_to_anchor = (0,1,5,0), mode = "expandir", ncol = 3, loc = 'lower left', fontsize = fs_others)

plt.savefig(os.path.join(path_results, 'Graphs', 'Mean_LogE_vs_iter.png'))
plt.savefig(os.path.join(path_results, 'Graphs', 'Mean_LogE_vs_iter.eps'), format = 'eps', dpi = 1200)
plt.clf()
