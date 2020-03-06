import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib import colors as mcolors
import scipy.spatial as sp
import shapely.geometry as sg
from shapely.geometry.polygon import Polygon
from matplotlib import colors as mcolors

from shapely.geometry.polygon import LinearRing
from shapely.geometry import Point
from shapely.geometry.multipolygon import MultiPolygon
import shapely.ops
#import main_plot as mplot
import csv
import os
import random
import math


#A class to take in a polygon and store its key features
class ReducedPoly:
    def __init__(self, poly):
        self.x = poly.centroid.x
        self.y = poly.centroid.y

        self.radius = (math.sqrt(float(poly.area)/3.141592))


#Generate a voronoi diagram from a series of locations (Used for the ACO algorithm)
def genInput(locations, cityPoly, polyAmount):
    openFile = open('PyACO/PyClusterize/Temp/district_input.csv', 'wb')
    openFile.close()
    result = open('PyACO/PyClusterize/Temp/district_input.csv', 'a')



    for loc in locations:
        if(cityPoly.contains(loc)):
            result.write(str(loc.x + 5*(random.random() - 0.5)) + ' ' + str(loc.y + 5*(random.random() - 0.5)) + ' ' + '1' + "\n")

    result.close()

    os.system('./PyACO/PyClusterize/do_redistrict ' + str(polyAmount) + ' PyACO/PyClusterize/Temp/district_input.csv')
    return genPolies(cityPoly)

#Generate the input for the predictive model
#Generates polygons and then stores their key features
def genNetInput(input_directory, output_directory, cityPoly, polyAmount=100):

    try:

        outputFile = open(output_directory, 'w')

        bounds = cityPoly.bounds

        minX = bounds[0]
        minY = bounds[1]
        maxX = bounds[2]
        maxY = bounds[3]

        imgSize = 1000


        def convX(x):
            return (round(0.98*imgSize*(x-minX)/(maxX-minX))+imgSize*0.01)

        def convY(y):
            return (round(0.98*imgSize*(y-minY)/(maxY-minY))+imgSize*0.01)

        scaledCity = shapely.ops.transform(lambda x, y, z=None: (convX(x), convY(y)), cityPoly)

        def reducedPolySort(reduced):
            return reduced.y

        result = open('PyACO/PyClusterize/Temp/district_input.csv', 'w')


        with open(input_directory, 'r') as inputFile:
            rdr= csv.reader(inputFile)
            for r in rdr:
                result.write(str(r[0]) + ' ' + str(r[1]) + ' 1' + '\n')

        result.close()


        os.system('./PyACO/PyClusterize/do_redistrict ' + str(polyAmount) + ' PyACO/PyClusterize/Temp/district_input.csv')


        rawPolies = genPolies(cityPoly)

        polies = []

        for poly in rawPolies:
            polies.append(shapely.ops.transform(lambda x, y, z=None: (convX(x), convY(y)), poly))

        newPolies = []

        for poly in polies:
            x, y = poly.exterior.coords.xy
            polyPts = []
            for i in range(len(x)):
                pt = Point(x[i], y[i])
                if(scaledCity.contains(pt)):
                    polyPt = [x[i], y[i]]
                    polyPts.append(polyPt)

            
            try:
                newPolies.append(Polygon(polyPts))
            except:
                pass


        
        reducedPolies = []

        for poly in newPolies:
            reducedPolies.append(ReducedPoly(poly))


        reducedPolies.sort(key=reducedPolySort, reverse=True)

        outputFile.write('x-coord, y-coord, radius\n')

        for redPol in reducedPolies:
            outputFile.write(str(redPol.x) + "," + str(redPol.y) + "," + str(redPol.radius) + '\n')

        outputFile.close()
    except Exception as e:
        print(e)
#
#
# Following code was not written by Sparsh Agrawal. This, along with the C Code, is the work of Cohen-Added, Klein and Young
#
#
#


def genPolies(cityPoly):
    #C_3D, A, assign_pairs, bbox = Parse("/Volumes/Sparsh_Passport/Sparsh-Data/ScienceFair/2019-2020/Zone_Creation/Polygons/Requests/YellowCabs/do_redistrict_output.txt")
    polies = power_cells_fromfile("PyACO/PyClusterize/Temp/do_redistrict_output.txt")

    return polies

def Parse(filename):
    f = open(filename, "r")
    lines = f.readlines()
    s = lines[0].split()
    nb_centers = int(s[0])
    nb_clients = int(s[1])
    x_min, y_min, z_min = (float("inf"),float("inf"),float("inf"))
    x_max, y_max, z_max = (-float("inf"),-float("inf"),-float("inf"))
    
    C = []
    for i in range(1, nb_centers+1):
        s = lines[i].split()
        x = float(s[0])
        y = float(s[1])
        z = float(s[2])
        C.append([x,y,z])
        x_max = max(x_max, x)
        y_max = max(y_max, y)
        z_max = max(z_max, z)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        z_min = min(z_min, z)
        
    assign_pairs = {}
    A = []
    j = 0
    for i in range(nb_centers+1, nb_centers+nb_clients+1):
        s = lines[i].split()
        x = float(s[0])
        y = float(s[1])
        A.append([x,y])
        assign_pairs[j] = int(s[2])
        j+=1
        x_max = max(x_max, x)
        y_max = max(y_max, y)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
    f.close()
    return C,A,assign_pairs, [[x_min,y_min,z_min],[x_max,y_max,z_max]]

def find_extent(bbox):
    minpt, maxpt = bbox
    return [maxpt[i] - minpt[i] for i in range(3)]

def unbounded(input_region): return any(x==-1 for x in input_region)

def find_proj(bounded_regions):
    proj_regions = []
    # print(bounded_regions)
    for i in range(len(bounded_regions)):
        region = bounded_regions[i]
        proj_regions.append([])
        for p1 in region:
            if p1[2] < 0: continue
            for p2 in region:
                if p2[2] > 0: continue
                v = [p2[0]-p1[0],
                     p2[1]-p1[1],
                     p2[2]-p1[2]]
                t = -p1[2]/v[2]
                proj_point = [p1[0] + t*v[0],
                              p1[1] + t*v[1]]
                proj_regions[i].append(proj_point)
    return proj_regions

def power_cells(C_3D, bbox):
    minpt, maxpt = bbox
    extent = find_extent([minpt,maxpt])
    smallpt, bigpt = [minpt[i]-extent[i] for i in range(3)], [maxpt[i]+extent[i] for i in range(3)]
    boundary = np.array([smallpt, [bigpt[0],smallpt[1],smallpt[2]],
                     [smallpt[0],bigpt[1],smallpt[2]],
                     [smallpt[0],smallpt[1],bigpt[2]],
                     [bigpt[0],bigpt[1],smallpt[2]],
                     [smallpt[0],bigpt[1],bigpt[2]],
                     [bigpt[0],smallpt[1],bigpt[2]],
                     bigpt])
    diagram = sp.Voronoi(np.concatenate((C_3D,boundary)))
    bounded_regions = [[diagram.vertices[j] for j in region]
                       for region in diagram.regions
                       if region != [] and not unbounded(region)]
    proj_regions = find_proj(bounded_regions)
    return [sg.MultiPoint(region).convex_hull for region in proj_regions
            if region != []]

def power_cells_fromfile(filename):
    C_3D, A, assign_pairs, bbox = Parse(filename)
    return power_cells(C_3D, bbox)