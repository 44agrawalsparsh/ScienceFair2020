import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.spatial as sp
import shapely.geometry as sg
from shapely.geometry.polygon import Polygon
from matplotlib import colors as mcolors
import Voronoi_boundaries as vb
import main_plot as mplot
import csv

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Use: ", sys.argv[0], "[file name] [state shape file name] [output file name]")
        exit(-1)
    C_3D, A, assign_pairs, bbox = vb.Parse(sys.argv[1])
    power_cells = vb.power_cells_fromfile(sys.argv[1])
    #print(power_cells)

    '''sX = []
    sY = []

    with open(sys.argv[2], 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            sX.append(row[0])
            sY.append(row[1])

    #plt.plot(sX,sY) '''

    for poly in power_cells:
        x = []
        y = []

        x, y = poly.exterior.coords.xy

        plt.plot(x,y)

        print("Polygon Coordinates")

        for i in range(0,len(x)):
            print(x[i], y[i]) 

    
    plt.show()








'''


    mplot.plot_helperVoronoi(C_3D, A, assign_pairs, bbox,
                             sys.argv[3]+"voronoi")
    mplot.plot_helperGNUplot(C_3D, A, power_cells, bbox, sys.argv[2],
                             sys.argv[3], False) '''
