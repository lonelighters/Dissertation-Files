import os
import csv
import pandas as pd
from pandas import DataFrame
from scipy.signal import find_peaks
import pickle as pkl
import matplotlib.pyplot as plt 
import mpl_toolkits.mplot3d.axes3d as p3 
import matplotlib.animation as animation
plt.ion()
import numpy as np 
from numpy.fft import fft, ifft, fftfreq, rfft
import seaborn as sn 
import networkx as nx
import yaml
import copy
import math
import time
from scipy.misc import electrocardiogram
import convpickle
import fouriermax
import CSVconv

def webmod(changenode, massdef):
    id_no = 0
    x = 0.0
    y = 0.0
    z = 0.0
    radius = 0.0
    theta = 0.0
    mass = 0.0
    fixed = 0

    node_num = 0
    nodes = []
    node = []
    springs = []
    mass = 0
    path = 'web.csv'
    changenode = changenode + 1
    #Web Modifier
    with open('web.csv', 'r') as w:
        line = w.readline()
        #Node Change (Node changed is Range - 1)
        for i in range (changenode):
            line = w.readline()
        id_no, x, y, z, radius, theta, mass, fixed =  [float(val) for val in line.split('\t')]

    #Web Description
    with open('web.csv', 'r') as web:
        r = csv.reader(web) # Here your csv file
        lines = list(r)

        mass = float(massdef)
        temp = '%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%d' % (id_no, x, y, z, radius, theta, mass, fixed)
        lines[changenode] = [temp]

    with open('webrand.csv', mode= 'w') as webrand:
        writer = csv.writer(webrand, lineterminator='\n')
        csv.register_dialect('lineterminator')
        writer.writerows(lines)
    print('websuccess')

Hmaxpoints = []
Nmaxpoints = []
Smaxpoints = []
Emaxpoints = []
Wmaxpoints = []
Fmaxpoints = []

changenodes = list(range(19, 52))
weights = [1, 10, 20]
#weights = np.arange(0.5, 1.6, 0.1)
#wt = np.arange(4.5, 5.6, 0.1)
#weights = np.append(weights, wt)
#wt = np.arange(9.5, 10.6, 0.1)
#weights = np.append(weights, wt)

for t in changenodes:
    print (t)
    for i in weights:
        name = 'webnode' + str (t) + 'mass' + str(i)
            #Web Definition
        webmod(t, i)            #Web Simulation
        os.system("D:\Project\Dissertation\Test2\martin_garrad-spidersweb-14205bbac18a\main.o webrand.csv > temp.txt")
            #Data Conversion
        convpickle.convpickle('webrand.csv', 'temp.txt', name)
            #Return and progress Checks
        print (name)
        print (str(i))
            #Maximum point position and saving
        f_max = fouriermax.Fouriermax(name + '.npy')
        Fmaxpoints.append(f_max)
        #Hmaxpoints.append([f_max[0], f_max[1]])
        #Nmaxpoints.append([f_max[2], f_max[3]])
        #Smaxpoints.append([f_max[4], f_max[5]])
        #Emaxpoints.append([f_max[6], f_max[7]])
        #Wmaxpoints.append([f_max[8], f_max[9]])
        ##maxpoints.append(fouriermax.Fouriermax(name + '.npy'))
    #np.save('Hpoints', Hmaxpoints)
    #np.save('Npoints', Nmaxpoints)
    #np.save('Spoints', Smaxpoints)
    #np.save('Epoints', Emaxpoints)
    #np.save('Wpoints', Wmaxpoints)
    np.save('L2points', Fmaxpoints)

CSVconv.CSVconv('L2points', changenodes, weights)
#N = ['Hpoints','Npoints','Spoints','Epoints','Wpoints']
#for node_names in N:
    #CSVconv.CSVconv(node_names)




    #Data Collection

    #Data Analysis