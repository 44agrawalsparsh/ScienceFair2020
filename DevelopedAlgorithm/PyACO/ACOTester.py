'''
This file was written in a seperate development environment for the ACO algorithm. If required, the file can easily be run again with minor changes to the declared directories.
'''
import PathFinder
from PyMonteCarlo.TaxiTripClasses import *
from PyMonteCarlo import TaxiTripClasses
from PyMonteCarlo.MonteCarlo import getTrips
import numpy as np
import shapely
from shapely.geometry import Point as shpPt
from shapely.geometry.polygon import Polygon
import random
import time

#Generates a series of points for taxis. Uses the end points of a set of trips as a quick proxy for taxi locations.
def tempGenTaxis(trips):
	Taxis = []
	for trip in trips:
		Taxis.append(trip.endingPoint)

	return Taxis

FILEPATHTOLISTOFPOINTS = ''
FILEPATHTORESULTS = ''
#Generates a list of files based on a file containing a list of points
def getFiles(directory):
	output = []
	with open(directory) as fp:
		line = fp.readline()
		cnt = 1
		while line:
			output.append(str(line.replace('\n', '')))
			line = fp.readline()
			cnt += 1
	return output

fileList = getFiles(FILEPATHTOLISTOFPOINTS)

for i in range(20):

	resultFile = open(FILEPATHTORESULTS + 'Sample-' + str(i) + '.txt', 'w')

	fileName = random.choice(fileList)


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

	TripLengths = (np.load('TripTimes/TripTimes-' + '50' + ".npy").tolist(), np.load('TripTimes/TripTimes-' + '30' + ".npy").tolist(), np.load('TripTimes/TripTimes-' + '10' + ".npy").tolist(), np.load('TripTimes/TripTimes-' + '5' + ".npy").tolist(), np.load('TripTimes/TripTimes-' + '3' + ".npy").tolist())

	trips =  getTrips(fileName)


	#Dropoff locations used as a proxy for taxi locations and the passenger pickup points of two timesteps later serves the role of passenger locations
	Taxis = PathFinder.tempGenTaxis(trips[1])
	Passengers = trips[3]

	#Find the greedy path
	Cheap = PathFinder(numberOfAnts = 1, taxis=Taxis, passengers=Passengers, triplengths=TripLengths, city=scaledNYC, greedy=True)

	Cheap.iterate()

	resultFile.write("GREEDY BASLINE:" + '\n')
	resultFile.write(str(Cheap.getBestValue()) + '\n')


	#Find the ACO Path
	finder = PathFinder(boostFactor=5, alphaGrowth=1.1, betaGrowth=1.25, alphaPeak=20, betaPeak=-15,calculation_time=5400, numberOfAnts = 500, taxis=Taxis, passengers=Passengers, triplengths=loadTripLengths(), search_range=5, percent_cut=100, city=scaledNYC)

	startTime = datetime.datetime.now()
	endTime = startTime + datetime.timedelta(seconds=3600)

	while datetime.datetime.now() < endTime:
		finder.iterate()
		resultFile.write(str(datetime.datetime.now() - startTime) + ',')
		resultFile.write(str(finder.getBestValue()) + '\n')

	resultFile.close()

