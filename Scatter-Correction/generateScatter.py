#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 11:06:50 2020

@author: jnsofini

## Part III: Scatter Correction
In scatter correction, we set out to estimate the scatter correction for each LOR. Typically this is measured using CT or other method, but but in this case, we instead estimate them from the energy distribution profile. The background extended to the area under the 511 keV peak reveals the scattering contribution to this LOR. An estimate, for a given geometry, can then be made for each LOR.

### 1. Data for each LOR
Get the energies of each LOR. The function below goes through the file, and extract the data as a dict. The LOR ids are the _key_ and the energies list as the _value_. The list container is such that the every successive even-odd pair are energies for pixel 1 and pixel 2 of a corresponding coincidence. The data for each LOR can then be accessed with the help of a key, which is a string of the form _d1 + d2 + "--" + x1 + "-" + y1 + "--" + x2 + "-" + y2_, where, each of these have the obious meaning.

"""

#Get modules used
import argparse
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import pandas as pd
import os
import time
import seaborn as sns
import sys
import csv

#Building the model
from sklearn.neighbors import KernelDensity, KNeighborsRegressor

#Clustering part
#from sklearn.cluster import KMeans
#from sklearn.metrics import silhouette_score, auc

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, LassoCV

#Used to create dic containers with keys automatically added
from collections import defaultdict, namedtuple
from functools import partial



#IO files to the program 

iname = ""
outfile = " "


#------------------------------------------------------------------------------------------

def ParseCommandLineArguments():
    '''
    Used to parse the command like arguments. Infile and outfile are names of the
    input and output files
    '''
    
    global iname, outfile #Because we need to modify the arguments we need to acess them as globals
        
    parser = argparse.ArgumentParser(description='=======PET Scattering Coefficients======')    
    parser.add_argument("input", nargs='+')
    parser.add_argument("output")    
    args = parser.parse_args()   
    
    
    arguments = args.input
    nargs = len(arguments)
    for i, item in enumerate(arguments):
        
        current = arguments[i]
        if   (current=="-h" or current=="--help"): 
            Usage
            
        elif (current == "inF"):
            if(i == nargs-1): 
                print("inF requires one argument!")
                Usage
            #With enough arguments
            iname = arguments[i+1]
            print(iname)
            
        elif (current == "outF"):
            if (i == nargs-1): 
                print("outF requires one argument!")
                Usage
            
    outfile = args.output # is the last arg
    print(outfile)

    
def Usage():
    print()
    print("Usage")
    print("exec_name inF data.txt outF outputfile.csv")
    print("  options:")
    print()

#----------------------------------------------------------------------------------------------
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
    
    with open(fh, "r") as fh:
        for i, line in enumerate(fh):
            ''' 
            Reads and the split each line. The split line contains 11 items. 
            First 4 are coincidence, 6 are cordinates, 
            (d x y e)_1 (d x y e)_2 and the last one is time    
            '''
            if i >= 1e5: break # NOT all events are necessary *********************************
            d1, x1, y1, e1, d2, x2, y2, e2 = line.split()
            key = d1 + d2 + "-" + x1 + "-" + y1 + "-" + x2 + "-" + y2
            energy[key] = np.concatenate((energy[key], [int(e1), int(e2)]))
        
    return energy

#------------------------------------------------------------------------------
def generateScatterCoefficients(data, keys=None, bins=30, n_neighbors = 3):
    '''
    Fits a single data using KNeighborsRegressor. Extract four points , two to 
    the left and two to the right and get their average to extract the area.
    
    Inputs
    -------
    
    data: A dict of list for each LOR
    bins: the number of bins for use in binning the data, 
    n_neighbors: number of neighbours used to create a point
    
    
    Returns
    -------
    Scattering_data a dict with keys the LOR and content the background.
    
    '''
    keys = keys if keys else data.keys()    
    scattering_data = {}
    
    for i, key in enumerate(keys):
        '''
        Go through each LOR and get the coeff
        '''
        #if (1 % 10 == 0): print('LOR : ', key)

        hist = np.histogram(data[key], bins=bins, density=False)
        X, y = hist[1][:-1], hist[0]  
        X_test = np.linspace(X.min(), X.max(), 1000)
        
        #Regressor to fit the data
        knn = KNeighborsRegressor(n_neighbors, weights='uniform', p=1)
        model = knn.fit(X[:, None], y)
        y_pred = model.predict(X_test[:, None])       
        
        #Get as estimate of the background from selecting the value at 40% and 60% and extracting a linear value
        v_40, v_60 = X_test[0] + (X_test[-1] - X_test[0])*0.4, X_test[0]+ (X_test[-1] - X_test[0])*0.6
        #Get X[40%] and x[60%]
        area = 0.5*( np.mean(y_pred[X_test < v_40][-2:]) + np.mean(y_pred[X_test > v_60][:2])  )*(X_test[600] - X_test[400] )        
        
        scattering_data[key] = round(area, 2)
        
    return scattering_data                     
    
#--------------------------------------------------------------------------------

#=======================================================================================================================
#Septup arguments
ParseCommandLineArguments()


print("   ")
print( "==============================================================================================")
print( "Data conversion is going on. Should take from one to several minutes depending on the hardware")
print( "==============================================================================================")
print("   ")

initial_time = time.time()
    
in_path, input_file_name =  os.path.split(iname)
out_path, output_file_name =  os.path.split(outfile)
num_1d_crystals = 35
Coincidence = namedtuple("Coincidence", "d x1 y1 x2 y2")
scatter = {'02': {}, '13': {}} # define a dict of dict





#We get the energies per LOR and then used it to get the coefficients
energies_per_lor = getEnergiesPerLOR(iname)

#Generate the coeffcients
scatter_coeff = generateScatterCoefficients(energies_per_lor)

#save the coefficients and load the pickle file
with open(f'{outfile}.pickle', 'wb') as bfile:   
    # source, destination 
    pickle.dump(scatter_coeff, bfile)   


with open(f"{outfile}.pickle",'rb') as rbfile:
    scatter_bin = pickle.load(rbfile)
    
def scatter_dict(scatter):
    
    for i, (coin_ID, s) in enumerate(scatter_bin.items()):
        '''
        We replace '--' by '-', split the key, and then extract the values from the return list
        z1 = x1 + 35*y1, z2 = x2 + 35* y2, 
        z = z1 + 35*35*z2  = x1 + x2*35**2 + 35*(y1+ y2*35**2)
        Coincidence(* coin_ID.split('-') )
        '''
    
        #if i > 50: break    
        d, x1, y1, x2, y2 = Coincidence(* coin_ID.split('-'))
        scatter[d][ int(x1) + int(x2)*num_1d_crystals**2 + 
                   num_1d_crystals*(int(y1) + int(y2)*num_1d_crystals**2)] = round(s/3600, 4)
        
    return scatter

scatter = scatter_dict(scatter)
        
#sort the values
#for det_id, scat in scatter.items():
 #   scatter[det_id] = {key: value for (key, value) in sorted(scat.items())}

#write to another file

def write_scatter(scatter):
    
    for det_id, scat in scatter.items():
        with open(f"sorted_{outfile}_{det_id}.csv", "w", newline='') as scatter_file:
            writer = csv.writer(scatter_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            for coordinate, value in sorted(scat.items()):
                #Write each of the   
                #print(det_id, value)
                writer.writerow([coordinate, value])  

write_scatter(scatter)

print("Time taken: ", time.time()-initial_time)
print("   ")
print("------------------------------------------------------------ ")
print("Data source: {}".format(in_path) )
print("Data destination: {}".format(out_path) )
print("   ")
#print("Input files: {}, {}".format(input_file_name, path.split(infile2)[1]) )
#print("Output file: {}".format(output_file_name) )
print("Input files 13: ", iname)
print("   ")