from os import path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class BasePairAgent:
    hosts = ['nome', 'me1', 'me2', 'me3', 'me12', 'me23', 'me123']
    abbr_hosts = {'nome': 'no-methyl', 'me1': 'methyl-5th', 'me2': 'methyl-7th', 'me3': 'methyl-9th',
                  'me12': 'methyl-5+7th', 'me23': 'methyl-7+9th', 'me123': 'methyl-5+7+9th'}
    d_colors = {'nome': 'black', 'me1': 'slateblue', 'me2': 'steelblue', 'me3': 'forestgreen', 'me12': 'darkred', 'me23': 'orange', 'me123': 'gold'}
    hosts_group = [['nome', 'me1'],
                   ['nome', 'me12'],
                   ['nome', 'me123'],
                   ['me1', 'me2', 'me3'],
                   ['me12', 'me23'],
                   ['me1', 'me123'],
                   ['me12', 'me123']]    ## , 'me2', 'me3', 'me123'

    def __init__(self, rootfolder, time_interval):
        self.rootfolder = rootfolder
        self.type_na = 'bdna+bdna'
        self.time_interval = time_interval
        
        self.start_bp = 3
        self.end_bp = 10
        self.n_bp = self.end_bp - self.start_bp + 1

        self.lbfz = 12
        self.lgfz = 12
        self.ticksize = 10

        self.parameters = ['shear', 'buckle', 'stretch', 'propeller', 'stagger', 'opening']

    def histogram_groups(self, figsize, parameter, bins, xlines, xlim, ylim):
        nrows = 1
        ncols = 7
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, sharey=True, sharex=True)
        col_id = 0
        xlabel = self.get_xlabel(parameter)
        for hosts in self.hosts_group:
            ax = axes[col_id]
            for host in hosts:
                data = self.get_data(host, parameter)
                ax.hist(data, bins=bins, density=True, color=self.d_colors[host], alpha=0.5, label=self.abbr_hosts[host])
            for xvalue in xlines:
                ax.axvline(xvalue, color='black', alpha=0.2)
            ax.set_xlabel(xlabel,fontsize=self.lbfz)
            ax.set_ylabel('Probabiity Density', fontsize=self.lbfz)
            ax.legend(frameon=False, fontsize=self.lgfz)
            ax.tick_params(axis='both', labelsize=self.ticksize)
            if xlim is not None:
                ax.set_xlim(xlim)
            if ylim is not None:
                ax.set_ylim(ylim)
            col_id += 1
        return fig, axes

    def histogram_six_sys_one_para(self, figsize, parameter, bins):
        nrows = 2
        ncols = 3
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, sharey=True, sharex=True)
        d_axes = self.get_daxes(axes, nrows, ncols)
        for host in self.hosts:
            data = self.get_data(host, parameter)
            ax = d_axes[host]
            ax.hist(data, bins=bins, density=True, color=self.d_colors[host], alpha=0.4)
            ax.set_title(self.abbr_hosts[host])
            ax.set_xlabel(parameter)
            ax.set_ylabel('Probabiity Density')
            ax.legend(loc = 'upper left')
        return fig, axes

    def get_xlabel(self, parameter):
        if parameter in ['shear', 'stretch', 'stagger']:
            return f'{parameter}(Å)'
        else:
            return f'{parameter}(°)'

    def get_daxes(self, axes, nrows, ncols):
        d_axes = dict()
        host_id = 0
        for row_id in range(nrows):
            for col_id in range(ncols):
                host = self.hosts[host_id]
                d_axes[host] = axes[row_id, col_id]
                host_id += 1
        return d_axes

    def get_data(self, host, parameter):
        host_time_folder = path.join(self.rootfolder, host, self.time_interval)
        fname = path.join(host_time_folder, f'{parameter}.csv')
        df = pd.read_csv(fname, index_col='Frame-ID')
        n_frame = df.shape[0]
        temp_array = np.zeros((n_frame, self.n_bp))
        col_id = 0
        for bp_id in range(self.start_bp, self.end_bp+1):
            temp_array[:,col_id] = df[f'bp{bp_id}']
            col_id += 1
        return np.ndarray.flatten(temp_array)

class BaseStepAgent(BasePairAgent):
    d_bimodal_label = {'atat_21mer': ('5\'-TA-3\'', '5\'-AT-3\''),
                       'gcgc_21mer': ('5\'-CG-3\'', '5\'-GC-3\''),
                       'ctct_21mer': ('5\'-TC-3\'', '5\'-CT-3\''),
                       'tgtg_21mer': ('5\'-GT-3\'', '5\'-TG-3\'')}

    def __init__(self, rootfolder, time_interval):
        super().__init__(rootfolder, time_interval)

    def get_xlabel(self, parameter):
        if parameter in ['shift', 'slide', 'rise']:
            return f'{parameter}(Å)'
        else:
            return f'{parameter}(°)'

    def histogram_bimodal(self, figsize, parameter, bins, xlines, xlim, ylim):
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=figsize, sharey=True, sharex=True)
        colors = ['blue', 'red']
        xlabel = self.get_xlabel(parameter)
        row_id = 0
        for host in ['atat_21mer', 'gcgc_21mer', 'ctct_21mer']:
            data1, data2 = self.get_bimodal_data(host, parameter)
            for col_id, data in enumerate([data1, data2]):
                ax = axes[row_id, col_id]
                label = f'{self.abbr_hosts[host]}:{self.d_bimodal_label[host][col_id]}'
                ax.hist(data, bins=bins, density=True, color=colors[col_id], alpha=0.4, 
                label=label)
                for xvalue in xlines:
                    ax.axvline(xvalue, color='grey', alpha=0.2)
                ax.set_xlabel(xlabel,fontsize=self.lbfz)
                ax.set_ylabel('Probabiity Density', fontsize=self.lbfz)
                ax.legend(frameon=False, fontsize=self.lgfz)
                ax.tick_params(axis='both', labelsize=self.ticksize)
                if xlim is not None:
                    ax.set_xlim(xlim)
                if ylim is not None:
                    ax.set_ylim(ylim)
            row_id += 1     
        return fig, ax

    def get_data(self, host, parameter):
        host_time_folder = path.join(self.rootfolder, host, self.time_interval)
        fname = path.join(host_time_folder, f'{parameter}.csv')
        df = pd.read_csv(fname, index_col='Frame-ID')
        n_frame = df.shape[0]
        temp_array = np.zeros((n_frame, self.n_bp))
        col_id = 0
        for bp_id in range(self.start_bp, self.end_bp):
            temp_array[:,col_id] = df[f'bp{bp_id}_bp{bp_id+1}']
            col_id += 1
        temp_array_2 = np.ndarray.flatten(temp_array)
        zero_indice = np.isclose(temp_array_2, 0)
        return temp_array_2[~zero_indice]

    def get_bimodal_data(self, host, parameter):
        host_time_folder = path.join(self.rootfolder, host, self.time_interval)
        fname = path.join(host_time_folder, f'{parameter}.csv')
        df = pd.read_csv(fname, index_col='Frame-ID')
        n_frame = df.shape[0]

        temp_array = np.zeros((n_frame, self.n_bp))
        col_id = 0
        for bp_id in range(self.start_bp, self.end_bp):
            temp_array[:,col_id] = df[f'bp{bp_id}_bp{bp_id+1}']
            col_id += 1

        temp_array_1 = temp_array[::2]
        temp_array_2 = temp_array[1::2]

        temp_array_1_flatten = np.ndarray.flatten(temp_array_1)
        temp_array_2_flatten = np.ndarray.flatten(temp_array_2)
        zero_indice_1 = np.isclose(temp_array_1_flatten, 0)
        zero_indice_2 = np.isclose(temp_array_2_flatten, 0)

        return temp_array_1_flatten[~zero_indice_1], temp_array_2_flatten[~zero_indice_2]

class GrooveAgent(BasePairAgent):

    def __init__(self, rootfolder, time_interval):
        super().__init__(rootfolder, time_interval)
        self.start_bp = 3
        self.end_bp = 10
        self.n_bp = self.end_bp - self.start_bp + 1

    def get_xlabel(self, parameter):
        return f'{parameter}(Å)'

    def get_data(self, host, parameter):
        host_time_folder = path.join(self.rootfolder, host, self.time_interval)
        fname = path.join(host_time_folder, f'{parameter}.csv')
        df = pd.read_csv(fname, index_col='Frame-ID')
        n_frame = df.shape[0]
        temp_array = np.zeros((n_frame, self.n_bp))
        col_id = 0
        for bp_id in range(self.start_bp, self.end_bp+1):
            temp_array[:,col_id] = df[f'label{bp_id}']
            col_id += 1
        return np.ndarray.flatten(temp_array)
