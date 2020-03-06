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
    if len(sys.argv) < 3:
        print("Use: ", sys.argv[0], "[file name] [output file name]")
        exit(-1)
        
    C_3D, A, assign_pairs, bbox = vb.Parse(sys.argv[1])
    power_cells = vb.power_cells_fromfile(sys.argv[1])
    fileName = open(sys.argv[2], 'wb')
    for poly in power_cells:
        fileName.write(str(poly.wkt) + "\n")
 
