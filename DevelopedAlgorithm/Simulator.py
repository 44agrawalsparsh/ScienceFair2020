import MainAlgorithm as Dispatch
import PyACO
import numpy as np
import random
import shapely
import multiprocessing
from multiprocessing import Process
import datetime
import os
import csv
from shapely.geometry import Point as shpPt
from shapely.geometry import Polygon
import PyACO.PyMonteCarlo.MonteCarlo as TripPredictor
import pickle
import shutil
import subprocess
import copy
import time

#Open the log files
taxiLog = open('SIMULATORLOGS/TAXILOG.txt', 'w')
taxiLog.close()

passengerLog = open('SIMULATORLOGS/PASSENGERLOG.txt', 'w')
passengerLog.close()

#A class representing a taxi in the simulation
class SimTaxi:

	PATH = []
	PASSENGERS = []

	LOG = open('SIMULATORLOGS/TAXILOG.txt', 'a')

	MaxID = 1
	TRIPLENGTHS = PyACO.PathFinder.loadTripLengths()
	City = PyACO.PathFinder.genNYC()

	#Initialize the taxi with a trip length finder and start point

	def __init__(self, startPoint, tripLengthFinder):
		self.Vacant = True
		self.Assigned = False

		self.TaxiID = SimTaxi.MaxID

		SimTaxi.MaxID += 1

		self.location = startPoint

		self.assignedPassenger = None

		self.assignedEndTime = None

		self.tripLengthFinder = tripLengthFinder

	#Picks up a passenger.

	def passengerPickedUp(self, passenger, pickup_time):
		self.Assigned = True
		self.location = passenger.dropoffLocation
		self.assignedPassenger = passenger
		self.Vacant = False
		self.assignedPassenger.pickUp(pickup_time)
		self.assignedEndTime = passenger.endTime
		SimTaxi.LOG.write(str(pickup_time) + ',' + str(self.TaxiID) +',' + str(self.Vacant) + ',' + str(self.assignedPassenger.length)  + '\n')

	#Simulates the taxi's movement based on the output of the developed algorithm
	def move(self, simTime):

		if(not self.Vacant):
			if(simTime >= self.assignedEndTime):
				self.Vacant = True
				self.Assigned = False
				self.assignedEndTime = None
				self.assignedPassenger = None

		if(self.Vacant):

			if(self.Assigned):
				if(simTime >= self.assignedEndTime):
					self.Assigned = False
					self.assignedEndTime = None

			if(not self.Assigned):

				if 1 == 1:
					polies = SimTaxi.PATH.passengerPolies
					polyIndex = Dispatch.getPolyFromPointBare(polies, self.location)

					if (polyIndex != None):
						poly = polies[polyIndex]

						passengersList = SimTaxi.getPassengersInPoly(poly)
					else:
						try:
							ptList = [[self.location.x - 25, self.location.y + 25], [self.location.x + 25, self.location.y + 25], [self.location.x + 25, self.location.y - 25], [self.location.x - 25, self.location.y - 25]]
							poly = Polygon(ptList)
							passengersList = SimTaxi.getPassengersInPoly(poly)
						except IndexError:
							passengersList = []

					if(len(passengersList) > 0):

						passenger = passengersList[0]

						self.passengerPickedUp(passenger, simTime)

					else:
						try:
							polies = SimTaxi.PATH.taxiPolies
							polyIndex = Dispatch.getPolyFromPointBare(polies, self.location)
							poly = SimTaxi.PATH.passengerPolies[SimTaxi.PATH.dispatch[polyIndex]]
						except:
							polyIndex = int(random.random()*len(SimTaxi.PATH.passengerPolies))
							poly = SimTaxi.PATH.passengerPolies[polyIndex]

						passengersList = SimTaxi.getPassengersInPoly(poly)

						polyBounds = poly.bounds

						minX = polyBounds[0]
						minY = polyBounds[1]
						maxX = polyBounds[2]
						maxY = polyBounds[3]

						

						polyPoint = PyACO.PathFinder.Graph.convertToShapely(PyACO.PathFinder.Graph.getCentroidPointInPoly(poly, SimTaxi.City))

						travelLength = int(self.tripLengthFinder(shpPt(self.location.x, self.location.y), polyPoint, SimTaxi.TRIPLENGTHS)*60)	

						searchLength = int(random.random()*(self.tripLengthFinder(shpPt(minX, minY), shpPt(maxX, maxY), SimTaxi.TRIPLENGTHS)*2/(len(passengersList) + 1)*60))

						SimTaxi.LOG.write(str(simTime) + ',' + str(self.TaxiID) +',' + str(self.Vacant) + ',' + str(travelLength + searchLength)  + '\n')

						endTime = simTime + datetime.timedelta(seconds=(travelLength + searchLength))

						self.Assigned = True
						self.location = shpPt(poly.centroid.x, poly.centroid.y)
						self.assignedEndTime = endTime

				else:
					try:
						polies = SimTaxi.PATH.taxiPolies
						polyIndex = Dispatch.getPolyFromPointBare(polies, self.location)
						poly = SimTaxi.PATH.passengerPolies[SimTaxi.PATH.dispatch[polyIndex]]
					except:
						polyIndex = int(random.random()*len(SimTaxi.PATH.passengerPolies))
						poly = SimTaxi.PATH.passengerPolies[polyIndex]

					passengersList = SimTaxi.getPassengersInPoly(poly)

					polyBounds = poly.bounds

					minX = polyBounds[0]
					minY = polyBounds[1]
					maxX = polyBounds[2]
					maxY = polyBounds[3]

					if(minX < 0):
						minX = 0
					if(minY < 0):
						minY = 0

					if(maxX > 999):
						maxX = 999
					if(maxY > 999):
						maxY = 999

					polyPoint = PyACO.PathFinder.Graph.convertToShapely(PyACO.PathFinder.Graph.getCentroidPointInPoly(poly, SimTaxi.City))

					travelLength = int(self.tripLengthFinder(shpPt(self.location.x, self.location.y), polyPoint, SimTaxi.TRIPLENGTHS)*60)	

					searchLength = int(self.tripLengthFinder(shpPt(minX, minY), shpPt(maxX, maxY), SimTaxi.TRIPLENGTHS)*2/(len(passengersList) + 1)*60)

					SimTaxi.LOG.write(str(simTime) + ',' + str(self.TaxiID) +',' + str(self.Vacant) + ',' + str(travelLength + searchLength)  + '\n')

					endTime = simTime + datetime.timedelta(seconds=(travelLength + searchLength))

					self.Assigned = True
					self.location = shpPt(poly.centroid.x, poly.centroid.y)
					self.assignedEndTime = endTime


	#Simulates the taxi moving according to the status quo greedy approach. The taxi looks for a passenger in it's general area, trying to find the closest passenger to it.
	def moveGreedy(self, simTime):

		if(not self.Vacant):
			if(simTime >= self.assignedEndTime):
				self.Vacant = True
				self.Assigned = False
				self.assignedEndTime = None
				self.assignedPassenger = None

		if(self.Vacant):

			if(self.Assigned):
				if(simTime >= self.assignedEndTime):
					self.Assigned = False
					self.assignedEndTime = None

			if(not self.Assigned):

				ptList = [[self.location.x - 25, self.location.y + 25], [self.location.x + 25, self.location.y + 25], [self.location.x + 25, self.location.y - 25], [self.location.x - 25, self.location.y - 25]]
				poly = Polygon(ptList)

				passengersList = SimTaxi.getPassengersInPoly(poly)

				if(len(passengersList) > 0):

					passenger = passengersList[0]

					self.passengerPickedUp(passenger, simTime)

				else:
					newPointX = random.random()*151 - 76 + self.location.x
					newPointY = random.random()*151 - 76 + self.location.y

					if newPointX < 0:
						newPointX = 0
					elif newPointX > 999:
						newPointX = 999

					if newPointY < 0:
						newPointY = 0
					elif newPointY > 999:
						newPointY = 999

					newPtList = [[newPointX - 25, newPointY + 25], [newPointX + 25, newPointY + 25], [newPointX + 25, newPointY - 25], [newPointX - 25, newPointY - 25]]
					newPoly = Polygon(newPtList)

					polyPoint = shpPt(newPointX, newPointY)

					travelLength = int(self.tripLengthFinder(shpPt(self.location.x, self.location.y), polyPoint, SimTaxi.TRIPLENGTHS)*60)	

					searchLength = int(self.tripLengthFinder(shpPt(newPointX - 25, newPointY - 25), shpPt(newPointX + 25, newPointY + 25), SimTaxi.TRIPLENGTHS)*2/(len(passengersList) + 1)*60)

					SimTaxi.LOG.write(str(simTime) + ',' + str(self.TaxiID) +',' + str(self.Vacant) + ',' + str(travelLength + searchLength)  + '\n')

					endTime = simTime + datetime.timedelta(seconds=(travelLength + searchLength))

					self.Assigned = True
					self.location = shpPt(poly.centroid.x, poly.centroid.y)
					self.assignedEndTime = endTime

	#Identifies all the passengers within a certain area
	def getPassengersInPoly(poly):
		outputList = []

		for passenger in SimTaxi.PASSENGERS:
			if(passenger != None and not passenger.pickedUp and not passenger.expired):
				if(poly.contains(passenger.location)):
					outputList.append(passenger)

		return outputList



#A class representing a passenger in the simulation
class SimPassenger:
	MaxID = 1

	LOG = open('SIMULATORLOGS/PASSENGERLOG.txt', 'a')

	#Initializes the passenger according to the details of a trip found in the true data
	def __init__(self, startLocation, dropoffLocation, deployTime, expiredTime, Fare, length):
		self.location = startLocation
		self.dropoffLocation = dropoffLocation
		self.deployTime = deployTime
		self.expiredTime = expiredTime
		self.pickedUpTime = 'NOT YET PICKED UP'
		self.fare = Fare
		self.tripLength = length
		self.pickedUp = False
		self.PassengerID = SimPassenger.MaxID
		self.length = abs(length)
		self.expired = False

		SimPassenger.MaxID += 1

	#The taxi calls this when the passenger is picked up
	def pickUp(self, time):
		self.pickedUpTime = time
		self.endTime = self.pickedUpTime + datetime.timedelta(seconds=self.length)
		self.pickedUp = True
		self.log()

	#If a passenger isn't picked up within 15 minutes, it expires 
	def complete(self):
		self.expired = True
		self.log()

	#Logs the passengers details
	def log(self):
		SimPassenger.LOG.write(str(self.PassengerID) + ',' + str(self.deployTime)  +',' + str(self.pickedUpTime) + ',' + str(self.fare) + '\n')


TRIPLENGTHS = PyACO.PathFinder.loadTripLengths()
NUMTAXIS = 5000
FILEINDEX = 0
PASSENGERS = []


BENCH = ''
FILELIST = []

TAXIS = []

PASSENGERS = []


DIFFERENCE = ''

#Method to identify the travel time between two points. This method is an input to the SimTaxi constructer.
def getTripLength(start, end, TripLengths):
	coordMultiplier = (50/1000, 30/1000, 10/1000, 5/1000, 3/1000)

	lengthFound = False

	sX = start.x
	sY = start.y

	eX = end.x
	eY = end.y

	if(sX < 0):
		sX = 0
	elif sX > 999:
		sX = 999

	if(sY < 0):
		sY = 0
	elif sY > 999:
		sY = 999

	if(eX < 0):
		eX = 0
	elif eX > 999:
		eX = 999

	if(eY < 0):
		eY = 0
	elif eY > 999:
		eY = 999

	for i in range(5):
		lengthTable = TripLengths[i]
		multiplier = coordMultiplier[i]
		startX = int(sX*multiplier)
		startY = int(sY*multiplier)

		endX = int(eX*multiplier)
		endY = int(eY*multiplier)
		
		length = lengthTable[startX][startY][endX][endY]

		if(length > 0):
			#scale the distance for a rough estimate of the travel time
			trueEucDist = ((eX - sX)**2 + (eY - sY)**2)**0.5
			tableEucDist = ((endX/multiplier - startX/multiplier)**2 + (endY/multiplier - startY/multiplier)**2)**0.5
			if tableEucDist == 0:
				tableEucDist = 0.52/1.44*(2/multiplier**2)**0.5
			output = length*trueEucDist/tableEucDist

			if output > 10:
				output = random.random()*8

			if output < 2:
				output = random.random() + 2

			return output

#Randomly generates taxis within NYC limits
def genTaxis(numTaxis):
	global TAXIS
	city = PyACO.PathFinder.genNYC()
	for i in range(numTaxis):
		pt = shpPt(-10,-10)

		while not city.contains(pt):
			x = (random.random()*1000 + 0.5)
			y = (random.random()*1000 + 0.5)

			pt = shpPt(x,y)

		taxi = SimTaxi(pt, getTripLength)

		TAXIS.append(taxi)

#Initializes the simulation. Calls the setUp method in the MainAlgorithm and generates taxis.
def getStarted(fileName, developed):
	global FILEINDEX
	global BENCH
	global PATH
	global FILELIST
	
	if developed:
		FILELIST, FILEINDEX = Dispatch.prepInputs(fileName)
		
		BENCH, PATH = Dispatch.setUp(FILELIST[FILEINDEX], NUMTAXIS)

	genTaxis(NUMTAXIS)

#Simulates 15 minutes of the simulation with the outputs of the developed algorithm. Also runs the algorithm as a subprocess.
def sim15Minutes():
	global FILEINDEX
	global TAXIS
	global PASSENGERGRID
	global BENCH
	global PATH
	global DIFFERENCE
	global PASSENGERS

	FILEINDEX += 1

	time.sleep(180) #Processer requires a break after concurrently running the algorithm and simulator at the same time

	DIFFERENCE = datetime.datetime.now() - datetime.datetime.strptime(FILELIST[FILEINDEX], '%Y-%m-%dT%H-%M-%S.csv')

	realEnd = datetime.datetime.strptime(FILELIST[FILEINDEX + 1], '%Y-%m-%dT%H-%M-%S.csv') + DIFFERENCE

	emergencyEnd = realEnd + datetime.timedelta(minutes=5)

	dataDir = FILELIST[FILEINDEX]

	processingTime = int((realEnd - datetime.datetime.now()).total_seconds()/60)

	filename = 'SubProcessFiles/Input/INPUTBENCH'
	outfile = open(filename,'wb')

	pickle.dump(BENCH, outfile)

	outfile.close()

	outfile = open('SubProcessFiles/Input/InputDetails.txt', 'w')

	outfile.write(dataDir + '\n')
	outfile.write(str(processingTime))
	outfile.close()

	p = subprocess.Popen(['python', 'AlgorithmSubprocess.py'], close_fds=True)

	addPassengers(FILEINDEX)

	SimTaxi.PATH = PATH
	SimTaxi.PASSENGERS = PASSENGERS

	while p.poll() == None and datetime.datetime.now() < emergencyEnd: #An emergency end clause is added in case some failure occurs and the subprocess never actually finishes

		curTime = datetime.datetime.now()
		simTime = curTime - DIFFERENCE
		
		for taxi in TAXIS:
			
			taxi.move(simTime)


	if p.poll() != None:
		p.kill()


	PASSENGERS = copy.copy(SimTaxi.PASSENGERS)

	benchfile = open('SubProcessFiles/Output/OUTPUTBENCH', 'rb')
	BENCH = copy.deepcopy(pickle.load(benchfile))
	benchfile.close()

	pathfile = open('SubProcessFiles/Output/PATH', 'rb')
	PATH = copy.deepcopy(pickle.load(pathfile))
	pathfile.close()


#Simulates according to a status quo model where taxis look for the nearest passenger to them.
def simGreedy():
	global FILEINDEX
	global TAXIS
	global PASSENGERGRID
	global BENCH
	global PATH
	global DIFFERENCE
	global PASSENGERS

	FILEINDEX += 1

	dataDir = FILELIST[FILEINDEX]

	DIFFERENCE = datetime.datetime.now() - datetime.datetime.strptime(FILELIST[FILEINDEX], '%Y-%m-%dT%H-%M-%S.csv')

	realEnd = datetime.datetime.strptime(FILELIST[FILEINDEX + 1], '%Y-%m-%dT%H-%M-%S.csv') + DIFFERENCE

	addPassengers(FILEINDEX)

	SimTaxi.PASSENGERS = PASSENGERS

	while datetime.datetime.now() < realEnd:

		curTime = datetime.datetime.now()
		simTime = curTime - DIFFERENCE
		
		for taxi in TAXIS:
			
			taxi.moveGreedy(simTime)

	PASSENGERS = copy.copy(SimTaxi.PASSENGERS)
	


#Generates the 'scalers'. These take the raw coordinates of a historical trip and transform them into a 1000x1000 scale according to the boundaries of NYC.
def genScales():

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


	return convX, convY

convX, convY = genScales()



#Adds passengers to the simulation from raw data of trips that occured. Also expires any passenger that has had to wait for more than 15 minutes.
def addPassengers(index):
	global PASSENGERS
	global DIFFERENCE

	PASSENGERS = []

	fileName = FILELIST[index]

	fileDir = 'RAWDATA/TRIPRECORDSSIMULATION/' + fileName

	deployTime = datetime.datetime.now() - DIFFERENCE

	expiredTime = deployTime + datetime.timedelta(minutes=15)


	ALREADY_EXPIRED = deployTime

	for i, passenger in enumerate(PASSENGERS):
		if passenger != None:
			if (not passenger.expired and not passenger.pickedUp and passenger.expiredTime <= ALREADY_EXPIRED):
				passenger.complete()
				PASSENGERS[i] = None
			elif passenger.pickedUp:
				PASSENGERS[i] = None



	with open(fileDir) as fp:
		rdr = csv.reader(fp)

		for line in rdr:
			startX = int(convX(float(line[2]))) 
			startY = int(convY(float(line[3]))) 

			endX = int(convX(float(line[4]))) 
			endY = int(convY(float(line[5]))) 

			startLocation = shpPt(startX, startY)
			dropoffLocation = shpPt(endX, endY)

			length = (datetime.datetime.strptime(str(line[1]), '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(str(line[0]), '%Y-%m-%d %H:%M:%S')).total_seconds()

			Fare = float(line[6])

			passenger = SimPassenger(startLocation, dropoffLocation, deployTime, expiredTime, Fare, length)

			PASSENGERS.append(passenger)

FILENAME = '2019-03-21T10-00-00.csv'

USE_DEVELOPED = True

getStarted(FILENAME, USE_DEVELOPED)

if USE_DEVELOPED:
	for i in range(100):
		sim15Minutes()
else:
	for i in range(100):
		simGreedy()
