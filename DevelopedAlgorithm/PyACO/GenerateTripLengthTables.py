'''
This file was written in a seperate development environment for the ACO algorithm. If required, the file can easily be run again with minor changes to the declared directories.
'''
#Using the google maps API or any other web API to determine the travel time between two locations is not feasible unless in production due to the high costs. I developed this file to determine the travel time between two points using historical taxi trips.

from PyMonteCarlo.TaxiTripClasses import Point, Cluster, Timestep, Trip, TripRecord
import numpy as np
import shapely.wkt
import os
import csv
import datetime
import random

cityPolygon = shapely.wkt.loads('POLYGON((-74.175568 40.64626200000002,-74.184322 40.64613099999998,-74.202175 40.63115099999999,-74.203033 40.614995,-74.20475 40.606524000000014,-74.199257 40.60079000000001,-74.1996 40.59779199999999,-74.206467 40.58866800000002,-74.21333300000002 40.563894000000026,-74.21814 40.55737400000002,-74.228439 40.558939,-74.244576 40.551635000000026,-74.251785 40.54407000000001,-74.245949 40.52319500000001,-74.256935 40.512755000000006,-74.261055 40.498398,-74.254532 40.48899800000001,-74.113598 40.53154599999998,-74.064846 40.58293100000001,-73.943653 40.537678,-73.794114 40.58383800000001,-73.7566129 40.58165330000001,-73.75653 40.58617099999997,-73.738552 40.59621400000001,-73.738116 40.60262800000003,-73.74374800000001 40.607650000000014,-73.745486 40.611902999999984,-73.755248 40.61018000000004,-73.766452 40.614870999999994,-73.7674398 40.6212288,-73.7454847 40.636091999999984,-73.7324653 40.65686349999999,-73.7089862 40.751039300000016,-73.7732095 40.80597790000001,-73.748374 40.87182600000002,-73.823189 40.89119900000001,-73.822376 40.889478,-73.838238 40.894113000000004,-73.841439 40.90416699999999,-73.853278 40.90741099999999,-73.859262 40.90045300000001,-73.918281 40.917610999999994,-73.922968 40.897749000000005,-73.93198700000002 40.87872200000001,-73.950614 40.85475300000002,-73.960991 40.82939799999999,-74.014549 40.757920000000006,-74.034806 40.68727699999999,-74.066734 40.64339600000001,-74.081497 40.653425,-74.093685 40.64821499999998,-74.109478 40.64821499999998,-74.125614 40.643787,-74.134369 40.64391699999998,-74.142952 40.64209399999998,-74.175568 40.64626200000002))')


bounds = cityPolygon.bounds

minX = bounds[0]
minY = bounds[1]
maxX = bounds[2]
maxY = bounds[3]

#The size of 1 dimension of the output table
#3,5,10,30 and 50 were generated
imgSize = 3

#Since all we care about is the average recorded trip time, the individual data samples don't need to be stored. This class allows us to just store the total sum of n samples as well as n
class TripLength:
	def __init__ (self):
		self.amount = 0
		self.totalLength = 0

	def addSample(self, length):
		self.amount += 1
		self.totalLength += length

	def getLength(self):
		if(self.amount > 0):
			return(self.totalLength/self.amount)
		else:
			return(0)
def convX(x):
	return (round(0.98*imgSize*(x-minX)/(maxX-minX))+imgSize*0.01)

def convY(y):
	return (round(0.98*imgSize*(y-minY)/(maxY-minY))+imgSize*0.01)

#Switch to correct directory
FILEPATHTOTRIPRECORDS =''
#Switch to correct directory
FILEPATHTOLISTOFPOINTS = ''
#Switch to correct directory
FILEPATHTOTRIPLENGTHS = ''


#Loads a list of files in the folder containing all the trip records that are also present in the file containing a list of approved data samples (Samples in the trainiong data set)

def getFiles(directory=FILEPATHTOLISTOFPOINTS):
	listOfFiles = os.listdir(FILEPATHTOTRIPRECORDS)
	output = []
	for name in listOfFiles:
		try:
			output.append(name)
		except:
			pass

	return output

#Wraps each data point as a TripRecord object

def getTripRecords(fileList):
	output = []
	
	for fileName in fileList:
		filePath = FILEPATHTOTRIPRECORDS + "/" +  fileName
		try:
			with open(filePath) as fp:
				reader = csv.reader(fp, delimiter=',')
				for line in reader:
					startingPoint = Point(int(convX(float(line[2]))), int(convY(float(line[3]))))
					endingPoint = Point(int(convX(float(line[4]))), int(convY(float(line[5]))))
					startTime = datetime.datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S')
					endTime = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S')
					record = TripRecord(startingPoint, endingPoint, startTime, endTime)
					output.append(record)
		except:
			pass

	return output

#Generates a blank output table of the specified size
def getBlankWorkList():
	start = np.ndarray(shape=(imgSize,imgSize,imgSize,imgSize), dtype=object)
	for i in range(imgSize):
		for j in range(imgSize):
			for k in range(imgSize):
				for l in range(imgSize):
					start[i][j][k][l] = TripLength()
	

	return start

#Generates an output table specifying the travel time between any two cells in a grid representing the city
def getOutputList():
	start = getBlankWorkList()
	
	filelist = getFiles()
	for i in range(100):

		try:

			tempFiles = filelist[int(i*len(filelist)/100) : int((i+1)*len(filelist)/100)]

			records = getTripRecords(tempFiles)

			cnt = 0
			for record in records:
				try:
					startX = record.startingPoint.x - 1
					startY = record.startingPoint.y - 1
					endX = record.endingPoint.x - 1
					endY = record.endingPoint.y - 1

					length = record.length

					start[startX][startY][endX][endY].addSample(length)
				except Exception as e:
					pass

			del records

		except Exception as e:
			print(e)

	

	output = np.ndarray(shape=(imgSize,imgSize,imgSize,imgSize), dtype=float)

	for i in range(imgSize):
		for j in range(imgSize):
			for k in range(imgSize):
				for l in range(imgSize):
					output[i][j][k][l] = start[i][j][k][l].getLength()

	return output

#Generates the output table and saves it
def getTripLengths():
	output = getOutputList()
	fileName = "TripTimes/TripTimes-" + str(imgSize) + ".npy" 
	np.save(fileName, output)

getTripLengths()