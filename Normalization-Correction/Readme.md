### 3. Normalization correction
Here, we will deal with normalization errors. These are errors that arise due to the inherent geometry of the system. 
A simple way to think of it is that if a cylindrical source is used, the density of lines through the center will be 
higher than at the edge, creating a fictitious high density at the center. To correct this, we use a flat phantom and 
place it with it face adjacent to the detectors. Events recorded are then processed. One technique used to improve the 
statistics is called fan-sum which helps reduce the variance. A sketch is shown below of the process used to variance 
reduction. ![](https://github.com/jnsofini/Computed-Tomography/blob/master/figures/fansum.png). 

In a simples way, the main assumption is that the phantom has a uniform variation in intensity. So, the coouts in detector 
$i$ in coincidence with a group of detectors B is improved by summing all the counts in B. By summing the count in the group,
the statistics is improved without any information leakage.
