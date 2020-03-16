# Scatter Correction

Scattering events affects PET systems significantly. They originate when a measured coicidence results from two photons
in which one is from a different coincidence and the other left the body unscattered, leading to the two being detected 
simultaneously. Below is a simple cartoon of how this originate gotten from ![here](http://tech.snmjournals.org/content/29/1/4.full). 
![PET scattering event](http://tech.snmjournals.org/content/29/1/4/F4.large.jpg)

There are multiple approaches to correct for it including

  - Fitting scatter tails 
  - Multiple energy windows 
  - Convolution 
  - Scatter simulation
  
 Here we focus on fitting scatter tails. One reason for adapting this technique is because we can extract it the correction 
 factors from our measured data.
