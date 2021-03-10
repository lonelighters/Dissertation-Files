import numpy as np
import csv

"""
lines = []
pnodesz = np.load('Hpoints.npy')
changenodes = [0, 19, 23, 27, 31]
weights = [1, 5, 10]
print (pnodesz)
a = 0
for t in changenodes:
    print (t)
    for i in weights:
        temp = '%d\t%d\t%.3f' % (t, i, pnodesz[a])
        lines.append([temp])
        a = a + 1

pnodesz = np.load('Npoints.npy')
changenodes = [19, 23, 27, 31]
weights = [1, 5, 10]
print (pnodesz)
a = 0
for t in changenodes:
    print (t)
    for i in weights:
        temp = '%d\t%d\t%.3f' % (t, i, pnodesz[a])
        lines.append([temp])
        a = a + 1

pnodesz = np.load('Spoints.npy')
print (pnodesz)
a = 0
for t in changenodes:
    print (t)
    for i in weights:
        temp = '%d\t%d\t%.3f' % (t, i, pnodesz[a])
        lines.append([temp])
        a = a + 1

pnodesz = np.load('Epoints.npy')
print (pnodesz)
a = 0
for t in changenodes:
    print (t)
    for i in weights:
        temp = '%d\t%d\t%.3f' % (t, i, pnodesz[a])
        lines.append([temp])
        a = a + 1

pnodesz = np.load('Wpoints.npy')
print (pnodesz)
a = 0
for t in changenodes:
    print (t)
    for i in weights:
        temp = '%d\t%d\t%.3f' % (t, i, pnodesz[a])
        lines.append([temp])
        a = a + 1
"""

#N = ['Hpoints','Npoints','Spoints','Epoints','Wpoints']
def CSVconv(node_names, changenodes, weights):
    #for node_names in N:
    lines = []
    pnodesz = np.load(node_names + '.npy')
    #print (pnodesz)
    a = 0
    for t in changenodes:
        #print (t)
        for i in weights:
            #temp = '%d\t%d\t%.3f\t%.3f' % (t, i, pnodesz[a][0], pnodesz[a][1])
            temp = '%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f' % (t, i, pnodesz[a][0], pnodesz[a][1], pnodesz[a][2], pnodesz[a][3], pnodesz[a][4], pnodesz[a][5], pnodesz[a][6], pnodesz[a][7], pnodesz[a][8], pnodesz[a][9])
            lines.append([temp])
            a = a + 1

    with open('AutomatedTesting\ ' + node_names + '.csv', mode= 'w') as points:
        writer = csv.writer(points, lineterminator='\n')
        csv.register_dialect('lineterminator')
        writer.writerows(lines)
    #print (lines)

