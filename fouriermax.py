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

def Fouriermax(inpath):
    timestep = 100
    pnodesz = np.load(inpath)

    num_timesteps = pnodesz[0]
    num_timesteps = int(num_timesteps)
    Hnodesz = pnodesz[1:num_timesteps+1]
    Nnodesz = pnodesz[num_timesteps+2:num_timesteps*2+1]
    Snodesz = pnodesz[num_timesteps*2+2:num_timesteps*3+1]
    Enodesz = pnodesz[num_timesteps*3+2:num_timesteps*4+1]
    Wnodesz = pnodesz[num_timesteps*4+2:num_timesteps*5+1]
    WGTnodesz = pnodesz[num_timesteps*5+2:num_timesteps*6+1]

    #plt.plot(Hnodesz)
    #plt.suptitle('Hub Node Pos')
    #plt.show()
    for t in range (5): #6 for all
        if t == 0:
            tffz = fft(Hnodesz)
            n = len(tffz)
            tffza = np.absolute(tffz/n) #P2 = abs(Y/L);
            tffp = []
            fh = [] 
            for i in range (int (n/2)):
                tffp.append(tffza[i]) #P1 = P2(1:L/2+1);
                fh.append(timestep*(i)/n) #f = Fs*(0:(L/2))/L;
            for i in range ((int (n/2)) - 2):
                tffp[i+1] = 2*tffza[i+1] #P1(2:end-1) = 2*P1(2:end-1);
            h_max = np.argmax(tffp)
            ha_max = max(tffp)
        if t == 1:
            tffz = fft(Nnodesz)
            n = len(tffz)
            tffza = np.absolute(tffz/n) #P2 = abs(Y/L);
            tffp = []
            fn = [] 
            for i in range (int (n/2)):
                tffp.append(tffza[i]) #P1 = P2(1:L/2+1);
                fn.append(timestep*(i)/n) #f = Fs*(0:(L/2))/L;
            for i in range ((int (n/2)) - 2):
                tffp[i+1] = 2*tffza[i+1] #P1(2:end-1) = 2*P1(2:end-1);
            n_max = np.argmax(tffp)
            na_max = max(tffp)
        if t == 2:
            tffz = fft(Snodesz)
            n = len(tffz)
            tffza = np.absolute(tffz/n) #P2 = abs(Y/L);
            tffp = []
            fs = [] 
            for i in range (int (n/2)):
                tffp.append(tffza[i]) #P1 = P2(1:L/2+1);
                fs.append(timestep*(i)/n) #f = Fs*(0:(L/2))/L;
            for i in range ((int (n/2)) - 2):
                tffp[i+1] = 2*tffza[i+1] #P1(2:end-1) = 2*P1(2:end-1);
            s_max = np.argmax(tffp)
            sa_max = max(tffp)
        if t == 3:
            tffz = fft(Enodesz)
            n = len(tffz)
            tffza = np.absolute(tffz/n) #P2 = abs(Y/L);
            tffp = []
            fe = [] 
            for i in range (int (n/2)):
                tffp.append(tffza[i]) #P1 = P2(1:L/2+1);
                fe.append(timestep*(i)/n) #f = Fs*(0:(L/2))/L;
            for i in range ((int (n/2)) - 2):
                tffp[i+1] = 2*tffza[i+1] #P1(2:end-1) = 2*P1(2:end-1);
            e_max = np.argmax(tffp)
            ea_max = max(tffp)
        if t == 4:
            tffz = fft(Wnodesz)
            n = len(tffz)
            tffza = np.absolute(tffz/n) #P2 = abs(Y/L);
            tffp = []
            fw = [] 
            for i in range (int (n/2)):
                tffp.append(tffza[i]) #P1 = P2(1:L/2+1);
                fw.append(timestep*(i)/n) #f = Fs*(0:(L/2))/L;
            for i in range ((int (n/2)) - 2):
                tffp[i+1] = 2*tffza[i+1] #P1(2:end-1) = 2*P1(2:end-1);
            w_max = np.argmax(tffp)
            wa_max = max(tffp)
    #print (max(tffp))
    #print (tffp.index(max(tffp)))
    #print (n_max)
    #print (f[5])
    return (fh[h_max], ha_max, fn[n_max], na_max, fs[s_max], sa_max, fe[e_max], ea_max, fw[w_max], wa_max)