#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 16:52:23 2020

@author: jnsofini
"""



from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
#plotting parameter
#matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

#A guess on the outlier ratio
outliers_fraction = 0.35

# define outlier/anomaly detection methods to be compared
anomaly_algorithms = [ ("Robust covariance", EllipticEnvelope(contamination=outliers_fraction)),
                       ("Isolation Forest", IsolationForest(contamination=outliers_fraction, random_state=42, behaviour="new"))]

def scatteringOutlier(lor_data, bins=100j):
    '''
    Takes LOR data and extract the energies for each detector
    
    '''
    x, y = np.array(lor_data[::2]), np.array(lor_data[1::2])
    xx, yy = np.mgrid[lor_data.min():lor_data.max():bins, lor_data.min():lor_data.max():bins]

    #Get the train data by stacking these two
    X  = np.vstack([y, x]).T

    plot_num = 1
    plt.figure(figsize=(len(anomaly_algorithms) * 2 + 3, 3))
    plt.subplots_adjust(left=.02, right=.98, bottom=.001, top=.96, wspace=.25, hspace=.01)

    for name, algorithm in anomaly_algorithms:
        t0 = time.time()
        algorithm.fit(X)
        t1 = time.time()
        plt.subplot(1, len(anomaly_algorithms), plot_num)
        plt.title(name, size=18)

        # fit the data and tag outliers
        if name == "Local Outlier Factor":
            y_pred = algorithm.fit_predict(X)
        else:
            y_pred = algorithm.fit(X).predict(X)

        # plot the levels lines and the points
        if name != "Local Outlier Factor":  # LOF does not implement predict
            Z = algorithm.predict(np.c_[xx.ravel(), yy.ravel()])
            Z = Z.reshape(xx.shape)
            plt.contour(xx, yy, Z, levels=[0], linewidths=2, colors='black')

        colors = np.array(['#377eb8', '#ff7f00'])
        plt.scatter(X[:, 0], X[:, 1], s=10, color=colors[(y_pred + 1) // 2])

        plt.xlim(200, 700)
        plt.ylim(200, 700)
        
        #plt.xticks(())
        #plt.yticks(())
        plt.text(.99, .01, ('%.2fs' % (t1 - t0)).lstrip('0'), 
                 transform=plt.gca().transAxes, size=15,
                 horizontalalignment='right'
                )
        plot_num += 1

    plt.show()