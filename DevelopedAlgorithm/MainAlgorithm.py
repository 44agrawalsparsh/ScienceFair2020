#Integrates the Deep Learning, Monte Carlo and ACO algorithms together
#The algorithm starts with local greedy solutions for the first hour and half. Afterwards it will generate ACO solutions
import PyACO.PathFinder as ACO
import PyACO
import PyACO.PyMonteCarlo.MonteCarlo as TripPredictor
import PyACO.PyMonteCarlo.TaxiTripClasses as TripClasses
import shapely
import numpy as np
import datetime
from shapely.geometry import Point as shpPt
import random
import matplotlib.pyplot as plt
import copy
import multiprocessing
from multiprocessing import Process
import os


TripPredictor.NUMBEROFPREDICTIONS = (6 + 3) #6 timesteps of trips plus 3 timesteps of accurate dropoff demand projections	

		
#A single timestep. Stores the state of passengers, taxis and a PathFinder object.
class RouteFrame:
	def __init__(self):
		#The number of taxis expected to be full during the entirety of the timestep
		self.BusyTaxiCount = 0
		#All the passenger locations expected to exist
		self.PassengerLocations = []

		#All the taxi locations that are estimated to start off vacant in each route frame
		self.TaxiLocations = []
		#All the taxi locations that are expected to be vacant at the end of the timestep
		self.RemainingTaxis = []

		#All the taxi locations that are expected to not be vacant for the timestep but for the next one
		self.TaxiLocations30Delay = []
		#All the taxi locations that are expected to not be vacant for the timestep but for the next to next one
		self.TaxiLocations45Delay = []

		self.Optimizer = None
		self.OptimizerType = 'GREEDY'

	#Sort the passenger and taxi locations
	def sortLocations(self):
		self.PassengerLocations.sort(key = ACO.Graph.sortKey)
		self.TaxiLocations.sort(key = ACO.Graph.sortKey)

	#Add a PathFinder object
	def addPathFinder(self, pathfinder, Greedy):
		self.Optimizer = pathfinder
		if Greedy:
			self.OptimizerType = 'GREEDY'
		else:
			self.OptimizerType = 'ACO'

	def __repr__(self):
		return "<BusyTaxiCount:%s PassengerCount:%s TaxiCount:%s RemainingTaxis: %s TaxiLocations30Delay: %s TaxiLocations45Delay: %s>" % (self.BusyTaxiCount, len(self.PassengerLocations), len(self.TaxiLocations), len(self.RemainingTaxis), len(self.TaxiLocations30Delay), len(self.TaxiLocations45Delay))
	def __str__(self):
		return "<BusyTaxiCount:%s PassengerCount:%s TaxiCount:%s RemainingTaxis: %s TaxiLocations30Delay: %s TaxiLocations45Delay: %s>" % (self.BusyTaxiCount, len(self.PassengerLocations), len(self.TaxiLocations), len(self.RemainingTaxis), len(self.TaxiLocations30Delay), len(self.TaxiLocations45Delay))


#A TripBench object manages a series of route frames
class TripBench:

	def __init__(self, samples):
		self.Bench = np.empty(shape=samples, dtype=object)
		self.Trips = []

		for i in range(len(self.Bench)):
			self.Bench[i] = RouteFrame()


	#With the updated set of predicted trips, the trip bench leaps forward one timestep.
	def moveForward(self, trips):
		#Updates the set of trips
		self.Trips = trips
		#Keeps a copy of the existing state while updating
		curBench = copy.deepcopy(self.Bench)
		#Shifts each routeframe on the bench one to the left
		for i in range(len(curBench) - 1):
			self.Bench[i] = curBench[i + 1]

		#Adds a blank route frame to the farthest position on the bench
		self.Bench[len(curBench) - 1] = RouteFrame()

		latestFrame = self.Bench[-1]


		#Updates the passenger locations for each route frame
		for i in range(len(self.Trips)):
			stepTrips = self.Trips[i]
			stepTrips.sort()

			self.Bench[i].PassengerLocations = []


			for trip in stepTrips:
				self.Bench[i].PassengerLocations.append(ACO.Graph.convertToShapely(trip.startingPoint))

		#Reset all the estimated taxi locations except for the ones that are impacted by the next timestep
		self.Bench[0].RemainingTaxis = []

		for i in range(1, len(self.Bench)):
			self.Bench[i].TaxiLocations = []
			self.Bench[i].RemainingTaxis = []
			self.Bench[i].BusyTaxiCount = 0
			if(i == 2):
				self.Bench[i].TaxiLocations.extend(self.Bench[i].TaxiLocations45Delay)
				self.Bench[i - 1].BusyTaxiCount = len(self.Bench[i].TaxiLocations45Delay)
			elif(i == 1):
				self.Bench[i].TaxiLocations.extend(self.Bench[i].TaxiLocations45Delay)
				self.Bench[i].TaxiLocations.extend(self.Bench[i].TaxiLocations30Delay)
			
			self.Bench[i].TaxiLocations30Delay = []
			self.Bench[i].TaxiLocations45Delay = []

		cityPoly = ACO.genNYC()

		#Simulate where future taxi locations should be
		for timestep in range(len(self.Bench) - 1):

			routeFrame = self.Bench[timestep]
			routeFrame.sortLocations()


			path = routeFrame.Optimizer.getBestPath()

			TripSet = copy.deepcopy(self.Trips[timestep])

			

			if len(routeFrame.TaxiLocations) > len(routeFrame.PassengerLocations):

				for trip in TripSet:

					start = trip.startingPoint
					end = trip.endingPoint

					length = trip.length


					RFJump = int(length/15)

					for j in range(1, RFJump):
						try:
							self.Bench[timestep + j].BusyTaxiCount += 1
						except IndexError:
							pass

					if RFJump > 0:
						try:
							self.Bench[timestep + RFJump].TaxiLocations.append(ACO.Graph.convertToShapely(end))
						except IndexError:
							pass
					else:
						routeFrame.RemainingTaxis.append(ACO.Graph.convertToShapely(end))

					if RFJump == 2:
						try:
							self.Bench[timestep + 2].TaxiLocations30Delay.append(ACO.Graph.convertToShapely(end))
						except IndexError:
							pass
					if RFJump == 3:
						try:
							self.Bench[timestep + 3].TaxiLocations45Delay.append(ACO.Graph.convertToShapely(end))
						except IndexError:
							pass

				REMAINING_TAXIS_COUNT = len(routeFrame.TaxiLocations) - len(routeFrame.PassengerLocations)

				remainingTaxiIndices = random.sample(range(len(routeFrame.TaxiLocations)), REMAINING_TAXIS_COUNT)

				for i in remainingTaxiIndices:
					pt = routeFrame.TaxiLocations[i]

					taxiIndex = getPolyFromPoint(path.taxiPolies, pt, i, len(routeFrame.TaxiLocations))
					if taxiIndex != None:
						try:
							passengerIndex = path.dispatch[taxiIndex]

							passengerPoly = path.passengerPolies[passengerIndex]

							newPt = ACO.Graph.getCentroidPointInPoly(passengerPoly, cityPoly)
							routeFrame.RemainingTaxis.append((ACO.Graph.convertToShapely(newPt)))
						except KeyError:
							pass
					else:
						routeFrame.RemainingTaxis.append(ACO.Graph.convertToShapely(pt))

			else:
				NUMBER_TRIPS_TAKEN = len(routeFrame.PassengerLocations) - len(routeFrame.TaxiLocations)
				remainingTripIndices = random.sample(range(len(TripSet)), NUMBER_TRIPS_TAKEN)

				for tripIndex in remainingTripIndices:
					trip = TripSet[tripIndex]
					start = trip.startingPoint
					end = trip.endingPoint

					length = trip.length


					RFJump = int(length/15)

					for j in range(1, RFJump):
						try:
							self.Bench[timestep + j].BusyTaxiCount += 1
						except IndexError:
							pass
					if RFJump > 0:
						try:
							self.Bench[timestep + RFJump].TaxiLocations.append(ACO.Graph.convertToShapely(end))
						except IndexError:
							pass
					else:
						routeFrame.RemainingTaxis.append(ACO.Graph.convertToShapely(end))

			try:
				self.Bench[timestep + 1].TaxiLocations.extend(routeFrame.RemainingTaxis)
			except IndexError:
				pass

		#Add a PathFinder object for the furthest routeframe
		taxiLocs = self.Bench[-1].TaxiLocations

		passLocs = self.Bench[-1].PassengerLocations

		opt = genACOFinder(taxiLocs, passLocs)


		self.Bench[-1].addPathFinder(opt,False)



	



#Given a polygon and a route frame, identify a taxi location or passenger location within that polygon
def getPointFromPoly(poly, polyIndex, route_frame, taxi, numPolies):
	if(taxi):
		midIndex = int(polyIndex/numPolies*len(route_frame.TaxiLocations))

		taxiList = route_frame.TaxiLocations

		loc = ACO.Graph.convertToShapely(taxiList[midIndex])

		if(poly.contains(loc)):
			return midIndex

		for i in range(100):

			if midIndex + i < len(taxiList):
				if midIndex + i:
					loc1 = ACO.Graph.convertToShapely(taxiList[midIndex + i])

					if(poly.contains(loc1)):
						return midIndex + i

			if midIndex - i > 0:
				if midIndex - i:
					loc2 = ACO.Graph.convertToShapely(taxiList[midIndex - i])

					
					if(poly.contains(loc2)):
						return midIndex - i
	else:
		midIndex = int(polyIndex/numPolies*len(route_frame.PassengerLocations))

		passengerList = route_frame.PassengerLocations

		loc = ACO.Graph.convertToShapely(passengerList[midIndex])

		if(poly.contains(loc)):
			return midIndex

		for i in range(100):

			if midIndex + i < len(passengerList):
				if midIndex + i:
					loc1 = ACO.Graph.convertToShapely(passengerList[midIndex + i])

					if(poly.contains(loc1)):
						return midIndex + i

			if midIndex - i > 0:
				if midIndex - i:
					loc2 = ACO.Graph.convertToShapely(passengerList[midIndex - i])

					
					if(poly.contains(loc2)):
						return midIndex - i

#Given a list of polygons and a point, identify the polygon that contains the point. This method is faster than getPolyFromPointBare because it inputs the index of the point allowing for a base estimate of which polygon contains the point.
def getPolyFromPoint(poliesList, point, index, max_range):
	midIndex = int(index/max_range*len(poliesList))

	if(poliesList[midIndex].contains(ACO.Graph.convertToShapely(point))):
		return midIndex

	for i in range(1000):
		if midIndex + i < len(poliesList):
			poly1 = poliesList[midIndex + i]

			if(poly1.contains(ACO.Graph.convertToShapely(point))):
				return midIndex + i

		if midIndex - i > 0:
			poly2 = poliesList[midIndex - i]

			

			if(poly2.contains(ACO.Graph.convertToShapely(point))):
				return midIndex - i

#Given a list of polygons and a point, identify the polygon that contains the point.
def getPolyFromPointBare(poliesList, point):
	midIndex = int(len(poliesList)/2)

	if(poliesList[midIndex].contains(ACO.Graph.convertToShapely(point))):
		return midIndex

	for i in range(1000):
		if midIndex + i < len(poliesList):
			poly1 = poliesList[midIndex + i]

			if(poly1.contains(ACO.Graph.convertToShapely(point))):
				return midIndex + i

		if midIndex - i > 0:
			poly2 = poliesList[midIndex - i]

			

			if(poly2.contains(ACO.Graph.convertToShapely(point))):
				return midIndex - i



#Generate a path finder for a greedy solution
def genGreedyFinder(taxis, passengers):
	return ACO.PathFinder(taxis=copy.deepcopy(taxis), passengers=copy.deepcopy(passengers), triplengths=ACO.loadTripLengths(), city=ACO.genNYC(), numberOfAnts=1, taxi_clusters=100, passenger_clusters=100, greedy=True)
#Generate a path finder for an ACO solution
def genACOFinder(taxis, passengers, inputGraph = None):
	if len(taxis) < 1000 or len(passengers) < 1000:
		return ACO.PathFinder(taxis=copy.deepcopy(taxis), passengers=copy.deepcopy(passengers), triplengths=ACO.loadTripLengths(), city=ACO.genNYC(), input_graph=inputGraph, taxi_clusters=100, passenger_clusters=100)

	else:
		return ACO.PathFinder(taxis=copy.deepcopy(taxis), passengers=copy.deepcopy(passengers), triplengths=ACO.loadTripLengths(), city=ACO.genNYC(), input_graph=inputGraph)


SIM_DATE_TO_REAL = 0

REAL_DATE_TO_SIM = 0

#Generate converters for SIMDATE to REALDATe and vice versa
def startSimDate(fileName):
	simDate = datetime.datetime.strptime(fileName, '%Y-%m-%dT%H-%M-%S.csv')
	curDate = datetime.datetime.now()

	difference = curDate - simDate
	
	def SIMTOREAL(simDateInput):
		return simDateInput + difference

	def REALTOSIM(realDateInput):
		return realDateInput - difference

	return SIMTOREAL, REALTOSIM

#Given a start file and taxi count, set up a bench to use the algorithm. Output the local greedy solution for the first few timesteps.
def setUp(startFile, numTaxis):

	SIM_DATE_TO_REAL, REAL_DATE_TO_SIM = startSimDate(startFile)

	simStart = datetime.datetime.strptime(startFile, '%Y-%m-%dT%H-%M-%S.csv')

	setUpEnd = simStart + datetime.timedelta(minutes=15)

	optBench = TripBench(TripPredictor.NUMBEROFPREDICTIONS - 3)
	optBench.Trips = TripPredictor.getTrips(startFile)

	taxis = ACO.genRandomTaxis(numTaxis)


	cityPoly = ACO.genNYC()
	for taxi in taxis:
		optBench.Bench[0].TaxiLocations.append(ACO.Graph.convertToShapely(taxi))

	for i in range(len(optBench.Trips)):
		trips = optBench.Trips[i]
		trips.sort()
		passengerLocs = optBench.Bench[i].PassengerLocations

		for trip in trips:
			passengerLocs.append(ACO.Graph.convertToShapely(trip.startingPoint))


	for timestep in range(len(optBench.Bench)):

		greedy = True

		if(timestep == TripPredictor.NUMBEROFPREDICTIONS - 3 - 1):
			greedy = False



		routeFrame = optBench.Bench[timestep]
		routeFrame.sortLocations()

		if(greedy):
			finder =  genGreedyFinder(routeFrame.TaxiLocations, routeFrame.PassengerLocations)
			routeFrame.addPathFinder(finder, greedy)
			routeFrame.Optimizer.iterate()
		else:
			finder =  genACOFinder(routeFrame.TaxiLocations, routeFrame.PassengerLocations)
			routeFrame.addPathFinder(finder, greedy)

			while(REAL_DATE_TO_SIM(datetime.datetime.now()) < setUpEnd - datetime.timedelta(minutes=1)):

				routeFrame.Optimizer.iterate()

		path = routeFrame.Optimizer.getBestPath()

		TripSet = copy.deepcopy(optBench.Trips[timestep])

		

		if len(routeFrame.TaxiLocations) > len(routeFrame.PassengerLocations):

			for trip in TripSet:

				start = trip.startingPoint
				end = trip.endingPoint

				length = trip.length


				RFJump = int(length/15)

				for j in range(1, RFJump):
					try:
						optBench.Bench[timestep + j].BusyTaxiCount += 1
					except IndexError:
						pass

				if RFJump > 0:
					try:
						optBench.Bench[timestep + RFJump].TaxiLocations.append(ACO.Graph.convertToShapely(end))
					except IndexError:
						pass
				else:
					routeFrame.RemainingTaxis.append(ACO.Graph.convertToShapely(end))

				if RFJump == 2:
					try:
						optBench.Bench[timestep + 2].TaxiLocations30Delay.append(ACO.Graph.convertToShapely(end))
					except IndexError:
						pass
				if RFJump == 3:
					try:
						optBench.Bench[timestep + 3].TaxiLocations45Delay.append(ACO.Graph.convertToShapely(end))
					except IndexError:
						pass

			REMAINING_TAXIS_COUNT = len(routeFrame.TaxiLocations) - len(routeFrame.PassengerLocations)

			remainingTaxiIndices = random.sample(range(len(routeFrame.TaxiLocations)), REMAINING_TAXIS_COUNT)

			for i in remainingTaxiIndices:
				pt = routeFrame.TaxiLocations[i]

				taxiIndex = getPolyFromPoint(path.taxiPolies, pt, i, len(routeFrame.TaxiLocations))
				if taxiIndex != None:
					try:
						passengerIndex = path.dispatch[taxiIndex]

						passengerPoly = path.passengerPolies[passengerIndex]

						newPt = ACO.Graph.getCentroidPointInPoly(passengerPoly, cityPoly)
						routeFrame.RemainingTaxis.append((ACO.Graph.convertToShapely(newPt)))
					except KeyError:
						pass
				else:
					routeFrame.RemainingTaxis.append(ACO.Graph.convertToShapely(pt))

		else:
			NUMBER_TRIPS_TAKEN = len(routeFrame.PassengerLocations) - len(routeFrame.TaxiLocations)
			remainingTripIndices = random.sample(range(len(TripSet)), NUMBER_TRIPS_TAKEN)

			for tripIndex in remainingTripIndices:
				trip = TripSet[tripIndex]
				start = trip.startingPoint
				end = trip.endingPoint

				length = trip.length


				RFJump = int(length/15)

				for j in range(1, RFJump):
					try:
						optBench.Bench[timestep + j].BusyTaxiCount += 1
					except IndexError:
						pass
				if RFJump > 0:
					try:
						optBench.Bench[timestep + RFJump].TaxiLocations.append(ACO.Graph.convertToShapely(end))
					except IndexError:
						pass
				else:
					routeFrame.RemainingTaxis.append(ACO.Graph.convertToShapely(end))

		try:
			optBench.Bench[timestep + 1].TaxiLocations.extend(routeFrame.RemainingTaxis)
		except IndexError:
			pass

	return optBench, optBench.Bench[0].Optimizer.getBestPath()

#Used for concurrently iterating through many RouteFrame Optimizers
def worker(RF, procnum, return_dict):
	for i in range(100):
		RF.Optimizer.iterate()
		return_dict[procnum] = copy.deepcopy(RF.Optimizer)

#Concurrently iterates all the PathFinder while moving the Bench forward one timestep.
def calculateTimeStep(bench, fileName, processingMinutes):
	calcEnd = datetime.datetime.now() + datetime.timedelta(minutes=processingMinutes)
	tripBench = copy.deepcopy(bench)

	manager = multiprocessing.Manager()
	return_dict = manager.dict()
	procs = []

	for i in range(1, len(tripBench.Bench)):
		try:
			RF = tripBench.Bench[i]
			proc = Process(target=worker, args=(RF, i - 1, return_dict))
			procs.append(proc)
			proc.start()
		except Exception as e:
			print(e)

	trips = TripPredictor.getTrips(fileName)

	tripBench.moveForward(trips)

	try:
		RF = tripBench.Bench[-1]
		proc = Process(target=worker, args=(RF,len(tripBench.Bench) - 1, return_dict))
		procs.append(proc)
		proc.start()
	except Exception as e:
		print(e)

	while datetime.datetime.now() < calcEnd:
		pass

	for proc in procs:
		proc.terminate()
		proc.join()

	for key in return_dict.keys():
		tripBench.Bench[key].Optimizer = copy.deepcopy(return_dict[key])

	return tripBench, tripBench.Bench[0].Optimizer.getBestPath()

#Prepare the deep learning inputs for 50 samples starting from a given sample
def prepInputs(fileName):
	filesList = os.listdir('RAWDATA/TRIPRECORDSSIMULATION') 
	filesList.sort()

	fileNameIndex = TripPredictor.binary_search(filesList, fileName)

	filesToPrep = filesList[fileNameIndex:fileNameIndex+50]

	fileNameIndex += 50

	for name in filesToPrep:
		TripPredictor.preparePoints(name)

	return filesList, fileNameIndex
