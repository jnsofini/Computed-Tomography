#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:35:45 2020

@author: jnsofini

This folder contain helper functions that are used to run the program
"""

import matplotlib.pyplot as plt
import numpy as np
#import os.path as path
import seaborn as sns
import matplotlib.gridspec as gridspec
#import pandas as pd
from collections import defaultdict
from functools import partial #used to call collection with numpy


sns.set()
import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          #'figure.figsize': (15, 5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


def getEnergy(fh, cutoff=10e5):
    '''
    Gets a container of energies from a text file. 
    The file incident is described in detainls in the markdown
    It also takes a cut off to limit howmany events are read
    
    Inputs
    -------
    fh is the input file handle with d1, x1, y1, d2, x2, y2, e2
    
    cutoff optional number of events to analyze
    
    Return
    ------
    
    detectors is a dict containing as many items as there are detectors in the data
     
    '''
    detectors = {str(i):[] for i in range(4)} #dict to hold the energies from each of the four detectors
    fh = open(fh, "r")
    for i, line in enumerate(fh):
        ''' 
        Reads and the split each line. The split line contains 11 items. 
        First 4 are coincidence, 6 are cordinates, 
        (d x y e)_1 (d x y e)_2 and the last one is time    
        '''
        if i >= cutoff: break # NOT all events are necessary
        d1, x1, y1, e1, d2, x2, y2, e2 = line.split()
        #d1 and d2 are text
        detectors[d1].append(int(e1))
        detectors[d2].append(int(e2))
        
    return detectors


#def plotEnergyHist_v1(energy, bins=25):
#    '''
#    Takes energy dict and plot it on a grid of 4 x len(energy)//4
#    Inputs
#    ------
#    energy: dict containing energy for each of the detectors
#    
#    Create fig and axes and plot each of the detector data on a separate axis
#    in a grid len(energy)//4 X 4.  
#    '''
#    
#    nrows = len(energy)//4
#    fig, axes = plt.subplots(nrows,4, sharey=True, sharex=True, figsize = (16,3*nrows))
#    fig.subplots_adjust(hspace=0.25)
#    
#    
#
#    for ax, det in zip(axes.flatten(), energy.keys()):
#        sns.distplot(a=energy[det], bins=bins, ax=ax, kde=True)
#        ax.set(title='Detector: '+det, xlabel='Energy(keV)')
#        if int(det)%4==0: #removed names with assumption that the keys are numbers
#            ax.set(ylabel='# of LORs')
#    plt.show()




class SeabornFig2Grid():

    def __init__(self, seaborngrid, fig,  subplot_spec):
        self.fig = fig
        self.sg = seaborngrid
        self.subplot = subplot_spec
        if isinstance(self.sg, sns.axisgrid.FacetGrid) or \
            isinstance(self.sg, sns.axisgrid.PairGrid):
            self._movegrid()
        elif isinstance(self.sg, sns.axisgrid.JointGrid):
            self._movejointgrid()
        self._finalize()

    def _movegrid(self):
        """ Move PairGrid or Facetgrid """
        self._resize()
        n = self.sg.axes.shape[0]
        m = self.sg.axes.shape[1]
        self.subgrid = gridspec.GridSpecFromSubplotSpec(n,m, subplot_spec=self.subplot)
        for i in range(n):
            for j in range(m):
                self._moveaxes(self.sg.axes[i,j], self.subgrid[i,j])

    def _movejointgrid(self):
        """ Move Jointgrid """
        h= self.sg.ax_joint.get_position().height
        h2= self.sg.ax_marg_x.get_position().height
        r = int(np.round(h/h2))
        self._resize()
        self.subgrid = gridspec.GridSpecFromSubplotSpec(r+1,r+1, subplot_spec=self.subplot)

        self._moveaxes(self.sg.ax_joint, self.subgrid[1:, :-1])
        self._moveaxes(self.sg.ax_marg_x, self.subgrid[0, :-1])
        self._moveaxes(self.sg.ax_marg_y, self.subgrid[1:, -1])

    def _moveaxes(self, ax, gs):
        #https://stackoverflow.com/a/46906599/4124317
        ax.remove()
        ax.figure=self.fig
        self.fig.axes.append(ax)
        self.fig.add_axes(ax)
        ax._subplotspec = gs
        ax.set_position(gs.get_position(self.fig))
        ax.set_subplotspec(gs)

    def _finalize(self):
        plt.close(self.sg.fig)
        self.fig.canvas.mpl_connect("resize_event", self._resize)
        self.fig.canvas.draw()

    def _resize(self, evt=None):
        self.sg.fig.set_size_inches(self.fig.get_size_inches())
        
 
#-------------------------------------------------------------------------------
        
def plotEnergyKDE(energy, bins=25):
    '''
    Takes energy dict and plot it on a grid of 4 x len(energy)//4
    Inputs
    ------
    energy: dict containing energy for each of the detectors
    
    Create fig and axes
    Plot each the energy distribution for detector as a 2D together
    with the projections in a len(energy)//4 X 2.  
    '''
    keys = [*energy] #get a list of the keys
    dict1, dict2 = keys[:len(keys)//2], keys[len(keys)//2:]

    grids = []

    for i, j in zip(dict1, dict2):
        g = sns.jointplot(x=energy[i],
                               y=energy[j], kind="hex", color="b")
        g.set_axis_labels('Energy_det_'+i+' (keV)', 'Energy_det_'+j+' (keV)', fontsize=16)
        grids.append(g)
    
    #Create a figuregrid to hold the plots
    fig = plt.figure(figsize=(14,6))
    gs = gridspec.GridSpec(1, 2)
    
    #Send the fig to the seaborn object and add the figures
    SeabornFig2Grid(grids[0], fig, gs[0])
    SeabornFig2Grid(grids[1], fig, gs[1])   
    
    
    plt.show()
    
#-------------------------------------------------------------------------------
def plotEnergyHist(energy, bins=25):
    '''
    Takes energy dict and plot it on a grid of 4 x len(energy)//4
    Inputs
    ------
    energy: dict containing energy for each of the detectors
    
    Create fig and axes and plot each of the detector data on a separate axis
    in a grid len(energy)//4 X 4.  
    '''
    
    nrows = len(energy)//2
    fig, axes = plt.subplots(nrows,2, sharey=True, sharex=True, figsize = (8,3*nrows))
    fig.subplots_adjust(hspace=0.5)
        

    for ax, det in zip(axes.flatten(), energy.keys()):
        sns.distplot(a=energy[det], bins=bins, ax=ax, kde=True)
        ax.set(title='Detector: '+det)
        
    #Labelling axis
    for xax, yax in zip(axes[-1,:], axes[:,0]):             
        yax.set(ylabel="LORs")
        xax.set(xlabel='Energy(keV)')         
         
    plt.show()
    
#-------------------------------------------------------------------------------


def getLORS(fh, id_):
    '''
    Takes a file and of coincidences and get the LORs pairs and group them for each detector pairs: 
    Here we have two detector. Reads reads line by line, and counts the number of events and create
    a 2D histogram
    
    Parameters
    ----------
    fh : input file name
    id : specify the coincidence detector for the norm data
    lors_norm : arrays of LOR sum for each pair
    
    Variables
    ---------
    DET_SIZE : Number por pixels in the detector module so number of LOR pairs lor_size = DET_SIZE^2
    lor_size :   
    '''
    if (id_==13):
        coin_ = 0 # was previoulsy wrongly set to 1
    elif (id_==24): 
        coin_ = 1
    else :
        raise ValueError('Wrong detector ID: {}'.format(id_))

    
    DET_SIZE = 35
    lors_norm = np.zeros((DET_SIZE*DET_SIZE, DET_SIZE*DET_SIZE)) #2x2 array

    fh = open(fh, "r")
    for i,  line in enumerate(fh):
        ''' 
        Reads and the split each line of 8 items. First four (d x y e)_1 for one detector and 
        the other four (d x y e)_2 for its coincidence detector    
        '''        
        d1, x1, y1, e1, d2, x2, y2, e2 = list(map(int, line.split()))
        #d1, x1, y1, e1, d2, x2, y2, e2 = [int(s) for s in line.split()] #split line, convert to ints
        #if i==1e8: break
        if (d1 == coin_):
            lors_norm[x1 + DET_SIZE*y1, x2 + DET_SIZE*y2] += 1 #Pick pair that coin

    fh.close()
    
    return lors_norm
    


#---------------------------------------------------------------------------------------------------------
def fansumAlgorithm(data):
    '''
    Apply the fansum algorithm to two input arrays and return an array of the same dimention:
    Parameters:
    -----------
    data: dict containing the LORs data for various pairs with keys
    d24 and d13 
    
    returns:
    -------
    lors_fan_sum_ dict with elements correspojding to input
        Improved statistics for fan_sum_LORS_13 & fan_sum_LORS_24: 
    '''
    #create variables
    #lors_fan_sum_ = [np.zeros(np.shape(det_data)) for det_data in data]
    
    #assert(len(lors_fan_sum_) == 2), "Only TWO data arrays are expected"
    
    #lors_fan_sum_[0] = np.sum(data[0], axis=1, keepdims=True)\
    #                                 *np.sum(data[0], axis=0, keepdims=True)/np.sum(data[0])
    #lors_fan_sum_[1] = np.sum(data[1], axis=1, keepdims=True)\
    #                                 *np.sum(data[1], axis=0, keepdims=True)/np.sum(data[1])
    lors_fansum = {}
    for key, val in data.items():
        lors_fansum[key] = np.sum(val, axis=1, keepdims=True)*\
                             np.sum(val, axis=0, keepdims=True)/np.sum(val)
        

    return lors_fansum

def fan_sum_algo(*data):
    '''
    Apply the fansum algorithm to two input arrays and return an array of the same dimention:
    Parameters:
    -----------
    data: array containing the LORs for the detector pair 24
    and detector pair 13 
    
    returns:
    -------
    lors_fan_sum_ list of two elements: Improved statistics for fan_sum_LORS_13 & fan_sum_LORS_24: 
    '''
    #create variables
    #lors_fan_sum_ = [np.zeros(np.shape(det_data)) for det_data in data]
    
    #assert(len(lors_fan_sum_) == 2), "Only TWO data arrays are expected"
    
    #lors_fan_sum_[0] = np.sum(data[0], axis=1, keepdims=True)\
    #                                 *np.sum(data[0], axis=0, keepdims=True)/np.sum(data[0])
    #lors_fan_sum_[1] = np.sum(data[1], axis=1, keepdims=True)\
    #                                 *np.sum(data[1], axis=0, keepdims=True)/np.sum(data[1])
    lors_fan_sum_ = []
    for item in data:
        lors_fan_sum_.append(np.sum(item, axis=1, keepdims=True)*\
                             np.sum(item, axis=0, keepdims=True)/np.sum(item))
        


    return lors_fan_sum_
#---------------------------------------------------------------------------------------------
    
def plotNormCoeff(data, bins=None):
    '''
    Make a plots of the number of LORs vs pixels and the histogram
    for a selected detectopr pixel
    '''
    if bins == None:
        maxx, minn = np.max(data), np.min(data)
        bins = int((maxx-minn)/2)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=False, figsize = (15,4))
    
    ax1.plot(data, '--', drawstyle='steps-pre')
    sns.distplot(a=data, bins=bins, ax=ax2, kde=True)        
    ax1.set(xlabel='Pixel', ylabel='LORs')
    ax2.set(xlabel='Count', ylabel='Freq')
    
    #return fig
    #ax2.set_title('Detecors 24')
    
#---------------------------------------------------------------------------------------------
    
def plotNormComparison(data, fansum_data, binsf=None):
    '''
    Make a list cpmparison 2x2 plot of the LORS and fansum LORS
    
    Inputs
    ------
    
    data is the data without fansum
    fansum_data is the data with the fansum applied
    binsf is the number of bins for the fansum, optional.
    
    '''
    maxx, minn = np.max(data), np.min(data)
    bins = int((maxx-minn)/2)
    #print(maxx, minn, bins)
    if binsf == None: binsf = bins
    fig, ax = plt.subplots(2, 2, sharex=False, figsize = (12,8))

    ax[0,0].plot(data, '--', drawstyle='steps-pre')
    sns.distplot(a=data, bins=bins, ax=ax[0,1], kde=True)
    ax[1,0].plot(fansum_data, '--', drawstyle='steps-pre')
    sns.distplot(a=fansum_data, bins=binsf, ax=ax[1,1], kde=True)

        
    ax[0,0].set(ylabel='LORs')
    ax[0,1].set(ylabel='Freq')
    ax[1,0].set(xlabel='Pixel', ylabel='LORs')
    ax[1,1].set(xlabel='Count', ylabel='Freq')
    #ax2.set_title('Detecors 24')
    
 
#---------------------------------------------------------------------------------------------  
def arrayToJoint(X):
    #initiate
    x = np.array([])
    y = np.array([])

    sel = X.astype(np.int16) + 1
    #create locations
    for i in range(1, sel.max()+1):
        locs = np.where(sel==i)
        for j in range(i):
            #locs = np.where(sel==i)
            try:
                x = np.append(x, locs[0])
                y = np.append(y, locs[1])
            except: #this number doesn't exist in the array
                break
            
    #make the sns plot
    with sns.axes_style("white"):
        sns.jointplot(x=x, y=y, kind="hex", color="k");
        plt.show()
                
    
    #return x, y

#---------------------------------------------------------------------------------------------

def plotJointLike(X):
    '''
    Plots a joint plot like for an 2D array data
    '''
    fig = plt.figure(figsize=(8,8))
    gs = fig.add_gridspec(3, 3)
    ax1 = fig.add_subplot(gs[0, :2])
    plt.bar(np.arange(X.shape[0]), np.sum(X, axis=0))
    ax1.axis('off')
    ax1.set_title('ProjY')
    ax2 = fig.add_subplot(gs[1:, :-1])
    ax2.imshow(X)

    ax3 = fig.add_subplot(gs[1:, -1])
    plt.barh(np.arange(X.shape[0]), np.sum(X, axis=1))
    ax3.set_title('ProjX')
    ax3.axis('off')
    plt.subplots_adjust(hspace=0.1) 


#---------------------------------------------------------------------------------------------

def getDirectLORS(X):
    '''
    Takes an array of (35, 35, 35, 35) X
    Returns only a 2D array of direct LORS defined as
    X(i, j, 34-i,j)
    '''
    sel = np.zeros((35,35))
    for x1 in range(35):
        for x2 in range(35):
            sel[x1, x2] = X.reshape(35,35,35,35)[x1, x2, 34-x1, x2]
            #sel[x1, x2] = X[x1 +35*x2, 34-x1+ 35*x2]
    
    return sel

#---------------------------------------------------------------------------------------------

def border_pixels(X):
    '''
    Takes nput array : X,
    Returns the border elements of X with width w
    '''
    edge_indices = np.concatenate([np.arange(35),
                               np.arange(35) + 35*34, 
                               np.arange(35)*35,
                               np.arange(35)*35 + 34])
    edges = np.array([])
    for i in edge_indices:
        edges = np.concatenate([edges, X[i,:], X[:,i]])
        
    return edges

#---------------------------------------------------------------------------------------------
def getEnergiesPerLOR(fh):
    '''
    Gets energy for each LOR a total of 35**4 keys in a dict.
    
    Input
    -----
    fh is a text file handle with each event being the LOR
    
    Return 
    ------
    energy is a dict with keys equal to the LORS of a detector pair.
    e.g for event 0 10, 5 400 2 4, 25, 500 we get a key '02'+str(10+35*5)+str(4+35*25)
    '''
    #energy = defaultdict(list) # A list is created only as needed, so empty LORs are not created
    energy = defaultdict(partial(np.ndarray, 0, dtype=np.uint16))
    fh = open(fh, "r")
    for i, line in enumerate(fh):
        ''' 
        Reads and the split each line. The split line contains 11 items. 
        First 4 are coincidence, 6 are cordinates, 
        (d x y e)_1 (d x y e)_2 and the last one is time    
        '''
        #if i >= 1e5: break # NOT all events are necessary
        d1, x1, y1, e1, d2, x2, y2, e2 = line.split()
        #d1 and d2 are text
        # We read only detectors 13 values
        key = d1 + d2 + "--" + x1 + "-" + y1 + "--" + x2 + "-" + y2
        energy[key] = np.concatenate((energy[key], [int(e1), int(e2)]))
        
    return energy

#---------------------------------------------------------------------------------------------
def plotEnergiesPerLOR(data, keys, bins=20):
    """
    Makes a stack of histogram of plots for the dict data input.
    The figures are arranged as an array of (x, 4) where x = len(dict_data)//4 +1
    Default values of x is 8
    
    Input
    -----
    dict_data: input dict of data
    """
    
    nrows = 5 if len(keys)//4 > 5  else len(keys)//4 
    energies = operator.itemgetter(*keys)(data)
    
    font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }
    fig, axes = plt.subplots(nrows,4, sharey=True, sharex=True, figsize = (14,3*nrows))
    fig.subplots_adjust(hspace=0.5)
    
    for i, ax in enumerate(axes.flatten()):
        sns.distplot(a=energies[i], bins=bins, ax=ax, kde=True)
        ax.set(title='LOR: '+ keys[i])
        
    #Labelling axis
    for xax, yax in zip(axes[-1,:], axes[:,0]):             
        #yax.set(ylabel="LORs", fontdict=font)
        #xax.set(xlabel='Energy(keV)', fontdict=font)
        yax.set_ylabel("LORs", fontdict=font)
        xax.set_xlabel('Energy(keV)', fontdict=font) 
    
