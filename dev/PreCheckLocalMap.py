#!/usr/bin/env python

'''
MIT License

Copyright (c) 2017 Tairan Liu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

__author__ = "Tairan Liu"
__copyright__ = "Copyright 2017, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "MIT"
__version__ = "0.4-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"


def loadData(path):
    infileList = []
    with open(path,'r') as inf:
        infileList = inf.readlines()
    dataList = []
    for temparea in infileList:
        templist = temparea.split()
        if int(templist[2]) == 16:
            dataList.append(templist[4:])
    #print(dataList)
    return dataList

def plotAreas(cornerList):
    fig1 = plt.figure()
    #plt.axes()
    ax = fig1.add_subplot(111, aspect='equal')
    patchList = []
    edge_x_min = float(cornerList[0][2])
    edge_x_max = float(cornerList[0][2])
    edge_y_min = float(cornerList[0][0])
    edge_y_max = float(cornerList[0][0])
    for i in range(len(cornerList)):
        corner = cornerList[i]
        x = min(float(corner[2]), float(corner[3]))
        y = min(float(corner[0]), float(corner[1]))
        dx = abs(float(corner[2]) - float(corner[3]))
        dy = abs(float(corner[0]) - float(corner[1]))
        edge_x_min = min(edge_x_min, x)
        edge_x_max = max(edge_x_max, max(float(corner[2]), float(corner[3])))
        edge_y_min = min(edge_y_min, y)
        edge_y_max = max(edge_y_max, max(float(corner[0]), float(corner[1])))
        patchList.append(patches.Rectangle((x,y), dx, dy, fill=False))
    print(len(patchList))
    for p in patchList:
        ax.add_patch(p)
    fig_x_min = edge_x_min - 0.1*(edge_x_max - edge_x_min)
    fig_x_max = edge_x_max + 0.1*(edge_x_max - edge_x_min)
    fig_y_min = edge_y_min - 0.1*(edge_y_max - edge_y_min)
    fig_y_max = edge_y_max + 0.1*(edge_y_max - edge_y_min)
    ax.set_xlim(fig_x_min, fig_x_max)
    ax.set_ylim(fig_y_min, fig_y_max)
    plt.show()
    #fig1.savefig('Areas.png', dpi=300, bbox_inches='tight')

def plotAreas2(tileList):
    fig1 = plt.figure()
    #plt.axes()
    ax = fig1.add_subplot(111, aspect='equal')
    patchList = []
    edge_x_min = float(tileList[0][0])
    edge_x_max = float(tileList[0][0])
    edge_y_min = float(tileList[0][1])
    edge_y_max = float(tileList[0][1])
    xList = []
    yList = []
    for i in range(len(tileList)):
        tile = tileList[i]
        x = float(tile[0])
        y = float(tile[1])
        xList.append(x)
        yList.append(y)
        edge_x_min = min(edge_x_min, x)
        edge_x_max = max(edge_x_max, x)
        edge_y_min = min(edge_y_min, y)
        edge_y_max = max(edge_y_max, y)

    ax.plot(xList, yList, 'ro')
    fig_x_min = edge_x_min - 0.1*(edge_x_max - edge_x_min)
    fig_x_max = edge_x_max + 0.1*(edge_x_max - edge_x_min)
    fig_y_min = edge_y_min - 0.1*(edge_y_max - edge_y_min)
    fig_y_max = edge_y_max + 0.1*(edge_y_max - edge_y_min)
    ax.set_xlim(fig_x_min, fig_x_max)
    ax.set_ylim(fig_y_min, fig_y_max)
    plt.show()

def main():
    path = 'mapcache.txt'
    dataList = loadData(path)
    plotAreas2(dataList)

if __name__ == "__main__":
    main()
