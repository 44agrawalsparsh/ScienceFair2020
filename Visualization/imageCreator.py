#Takes in a file with a list of polygons and generates an image representing them.

import shapely.wkt
import os
import shapefile
import shapely.geometry
import shapely.ops
import matplotlib.pyplot as plt
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import Point
from shapely.geometry.multipolygon import MultiPolygon
import cv2
import numpy as np
import math
import datetime
import PIL
import imageio
import os
from interruptingcow import timeout


#Process the city boundaries of NYC

cityPolygon = shapely.wkt.loads('POLYGON((-74.175568 40.64626200000002,-74.184322 40.64613099999998,-74.202175 40.63115099999999,-74.203033 40.614995,-74.20475 40.606524000000014,-74.199257 40.60079000000001,-74.1996 40.59779199999999,-74.206467 40.58866800000002,-74.21333300000002 40.563894000000026,-74.21814 40.55737400000002,-74.228439 40.558939,-74.244576 40.551635000000026,-74.251785 40.54407000000001,-74.245949 40.52319500000001,-74.256935 40.512755000000006,-74.261055 40.498398,-74.254532 40.48899800000001,-74.113598 40.53154599999998,-74.064846 40.58293100000001,-73.943653 40.537678,-73.794114 40.58383800000001,-73.7566129 40.58165330000001,-73.75653 40.58617099999997,-73.738552 40.59621400000001,-73.738116 40.60262800000003,-73.74374800000001 40.607650000000014,-73.745486 40.611902999999984,-73.755248 40.61018000000004,-73.766452 40.614870999999994,-73.7674398 40.6212288,-73.7454847 40.636091999999984,-73.7324653 40.65686349999999,-73.7089862 40.751039300000016,-73.7732095 40.80597790000001,-73.748374 40.87182600000002,-73.823189 40.89119900000001,-73.822376 40.889478,-73.838238 40.894113000000004,-73.841439 40.90416699999999,-73.853278 40.90741099999999,-73.859262 40.90045300000001,-73.918281 40.917610999999994,-73.922968 40.897749000000005,-73.93198700000002 40.87872200000001,-73.950614 40.85475300000002,-73.960991 40.82939799999999,-74.014549 40.757920000000006,-74.034806 40.68727699999999,-74.066734 40.64339600000001,-74.081497 40.653425,-74.093685 40.64821499999998,-74.109478 40.64821499999998,-74.125614 40.643787,-74.134369 40.64391699999998,-74.142952 40.64209399999998,-74.175568 40.64626200000002))')


bounds = cityPolygon.bounds

minX = bounds[0]
minY = bounds[1]
maxX = bounds[2]
maxY = bounds[3]

imgSize = 1000


def convX(x):
	return (round(0.98*imgSize*(x-minX)/(maxX-minX))+imgSize*0.01)

def convY(y):
	return (round(0.98*imgSize*(y-minY)/(maxY-minY))+imgSize*0.01)


scaledNYC = shapely.ops.transform(lambda x, y, z=None: (convX(x), convY(y)), cityPolygon)
boundary = scaledNYC.boundary



boundPoints = []
for i in range(1,round(boundary.length)*5):
	multiplier = float(i)/round(boundary.length)
	boundPoints.append(boundary.interpolate(multiplier, normalized=True))

bX = []
bY =[]
for pt in boundPoints:
	bX.append(pt.x)
	bY.append(pt.y)

def genImg(fileName, outputfile):
	#Go line by line
	#Convert WKT to Shapely.Polygon and add to list
	#Obtain the shapefile of NYC and extract the multipolygon
	#For each Polygon in list, take the boundary coordnates and store it in a list (just needs to be a 1D list of Shapely.Point objects, not a 2D list of 100 Polygons and their boundaries)
	#For each point, if it is not within the city polygon, delete it
	#add the boundary points of the city
	#Generate a new 2D list of 100 2 object arrays (x and y), by running convertToArray on each point
	#Generate a 1000*1000 array of ints (each object is currently a 0) This will be called imageArray from here on out
	#For each point in the list, make imageArray[x-1][y-1] = 1
	#return imageArray

	startImg = np.ones([imgSize,imgSize])*255

	i = 0

	polies = []
	points = []

	cityPolygon = shapely.wkt.loads('POLYGON((-74.175568 40.64626200000002,-74.184322 40.64613099999998,-74.202175 40.63115099999999,-74.203033 40.614995,-74.20475 40.606524000000014,-74.199257 40.60079000000001,-74.1996 40.59779199999999,-74.206467 40.58866800000002,-74.21333300000002 40.563894000000026,-74.21814 40.55737400000002,-74.228439 40.558939,-74.244576 40.551635000000026,-74.251785 40.54407000000001,-74.245949 40.52319500000001,-74.256935 40.512755000000006,-74.261055 40.498398,-74.254532 40.48899800000001,-74.113598 40.53154599999998,-74.064846 40.58293100000001,-73.943653 40.537678,-73.794114 40.58383800000001,-73.7566129 40.58165330000001,-73.75653 40.58617099999997,-73.738552 40.59621400000001,-73.738116 40.60262800000003,-73.74374800000001 40.607650000000014,-73.745486 40.611902999999984,-73.755248 40.61018000000004,-73.766452 40.614870999999994,-73.7674398 40.6212288,-73.7454847 40.636091999999984,-73.7324653 40.65686349999999,-73.7089862 40.751039300000016,-73.7732095 40.80597790000001,-73.748374 40.87182600000002,-73.823189 40.89119900000001,-73.822376 40.889478,-73.838238 40.894113000000004,-73.841439 40.90416699999999,-73.853278 40.90741099999999,-73.859262 40.90045300000001,-73.918281 40.917610999999994,-73.922968 40.897749000000005,-73.93198700000002 40.87872200000001,-73.950614 40.85475300000002,-73.960991 40.82939799999999,-74.014549 40.757920000000006,-74.034806 40.68727699999999,-74.066734 40.64339600000001,-74.081497 40.653425,-74.093685 40.64821499999998,-74.109478 40.64821499999998,-74.125614 40.643787,-74.134369 40.64391699999998,-74.142952 40.64209399999998,-74.175568 40.64626200000002))')

	superX = []
	superY = []
	
	with open(fileName, 'rb') as source:
		for r in source:
			encoding = 'utf-8'
			string = str(r, encoding)
			
			P = shapely.wkt.loads(string)
			P2 = shapely.ops.transform(lambda x, y, z=None: (convX(x), convY(y)), P)

			boundary = P2.boundary

			numInterlopes = round(boundary.length)*5

			for i in range(1,numInterlopes):
				multiplier = float(i)/numInterlopes
				points.append(boundary.interpolate(multiplier, normalized=True))
	
	lines = []

	checkedPoints = []

	arrayPoints = []

	for point in points:
		pt = Point(point)
		if(scaledNYC.contains(pt)):
			checkedPoints.append(pt)
			arrayPoints.append(pt)
	
	for pt in boundPoints:
		arrayPoints.append(pt)

	for pt in arrayPoints:
		x = int(pt.x)
		y = int(pt.y)
		a = 90
		modifiedX = -(x-1)
		modifiedY = -(y-1)

		startImg[modifiedX][modifiedY] = 0

	# Perform the counter clockwise rotation holding at the center
	# 90 degrees
	
	M = cv2.getRotationMatrix2D((imgSize/2,imgSize/2), 270, 1.0)
	
	output = cv2.warpAffine(startImg, M, (imgSize, imgSize))

	imageio.imwrite(outputfile, img)


