#From August, 2016, the NYC TLC Dataset doesn't give the exact co-ordinates of passenger trips but rather just a general zone where they were located. 
#This file was written to be able to take a given generalized zone and convert it into an exact pair of co-ordinates for the developed algorithm and simulator

import shapefile
import random
from shapely.geometry import shape, Polygon, Point

#Identifie the NYC TLC zone that a point exists in
def identifyZone(x,y):
    complete = False
    zone = 0
    sf = shapefile.Reader('taxi_zones.shp')
    pt = Point(x,y)
    while(complete == False):
        zone += 1
        poly = getPolygon(getBoundaryPoints(zone))
        if(poly.contains(pt)):
            complete = True
    return zone

#Identifies the boundary points of the NYC TLC general area for a specified index id
def getBoundaryPoints(index):
    sf = shapefile.Reader('taxi_zones.shp')
    x = next(x for x in sf.iterShapeRecords()  if x.record[0]==index)

    pts = []
    for i in range(1,len(x.shape.points)):
        pt = x.shape.points[i]
        pts.append([pt[0],pt[1]])
    return pts

#Constructs a polygon from a series of points
def getPolygon(pts):
    constructInput = []
    for pt in pts:
        x = pt[0]
        y = pt[1]

        addition = [x,y]
        constructInput.append(addition)

    poly = Polygon(constructInput)

    return poly
    
#Generates a random point within a polygon
def generatePoint(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p

#Given the NYC TLC region ID, a random coordinate in the polygon is generated
def convert(index):
    return generatePoint(getPolygon(getBoundaryPoints(index)))

#Generates a new point in the NYC TLC general area from an existing point
def newPoint(x,y):
    convert(identifyZone(x,y))

    