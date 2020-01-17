# Positron emission tomography
Positron emission tomography (PET) is a modality to generate images, mostly of internal organs, via the use of a radiotracer, which is a labelled radioactive isotope. A typical example is fluorodeoxyglucose and abbreviated [$^18$F]FDG, $^18$F-FDG or FDG used in the medical imaging. In the target organ, a nuclear process occurs, and a positron is emitted. Within a short-range, this particle is captured by an electron, a process known as annihilation. Two photons are released, and they travel in a straight line opposite to each other. Arrays of detectors commonly arranged in a circular fashion detect the photons, in coincidence. An electrical signal recorded in the form of and event. In our DAQ system, and the event is recorded in a binary file after a trigger. In this repository are programs in C++, Python, OpenCV, Jave (Imagej) to perform 
* Conversion from binary to text and castor CDF format.  
* Processing of normalization data used for image correction
* Image reconstruction using Maximum Likelihood implemented in [`castor-recon`](http://www.castor-project.org/)., C++ base
* Visualization of data
* NEMA standards implemented in Imagej

### 1. Data file
The event constitutes 4 segments
1. Detector event recoded as 1, 0., for example, 1100 means detector 1 and 2 fired and detector 3 and 4 were off, of  1111 means all four detectors fires.
2. The next event is conditional on the number of detectors that fired. If detector event is 1100 as above, x1, y1, e1, and x2, y2, e2 are measured. These are correspondingly the x location, y location, and energy.
3. The time is the last thing to record.

### 2. Data conversion
`castor-recon` accepts a specific format of data called CDF. Details description is on the [wbsite](http://www.castor-project.org/). Provided in the program folder is a C++ program that converts binary to CDF. PET images suffer from various errors that must be corrected. We have data for normalization correction and will be processed in the appropriate format.

### 3. Normalization correction
Here, we will deal with normalization errors. These are errors that arise due to the inherent geometry of the system. A simple way to think of it is that if a cylindrical source is used, the density of lines through the center will be higher than at the edge, creating a fictitious high density at the center. To correct this, we use a flat phantom and place it with it face adjacent to the detectors. Events recorded are then processed. One technique used to improve the statistics is called fan-sum which helps reduce the variance

### 4. Data visualization
Several data visualizations files are in the repo. Images  and normalization coefficients visualized. Outlier detection methods are applied to identify dead pixels.


### 4. NEMA standards implemented in ImageJ
NEMA - NU 2004 standards are a set of rules defined to facilitate the comparison of results across different systems.
