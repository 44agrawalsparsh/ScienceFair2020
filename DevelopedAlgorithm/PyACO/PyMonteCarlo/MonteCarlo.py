from .PyTaxiNet import DataProcessor as dp
import csv
import tensorflow as tf

import datetime
import numpy as np
import statistics
import joblib
import random
import shapely.wkt
import shapely
import shapely.ops
import math
import copy
from .TaxiTripClasses import Point, Cluster, Timestep, Trip, TripRecord
import os

#Ensure that the program is able to import PyClusterize
import sys

sys.path.append('PyACO/')

import PyClusterize.ClusterWrapper as clusterer
from tensorflow.keras.models import model_from_json, Model, load_model


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

CONVERGEMIN = 0.98

NUMBEROFPREDICTIONS = 0

NUMBEROFTRIPRECORDS = 10000

FILEPATHTODATA = 'PyACO/PyMonteCarlo/Data/'

FILEPATHTORAWDATA = 'RAWDATA/'

FILEPATHTOMODEL = 'PyACO/PyMonteCarlo/Model/'

FILEPATHTOTRIPRECORDS = FILEPATHTORAWDATA + 'TRIPRECORDS/'

PSIFilePath = FILEPATHTODATA + 'RequestSpatial'
PQIFilePath = FILEPATHTODATA + 'RequestQuantity'
DSIFilePath = FILEPATHTODATA + 'DropoffSpatial'
DQIFilePath = FILEPATHTODATA + 'DropoffQuantity'

PSIScalers = [joblib.load(FILEPATHTOMODEL + 'Scalers/PSXScaler.save'), joblib.load(FILEPATHTOMODEL + 'Scalers/PSYScaler.save'), joblib.load(FILEPATHTOMODEL + 'Scalers/PSRScaler.save')]

PQIScaler = joblib.load(FILEPATHTOMODEL + 'Scalers/PQScaler.save')

DSIScalers = [joblib.load(FILEPATHTOMODEL + 'Scalers/DSXScaler.save'), joblib.load(FILEPATHTOMODEL + 'Scalers/DSYScaler.save'), joblib.load(FILEPATHTOMODEL + 'Scalers/DSRScaler.save')]

DQIScaler = joblib.load(FILEPATHTOMODEL + 'Scalers/DQScaler.save')

FILELISTPATH = 'PyACO/PyMonteCarlo/Data/listOfPoints.csv'


VERSION = 1
SAMPLE_SIZE = 24

TripRecords = []
TimeSteps = []

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

#Standard binary search function
def binary_search(elements, target, low=0, high=' '):
	if(high == ' '):
		high = len(elements) - 1
	if(high >= low):
		middle = int((high + low)/2)
		if(elements[middle] == target):
			return middle
		elif(elements[middle] > target):
			return binary_search(elements=elements, target=target, low=low, high=(middle - 1))
		else:
			return binary_search(elements=elements, target=target, low=(middle + 1), high=high)
	else:
		return -1

#Generates intital x sample to predict future samples
def getInitialInputs(dateSample):
	files = getFiles(FILELISTPATH)
	maxIndex = binary_search(files, dateSample)
	start = maxIndex - 99
	end = maxIndex + 1

	if start < 0:
		start = 0
	fileList = files[start:maxIndex+1]
	fileList = dp.fileListCalc(fileList, PSIFilePath, DSIFilePath)
	PSInput = dp.processSpatialDataWithScalers(PSIFilePath, SAMPLE_SIZE,fileList, PSIScalers)
	DSInput = dp.processSpatialDataWithScalers(DSIFilePath, SAMPLE_SIZE,fileList, DSIScalers)

	PQInput = dp.processQuantityDataWithScalers(PQIFilePath, SAMPLE_SIZE,fileList, PQIScaler)
	DQInput = dp.processQuantityDataWithScalers(DQIFilePath, SAMPLE_SIZE,fileList, DQIScaler)


	return([PSInput, DSInput, PQInput, DQInput])

#Predicts future taxi demand for a set prediction window
def getPredictedTimesteps(sampleX):

	model = load_model(FILEPATHTOMODEL + 'Model.h5')
	
	x = sampleX
	preds = []
	output = []
	for i in range(NUMBEROFPREDICTIONS):

		predictedY = model.predict(x, batch_size=1)
		
		nextPSX = np.array([np.concatenate([x[0][0][1:], [predictedY[0][0]]]).tolist()])
		nextDSX = np.array([np.concatenate([x[1][0][1:], [predictedY[1][0]]]).tolist()])
		nextPQX = np.array([np.concatenate([x[2][0][1:], [predictedY[2][0]]]).tolist()])
		nextDQX = np.array([np.concatenate([x[3][0][1:], [predictedY[3][0]]]).tolist()])

		x = [nextPSX, nextDSX, nextPQX, nextDQX]
		
		preds.append(predictedY)

	for i in range(len(preds)):
		output.append(predictionToTimestep(preds[i]))

	return output

#Converts predicted demand to a timestep object
def predictionToTimestep(prediction):
	pickupSpatial = prediction[0][0]
	dropoffSpatial = prediction[1][0]
	pickupQuantity = prediction[2][0]
	dropoffQuantity = prediction[3][0]

	newPickupQuantity = int(PQIScaler.inverse_transform([pickupQuantity])[0][0] + 0.5)
	newDropoffQuantity = int(DQIScaler.inverse_transform([dropoffQuantity])[0][0] + 0.5)

	pickupSpatialX = []
	pickupSpatialY = []
	pickupSpatialR = []

	for i in range(len(pickupSpatial)):
		value = pickupSpatial[i]
		if(i % 3 == 0):
			pickupSpatialX.append(value)
		elif(i % 3 == 1):
			pickupSpatialY.append(value)
		elif(i%3 == 2):
			pickupSpatialR.append(value)

	pickupSpatialX = PSIScalers[0].inverse_transform([pickupSpatialX])[0]
	pickupSpatialY = PSIScalers[1].inverse_transform([pickupSpatialY])[0]
	pickupSpatialR = PSIScalers[2].inverse_transform([pickupSpatialR])[0]

	dropoffSpatialX = []
	dropoffSpatialY = []
	dropoffSpatialR = []

	for i in range(len(dropoffSpatial)):
		value = dropoffSpatial[i]
		if(i % 3 == 0):
			dropoffSpatialX.append(value)
		elif(i % 3 == 1):
			dropoffSpatialY.append(value)
		elif(i%3 == 2):
			dropoffSpatialR.append(value)

	dropoffSpatialX = DSIScalers[0].inverse_transform([dropoffSpatialX])[0]
	dropoffSpatialY = DSIScalers[1].inverse_transform([dropoffSpatialY])[0]
	dropoffSpatialR = DSIScalers[2].inverse_transform([dropoffSpatialR])[0]

	pickupPolies = []
	dropoffPolies = []


	pickupClusterQuantity = newPickupQuantity/len(pickupSpatialX)
	dropoffClusterQuantity = newDropoffQuantity/len(dropoffSpatialX)
	for i in range(0, len(pickupSpatialX)):
		point = Point(pickupSpatialX[i], pickupSpatialY[i])
		size = pickupSpatialR[i]
		amount = pickupClusterQuantity
		cluster = Cluster(point, size, amount, True)
		pickupPolies.append(cluster)

	for i in range(0, len(dropoffSpatialX)):
		point = Point(dropoffSpatialX[i], dropoffSpatialY[i])
		size = dropoffSpatialR[i]
		amount = dropoffClusterQuantity
		cluster = Cluster(point, size, amount, True)
		dropoffPolies.append(cluster)

	output = Timestep(pickupPolies, dropoffPolies)

	return(output)

#Loads past trip records
def getTripRecords(dateSample):
	files = getFiles(FILELISTPATH)
	maxIndex = binary_search(files, dateSample)
	fileList = files[maxIndex-100:maxIndex][::-1]

	output = []
	for fileName in fileList:
		filePath = FILEPATHTOTRIPRECORDS + fileName
		with open(filePath) as fp:
			reader = csv.reader(fp, delimiter=',')
			for line in reader:
				startingPoint = Point(convX(float(line[2])), convY(float(line[3])))
				endingPoint = Point(convX(float(line[4])), convY(float(line[5])))
				startTime = datetime.datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S')
				endTime = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S')
				record = TripRecord(startingPoint, endingPoint, startTime, endTime)
				output.append(record)
				if(len(output) >= NUMBEROFTRIPRECORDS):
					return output

#Estimates travel time between two clusters using a set of past trips
def getTripLength(cluster1, cluster2, tripList):
	startX = cluster1.centroid.x
	startY = cluster1.centroid.y

	endX = cluster2.centroid.x
	endY = cluster2.centroid.y

	cluster1Range = cluster1.radius*4
	cluster2Range = cluster2.radius*4

	def validTrip(record):
		startPoint = record.startingPoint
		endPoint = record.endingPoint
		
		startValid = (math.sqrt((startX-startPoint.x)**2 + (startY-startPoint.y)**2) <= cluster1Range)
		endValid = (math.sqrt((endX-endPoint.x)**2 + (endY-endPoint.y)**2) <= cluster2Range)

		return(startValid and endValid)

	duration = 0
	for trip in tripList:
		if(validTrip(trip)):
			duration = trip.length
			break

	return(duration)

#Identifies if a set of timesteps have converged to a set of likely trips
def converge(timesteps):
	filledRates = []

	for step in timesteps:
		pickups = step.pickupClusters
		dropoffs = step.dropoffClusters

		for cluster in pickups:
			filledRates.append((len(cluster.trips)/cluster.count))
		for cluster in dropoffs:
			filledRates.append((len(cluster.trips)/cluster.count))

	filledRate = (sum(filledRates)/len(filledRates))

	if(filledRate >= CONVERGEMIN):
		return True
	else:
		return False
		
#Identifies which trips are possible depending one stimated travel time and past frequency.
def generatePossibleTrips(timesteps, records):
	for i in range(len(timesteps)):
		curStep = timesteps[i]
		for startCluster in curStep.pickupClusters:
			try:
				for finalCluster in timesteps[i].dropoffClusters:
					tripLength = getTripLength(startCluster, finalCluster, records)
					possibleTrip = Trip(startCluster, finalCluster, tripLength)
					if(tripLength > 0 and tripLength <= 15):
						startCluster.addPossibleTrip(possibleTrip)
			except IndexError:
				pass
			try:
				for finalCluster in timesteps[i+1].dropoffClusters:
					tripLength = getTripLength(startCluster, finalCluster, records)
					possibleTrip = Trip(startCluster, finalCluster, tripLength)
					if(tripLength > 15 and tripLength <= 30):
						startCluster.addPossibleTrip(possibleTrip)
			except IndexError:
				pass
			try:
				for finalCluster in timesteps[i+2].dropoffClusters:
					tripLength = getTripLength(startCluster, finalCluster, records)
					possibleTrip = Trip(startCluster, finalCluster, tripLength)
					if(tripLength > 30 and tripLength <= 45):
						startCluster.addPossibleTrip(possibleTrip)
			except IndexError:
				pass
			try:
				for finalCluster in timesteps[i+3].dropoffClusters:
					tripLength = getTripLength(startCluster, finalCluster, records)
					possibleTrip = Trip(startCluster, finalCluster, tripLength)
					if(tripLength > 45 and tripLength <= 60):
						startCluster.addPossibleTrip(possibleTrip)
			except IndexError:
				pass

	return timesteps

#Identifies favorable trips
def generateFavorableTrips(timesteps):
	iterations = 1
	while converge(timesteps) == False:
		iterations += 1
		for step in timesteps:
			pickups = step.pickupClusters
			dropoffs = step.dropoffClusters

			for cluster in pickups:
				for i in range(cluster.count - len(cluster.trips)):
					cluster.addTrip()

			for cluster in dropoffs:
				for i in range(cluster.count - len(cluster.trips)):
					cluster.addTrip()

	return timesteps

#Takes a collection of timesteps with favorable trips and produces a list of predicted TripRecords
def getPredictedTrips(timesteps, startTimeFile):
	startTime = datetime.datetime.strptime(startTimeFile, '%Y-%m-%dT%H-%M-%S.csv')
	#Generates a random point around a circle with a set radius. Ensures that the point is within the city limits.
	def getRandomPoint(centroid, radius):
		x = 0
		y = 0
		while(not scaledNYC.contains(shapely.geometry.Point(x,y))):
			r = radius * math.sqrt(random.random())
			theta = random.random() * 2 * math.pi
			x = centroid.x + r * math.cos(theta)
			y = centroid.y + r * math.sin(theta)
		return Point(x,y)
	output = []
	for i in range(len(timesteps)):
		step = timesteps[i]
		stepTrips = []
		for cluster in step.pickupClusters:
			for trip in cluster.trips:
				length = trip.duration
				startPoint = getRandomPoint(trip.start.centroid, trip.start.radius)
				endPoint = getRandomPoint(trip.start.centroid, trip.start.radius)
				startingTime = startTime + datetime.timedelta(seconds=(i*15*60 + random.random()*15*60))
				endingTime = startingTime + datetime.timedelta(seconds=(length*60))
				stepTrips.append(TripRecord(startPoint, endPoint,startingTime,endingTime))
		output.append(stepTrips)
	return output

#Preprocesses the inputs for the Deep Learning Model
def preparePoints(fileName):
	pickupData = FILEPATHTORAWDATA + 'PICKUPS/' + fileName

	dropoffData = FILEPATHTORAWDATA + 'DROPOFFS/' + fileName

	clusterer.genNetInput(pickupData, PSIFilePath + '/' + fileName, cityPolygon)

	clusterer.genNetInput(dropoffData, DSIFilePath + '/' + fileName, cityPolygon)

	pickupCount = sum(1 for line in open(pickupData))
	dropoffCount = sum(1 for line in open(dropoffData))

	pCount = open(PQIFilePath +'/' + fileName, 'w')

	pCount.write(str(pickupCount))

	pCount.close()

	dCount = open(DQIFilePath +'/' + fileName, 'w')

	dCount.write(str(dropoffCount))

	dCount.close()

	fileList = open(FILELISTPATH, 'a')

	fileList.write("\n" + fileName)

	fileList.close()

#Wrapper for all the methods in the file. Generates predicted trips with the input filename
def getTrips(fileName):
	preparePoints(fileName)
	timeSteps = getPredictedTimesteps(getInitialInputs(fileName))
	records = getTripRecords(fileName)
	timeSteps = generatePossibleTrips(timeSteps, records)
	timeSteps = generateFavorableTrips(timeSteps)
	trips = getPredictedTrips(timeSteps,fileName)[:-3]

	return trips

