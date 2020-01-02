#!/usr/bin/env python
# coding: utf-8

"""
Created on Tue Jun  10 15:56:48 2019

Modified Tue Jun 11 2019

@author: jnsofini

Program to convert the bin files from out phytopet system to castor data format cdf. 
The bin file contains a sequence of data in the form [detector coincidence {ABCD}] 
: [X_position det1 {ABCD}] : [Y_position det1 {ABCD}] : [Energy det1 {ABCD}] 
: [X_position det2 {ABCD}] : [Y_position det2 {ABCD}] : [Energy det2 {ABCD}]
: [Time-Stamp {ABCD abcd jklm pqrs}]. 

"""

import os.path as path


# The input file is given below. It should be edited as desired. The output file has the same name as the input but with a .txt extension

infile = '/home/jnsofini/R2019/Data/Cyl-cont-rot-6-May8.bin'
time_units = 4e-9

default_path, input_file_name =  path.split(infile)
oufile_name = path.splitext(input_file_name)[0]+".txt"

outfile = path.join(default_path, oufile_name)

#=====================================================================================================================================
# ### Helper functions implementation:
# 
# There are three functions which include:
# 
# 1. getCoincidence to return the coincidence event
# 2. getData which gets the coordinate of x,y position and energy e
# 3. getTime which return the time at which the event occured
# 

#-------------------------------------------------------------------------------------------------------------------
# Get coincidence to read the coincidence and return a boolean mask with four entries representing det4,det3,det2,det1

def getCoincidence(single_line):
    """
    Gets a binary format buffer containing 2 chars which represents the coincidence part of the event. It then return
    and a mask that shows the detector in coincidence represented as 0213 or 1324
    Parameters
    ----------
    single_line: 
    Immutable binary array buffer containing cobinations of F and 0 representing the 
    coincidence between the detectors
    
    co_buffer, mask:
    co_buffer is a list containing the values that tell if the detector fired or not
    mask is a boolian generator (basically an on-demand list, can be printed by using list(mask)) 
    of the detectors that fired
    
    """  
    
    co_buffer = [single_line[i%2] for i in range(4)] # Converts its to a mutable format
    
    co_buffer[0] = (co_buffer[0]>>4)&0xF  # uses bit shifting to extract value for single det bc val read is for two dets
    co_buffer[1] = (co_buffer[1]>>4)&0xF
    
    co_buffer[2] = co_buffer[2]&0xF
    co_buffer[3] = co_buffer[3]&0xF
    
    #maska = (int(k==15) for k in co_buffer)
    mask = [int(k==15) for k in co_buffer] #a mutable form for easy use. Return is coincidence 0213
    
    return co_buffer, mask 

#-------------------------------------------------------------------------------------------------------------------

def getData(binary_file):
    """
    Takes an input line if events are present, reads their features to and return list of Rawdata data
    Parameters
    ----------
    binary_file:
    Impur file that contain the stream as described in the beginning.
    
    Coordinate:
    A stream containing on the coordinates (x, y, e)_1 and  (x, y, e)_1 of the detectors that fired in the coincidence
    
    """
    cordinate = []
    
    cord_line = binary_file.read(6) # each of xye contains 2 chars
    for k in range(0, len(cord_line), 2):
        cordinate.append((cord_line[k] << 8)|(cord_line[k+1] & 0xFF)) 
        
    return cordinate

#-------------------------------------------------------------------------------------------------------------------

def getTime(binary_file):
    """
    The next 8 pairs are the time. To combine them to a single time stamp, we will NOT shift last one 
    and then the one to its left by 8 and so on until the first digit.
    
    time;
    ----------------
    The integer form of the time.
    8 char are read from the file to the buffer. Each of them correcpond to the bin base component for 
    each of the location. The chars are converted to 64 (because all the 8 read are of a single var) by p
    roper left bitshift << and clearing residues with bitset |. All of them are finally combined together 
    using | which generate a final time stamp.
    
    """
    timestamp = binary_file.read(8)
    
    
    time = 0
    time |= ((timestamp[0]<<56) & 0xff00000000000000)
    time |= ((timestamp[1]<<48) & 0x00ff000000000000)
    time |= ((timestamp[2]<<40) & 0x0000ff0000000000)
    time |= ((timestamp[3]<<32) & 0x000000ff00000000)
    time |= ((timestamp[4]<<24) & 0x00000000ff000000)
    time |= ((timestamp[5]<<16) & 0x0000000000ff0000);
    time |= ((timestamp[6]<<8)  & 0x000000000000ff00);
    time |= ((timestamp[7])     & 0x00000000000000ff); 
    
    return time

#=====================================================================================================================================

# ## Main program: 
# Converting any file from bin to text and then saving in the same folders. the following ask for the file names:

'''
Reads the data and store in a 
'''

with open(infile, "rb") as fbin:
    with open(outfile, "w") as ftext:
        
        #----Get first machine event which is not good and discard--------
        coin = fbin.read(2); 
        _ , mask = getCoincidence(coin)  
        for k in range(sum(mask)): 
            getData(fbin)
        getTime(fbin)    
        #----------------------------------------------------------------
        
        #----The real first event and use it to set the time-------------
        coin = fbin.read(2); 
        coincidence, mask = getCoincidence(coin)
        event_and_data = mask
        for k in range(sum(mask)):
            #read coordinates
            event_and_data.extend(getData(fbin))

        #times
        initial_time = 0
        time = getTime(fbin)

        event_and_data.extend([initial_time])
        for events in event_and_data:
            ftext.write(str(events)+'\t')
        ftext.write('\n') # write new line to move to the next line and represent the next event
        
        initial_time = time

        coin = fbin.read(2) #proceed to next
    
        
        while coin:
            """ Receives various versions of coincidencecoincidence, mask, maska and then read the coordinate and time"""
            coincidence, mask = getCoincidence(coin)
            
            event_and_data = mask
            for k in range(sum(mask)):
                #read coordinates
                event_and_data.extend(getData(fbin))
                
            #times
            time = getTime(fbin)
             
            event_and_data.extend([round((time - initial_time)*time_units, 6)])
            
            #print(event_and_data)
            for events in event_and_data:
                ftext.write(str(events)+'\t')
            ftext.write('\n') # write new line to move to the next line and represent the next event
            
            #Proceed to the next event 
            coin = fbin.read(2)


