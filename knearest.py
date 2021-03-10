from math import sqrt
import numpy as np
import csv
import pandas as pd
from pandas import DataFrame
import scipy.io as sio
import sklearn
import sklearn.model_selection
import statistics
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
from operator import truediv
import matplotlib.pyplot as plt

# calculate the Euclidean distance between two vectors
def euclidean_distance(row1, row2):
	distance = 0.0
	for i in range(len(row1)-1):
		distance += (row1[i] - row2[i])**2
	return sqrt(distance)
 
# Locate the most similar neighbors
def get_neighbors(train, test_row, num_neighbors):
	distances = list()
	for train_row in train:
		dist = euclidean_distance(test_row, train_row)
		distances.append((train_row, dist))
	distances.sort(key=lambda tup: tup[1])
	neighbors = list()
	for i in range(num_neighbors):
		neighbors.append(distances[i][0])
	return neighbors

spltamt = [0.2]

for splamt in spltamt:
    print ("/n")
    print (splamt)
    for k in range (3, 4):
        percentage = []
        tPF = []
        tallyp = [1] * 24
        tally=[1] * 24
        tanswer = []
        for t in range (1, 21):
            tallyf = []
            PF = []

            #Reading
            N = ['Hpoints','Npoints','Spoints','Epoints','Wpoints']
            Fullpoints = []
            Trainpoints = []
            Testpoints = []
            nodepoint = 0
            FPoints = []
            Apoints = []
            Rpoints = []
            ranswer = []

            with open('AutomatedTesting\ ' + 'Mpoints' + '.csv', 'r') as web:
                #changenodes = list(range(19, 52))
                #weights = [1, 10, 20]
                changenodes = [19, 23, 27, 31]
                weights = list(range(1, 25))
                a = 0
                for t in changenodes:
                    for i in weights:
                        line = web.readline()
                        #if (t != 19 and t!= 23 and t!= 27 and t!=31 and t !=35 and t!=39 and t!=43 and t!=47 and t!=51):
                        #if (t == 21 or t == 25 or t == 29 or t == 33 or t == 37 or t == 41 or t == 25 or t == 49):
                        #if (t>=31 and t<=39):
                        if (i != 8 and i != 9 and i != 17):
                            id_no, w, h_max, ha_max, n_max, na_max, s_max, sa_max, e_max, ea_max, w_max, wa_max =  [float(val) for val in line.split('\t')]
                            temp = [h_max, n_max, s_max, e_max, w_max]
                            #FPoints.append(temp)
                            #temp = [ha_max, na_max, sa_max, ea_max, wa_max]
                            FPoints.append(temp)
                            temp = [id_no, w, h_max, ha_max, n_max, na_max, s_max, sa_max, e_max, ea_max, w_max, wa_max]
                            Rpoints.append(temp)
                            #ranswer.append(id_no)
                            ranswer.append(w)
                            a = a + 1
                
            split = np.arange (0, len(Rpoints), 1)
            ptstrn, ptstst = sklearn.model_selection.train_test_split(split, test_size = splamt)
            trnpts = []
            Trainpoints = []
            Testpoints = []
            answer = []
            tempanswer = list(ranswer)

            #for i in range (len(Rpoints)):
            #    if ((Rpoints[i][0] <= 27 and Rpoints[i][0] >= 24) or (Rpoints[i][0]<=43 and Rpoints[i][0]>=40)):
            #        Rpoints[i][0] = "NE"
            #        ranswer[i] = "NE"
            #    elif ((Rpoints[i][0] <= 23 and Rpoints[i][0] >= 20) or (Rpoints[i][0]<=39 and Rpoints[i][0]>=36)):
            #        Rpoints[i][0] = "SE"
            #        ranswer[i] = "SE"
            #    elif ((Rpoints[i][0] <= 35 and Rpoints[i][0] >= 32) or (Rpoints[i][0]<=51 and Rpoints[i][0]>=48) or Rpoints[i][0] == 19):
            #        Rpoints[i][0] = "SW"
            #        ranswer[i] = "SW"
            #    elif ((Rpoints[i][0] <= 31 and Rpoints[i][0] >= 28) or (Rpoints[i][0]<=47 and Rpoints[i][0]>=44)):
            #        Rpoints[i][0] = "NW"
            #        ranswer[i] = "NW"
            #    else:
            #        print ("Error")
            #        print (i, Rpoints[i][1])
            
            #for i in range (len(Rpoints)):
            #    if (Rpoints[i][0] <= 34 and Rpoints[i][0] >= 19):
            #        Rpoints[i][0] = "R1"
            #        ranswer[i] = "R1"
            #    elif (Rpoints[i][0] <= 51 and Rpoints[i][0] >= 35):
            #        Rpoints[i][0] = "R2"
            #        ranswer[i] = "R2"
            #    else:
            #        print ("Error")
            #        print (i, Rpoints[i][1])



            for i in range (len(Rpoints)):
                if (Rpoints[i][1] <= 8):
                    Rpoints[i][1] = "L"
                    ranswer[i] = "L"
                elif (Rpoints[i][1] >=9 and Rpoints[i][1] <=16):
                    Rpoints[i][1] = "M"
                    ranswer[i] = "M"
                elif (Rpoints[i][1] >= 17):
                    Rpoints[i][1] = "H"
                    ranswer [i] = "H"
                else:
                    print ("Error")
                    print (i, RPoints[i][1])
            refanswer = []

            for i in ptstrn:
                Trainpoints.append(FPoints[i])
            for i in ptstst:
                Testpoints.append(FPoints[i])
                answer.append(ranswer[i])
                refanswer.append(tempanswer[i])

            
            length = len(Testpoints)
            SF = []
            for i in range(length):
                #Get nearest neighbors
                neighbors = get_neighbors(Trainpoints, Testpoints[i], k)
                #Convert Reference frame to a dataframe for future manipulation
                df = DataFrame (Rpoints,columns=['id_no', 'w', 'h_max', 'ha_max', 'n_max', 'na_max', 's_max', 'sa_max', 'e_max', 'ea_max', 'w_max', 'wa_max'])
                #columns to check
                #fcheck = ['ha_max', 'na_max', 'sa_max', 'ea_max', 'wa_max']
                fcheck = ['h_max', 'n_max', 's_max', 'e_max', 'w_max']
                first_column = []
                #iterate through all neighbors
                for neighbor in neighbors:
                    #find corresponding weight
                    dff = df.query(fcheck[0] + ' == ' + str(neighbor[0]) + ' and ' + fcheck[1] + ' == ' + str(neighbor[1])+ ' and ' + fcheck[2] + ' == ' + str(neighbor[2])+ ' and ' + fcheck[3] + ' == ' + str(neighbor[3])+ ' and ' + fcheck[4] + ' == ' + str(neighbor[4]))
                    #print(dff)
                    first_column.append(dff.iloc[0, 1])
                PF.append(max(set(first_column), key=first_column.count))

                tally[int(refanswer[i])-1] = tally[int(refanswer[i])-1]+1
                if (answer[i] == PF[i]):
                    tallyf.append(1)
                    tallyp[int(refanswer[i])-1] = tallyp[int(refanswer[i])-1] + 1
                else:
                    tallyf.append(0)

            tanswer = tanswer + answer
            tPF = tPF + PF
            truth = tallyf.count(1)
            total = len(tallyf)
            percentage.append(truth/total)
        tpercentage = (sum(percentage))/(len(percentage))
        stdev = statistics.stdev(percentage)
        print (k)
        #cmat = sklearn.metrics.confusion_matrix(tanswer, tPF, labels=["NW", "NE", "SW", "SE"])
        cmat = sklearn.metrics.confusion_matrix(tanswer, tPF, labels=["L", "M", "H"])
        #cmat = cmat
        print(cmat)

        res = list(map(truediv, tallyp, tally))
        bar = list(range(1, 25))
        res[8] = 0
        res[9] = 0
        res[17] = 0
        plt.barh(bar, res)
        plt.suptitle('Accuracy of each weight class')
        plt.xlabel("Accuracy")
        plt.ylabel("Weight")
        plt.show()



        print("Accuracy Distribution: ", res)
        print(sklearn.metrics.classification_report(tanswer, tPF, digits=3))
        print ("St Dev: ", stdev)
        print ("Accuracy :", tpercentage)
        