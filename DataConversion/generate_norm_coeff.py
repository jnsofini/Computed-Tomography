#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 15:07:41 2019

@author: jnsofini

# Program to convert text raw normalization data to norm coefficients
Takes in a text data file with each line representing events recorded as \\(d_1, x_1, y_1, e_1, d_2, x_2, y_2, e_2\\). These represents the detector, x and y locations and the energy.
Dec 4th

The file is output from a C++ program that convert binary to text with that format. In this  program a histogram of the normalization intensity is created and the correcponding normalization coefficients extracted. They are saved in a text file.
What this script does:
 - Convert a normalization intensity file to an array of 35X35
 - Convert multiple files for a particular pair into a single 35x35 array
 - Perform the fansum algorithm to improve the statistics
 - save a text file to the output
 
 Last edited: Jan 10
 
 RUNNING the program:
    python3 petNormDataToNormCoeff.py  inF13 inputfile13_1.txt inputfile13_2.txt ...\
    inF24 inputfile24_1.txt inputfile24_2.txt ... outF outputfile.txt

"""

#Important imports

import numpy as np
import os.path as path
import itertools as it
import argparse
import time


iname13 = []
iname24 = []
outfile = " "

#Helper functions

'''
Given a file, we want to extract the LORs pairs and group them in to a histogram. 
The histogram is recoded as a 2D list with the dimensions N*M where N and M are the 
number of pixels in the x and y axis.
'''

    
def ParseCommandLineArguments():
    '''
    Used to parse the command like arguments. Infile and outfile are names of the
    input and output files
    '''

    
    global iname13, iname24, outfile
        
    parser = argparse.ArgumentParser(description='=======PET Normalization Coefficients======')
    #parser.add_argument('infile', type=str, help='Input dir/file for norm data')
    #parser.add_argument('infile2', type=str, help='Input dir/file for norm data')
    #parser.add_argument('outfile', type=str, help='Output dir for norm coefficients')
    
    parser.add_argument("input", nargs='+')
    parser.add_argument("output")
    
    args = parser.parse_args()   
    
    
    arguments = args.input
    nargs = len(arguments)
    for i, item in enumerate(arguments):
        
        current = arguments[i]
        if(current=="-h" or current=="--help"): 
            Usage
            
        elif (current=="inF13"):
            if(i==nargs-1): print("-inF13 requires one argument!")
            #With enough arguments
            j = i + 1
            while((arguments[j] != "inF24") and (j<nargs)):
                iname13.append(arguments[j])
                j += 1
            i = j
        elif (current=="inF24"):
            if(i==nargs-1): print("-inF13 requires one argument!")
            #With enough arguments
            j = i + 1
            while((arguments[j] != "outF") and (j<nargs)):
                iname24.append(arguments[j])
                j += 1
            i = j
            
    outfile = args.output
    #print("Arg object is:", args)
    #for item in args.input:
    #    print(item)
    #    print(type(item))
    
    #infile = args.infile
    #infile2 = args.infile2
    #outfile = args.outfile
    
def Usage():
    print()
    print("Usage")
    print("exec_name inF13 norm_data_13_1.txt norm_data_13_2.txt norm_data_13_3.txt ---\
          inF24 norm_data_24_1.txt norm_data_24_2.txt norm_data_13_3.txt outF outputfile.txt")
    print("  options:")
    print()
    
    
    
#-----------------------added-------------------------------------------------------------------
def getLORsFromTxt(fh, id_):
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
        coin_ = 0 # The useful intensity in 13 files is 0 2
    elif (id_==24): 
        coin_ = 1 # The useful intensity in 13 files is 1 3
    else :
        raise ValueError('Wrong detector ID: {}'.format(id_))

    
    DET_SIZE = 35
    lors_norm = np.zeros((DET_SIZE*DET_SIZE, DET_SIZE*DET_SIZE)) #2x2 array

    fh = open(fh, "r")
    for line in fh:
        ''' 
        Reads and the split each line of 8 items. First four (d x y e)_1 for one detector and 
        the other four (d x y e)_2 for its coincidence detector    
        '''        
        d1, x1, y1, e1, d2, x2, y2, e2 = list(map(int, line.split()))
        #d1, x1, y1, e1, d2, x2, y2, e2 = [int(s) for s in line.split()] #split line, convert to ints

        if (d1 == coin_):
            lors_norm[x1 + DET_SIZE*y1, x2 + DET_SIZE*y2] += 1 #Pick pair of coin

    fh.close()
    
    return lors_norm

#---------------------------------------------------------------------------------------------------------
def fanSumAlgo(*data):
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
    lors_fan_sum_ = [np.zeros(np.shape(det_data)) for det_data in data]
    
    assert(len(lors_fan_sum_) == 2), "Only TWO data arrays are expected"
    
    lors_fan_sum_[0] = np.sum(data[0], axis=1, keepdims=True)\
                                     *np.sum(data[0], axis=0, keepdims=True)/np.sum(data[0])
    lors_fan_sum_[1] = np.sum(data[1], axis=1, keepdims=True)\
                                     *np.sum(data[1], axis=0, keepdims=True)/np.sum(data[1])

    return lors_fan_sum_

#---------------------------------------------------------------------------------------------------------


def saveNormCoeffTxt(fansum_1324_list):  
    '''
    Saves the normalization coefficients that are stored in an array into a file. The form of the data is
    is [detector, x, y, detector, x, y, normcoeff]
    Input:
    ------
    fansum_1324_list: array of form [detector, x, y, detector, x, y, normcoeff]
    '''
    
    
    n_pixel = 35
    lors_13, lors_24 = fansum_1324_list

    fh = open(outfile, "w")
    #for i, line in enumerate(fh):
    for x1, y1, x2, y2 in it.product(range(n_pixel), range(n_pixel), range(n_pixel), range(n_pixel)):
                    
        fh.write(str(0) + ' ' + str(x1) + ' ' + str(y1) + ' ' 
                 + str(2) + ' ' + str(x2)+ ' ' + str(y2) + ' ' + str(lors_13[x1+n_pixel*y1, x2+n_pixel*y2]) + '\n' ) #flags 1, 2
        fh.write(str(1) + ' ' + str(x1) + ' ' + str(y1) + ' ' 
                 + str(3) + ' ' + str(x2)+ ' ' + str(y2)+ ' ' + str(lors_24[x1+n_pixel*y1, x2+n_pixel*y2]) + '\n' ) #flags 1, 2
                    
    fh.close()
#---------------------------------------------------------------------------------------------------------

def test_coordinates(f):
    print("Coordinates with zero values: ")
    print("-----------------------------")
    print(np.argwhere(f==0))

#===============main=========================================================

    
initial_time = time.time() # check the script running time

ParseCommandLineArguments()



print("   ")
print( "==============================================================================================")
print( "Data conversion is going on. Should take from one to several minutes depending on the hardware")
print( "==============================================================================================")
print("   ")


    
    
#Get the data from the input file and sort in into an array
DET_SIZE = 35
lors_norm_13 = np.zeros((DET_SIZE*DET_SIZE, DET_SIZE*DET_SIZE)) #get LORS for 13
for fh in iname13:
    lors13 = getLORsFromTxt(fh, 13)    
    assert(lors_norm_13.shape == lors13.shape), "Only similar dimensions are allowed"
    lors_norm_13 = lors_norm_13 + lors13
    
lors_norm_24 = np.zeros((DET_SIZE*DET_SIZE, DET_SIZE*DET_SIZE)) #get lors for 24
for fh in iname24:
    lors24 = getLORsFromTxt(fh, 24)
    assert(lors_norm_24.shape == lors24.shape), "Only similar dimensions are allowed"
    lors_norm_24 = lors_norm_24 + lors24


#print(np.max(lors_norm_13), np.min(lors_norm_13), np.mean(lors_norm_13))
#print(np.max(lors_norm_24), np.min(lors_norm_24), np.mean(lors_norm_24))

#check the coordinates that don't have intensities
#test_coordinates(lors_norm_13)
#test_coordinates(lors_norm_24)

#Scalling the data
lors_norm_13s = lors_norm_13/np.sum(lors_norm_13)
lors_norm_24s = lors_norm_24/np.sum(lors_norm_24)

#saveNormCoeffTxt((lors_norm_13s, lors_norm_24s))
fan_sum_data = fanSumAlgo(lors_norm_13s, lors_norm_24s)

# write the norm coefficients from the fan_sum into a textfile
saveNormCoeffTxt(fan_sum_data)



in_path, input_file_name =  path.split(iname13[0])
out_path, output_file_name =  path.split(outfile)
input_file_names = [path.split(f)[1] for f in iname13+iname24]



print("Time taken: ", time.time()-initial_time)
print("   ")
print("------------------------------------------------------------ ")
print("Data source: {}".format(in_path) )
print("Data destination: {}".format(out_path) )
print("   ")
#print("Input files: {}, {}".format(input_file_name, path.split(infile2)[1]) )
#print("Output file: {}".format(output_file_name) )
print("Input files 13: ", input_file_names[:len(iname13)])
print("Input files 24: ", input_file_names[len(iname13):])
print("   ")
