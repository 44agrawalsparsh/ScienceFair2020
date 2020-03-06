from .PyMonteCarlo.TaxiTripClasses import *
from .PyMonteCarlo import TaxiTripClasses
from .PyMonteCarlo.MonteCarlo import getTrips
from .PyClusterize import ClusterWrapper
import shapely
from shapely.geometry import Point as shpPt
from shapely.geometry.polygon import Polygon
import random
import numpy as np
import datetime
import copy


#Loads the series of trip length tables
def loadTripLengths():
	TripLengths = (np.load('PyACO/TripTimes/TripTimes-' + '50' + ".npy").tolist(), np.load('PyACO/TripTimes/TripTimes-' + '30' + ".npy").tolist(), np.load('PyACO/TripTimes/TripTimes-' + '10' + ".npy").tolist(), np.load('PyACO/TripTimes/TripTimes-' + '5' + ".npy").tolist(), np.load('PyACO/TripTimes/TripTimes-' + '3' + ".npy").tolist())

	return TripLengths

#Generates a scaled version of NYC (1000x1000)
def genNYC():
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

	return scaledNYC

#Randomly generates cities within NYC
def genRandomTaxis(num):

	scaledNYC = genNYC()

	Taxis = []

	for i in range(num):
		x = 0
		y = 0
		while(not scaledNYC.contains(shapely.geometry.Point(x,y))):
			x = random.random()*1000
			y = random.random()*1000

		taxi = Point(x,y)
		Taxis.append(taxi)

	return Taxis

#Class for each node in the Ants graph
class Node:

	def __init__(self):
		self.MIN = 1
		self.MAX = 100
		self.pheromoneLevels = self.MIN
		self.Q_CONSTANT = 0
		self.PHEROMONE_RETAIN_RATE = 1
		


	#Pheromone evaporation. Used after each iteration.
	def evaporate(self):
		self.pheromoneLevels *= self.PHEROMONE_RETAIN_RATE
		if(self.pheromoneLevels < self.MIN):
			self.pheromoneLevels = self.MIN

	#Increases the pheromone count
	def addPheromones(self, deltaPheromone):
		self.pheromoneLevels += deltaPheromone
		if(self.pheromoneLevels > self.MAX):
			self.pheromoneLevels = self.MAX

	def __repr__(self):
		return str(self.pheromoneLevels)
	def __str__(self):
		return str(self.pheromoneLevels)



#Class for the graph of the ACO system
class Graph:

	#Generates a random point in a polygon that is also within the city limits. Serves as the "centroid" of the polygon
	def getCentroidPointInPoly(poly, city):
		bounds = poly.bounds

		minX = (bounds[0])
		minY = (bounds[1])
		maxX = (bounds[2])
		maxY = (bounds[3])

		if(minX < city.bounds[0]):
			minX = city.bounds[0]

		if(minY < city.bounds[1]):
			minY = city.bounds[1]

		if(maxX > city.bounds[2]):
			maxX = city.bounds[2]

		if(maxY > city.bounds[3]):
			maxY = city.bounds[3]

		if(city.contains(poly.centroid)):
			return Graph.convertToTripClasses(poly.centroid)
		while True:
			randX = random.random()*(maxX - minX) + minX
			randY = random.random()*(maxY - minY) + minY

			pt = shpPt(randX, randY)

			if poly.contains(pt) and city.contains(pt):
				return Graph.convertToTripClasses(pt)

	#Wraps a TaxiTripClasses Point object as a Shapely Point object
	def convertToShapely(point):
		return shpPt(point.x, point.y)

	#Wraps a Shapely Point object as a TaxiTripClasses Point object
	def convertToTripClasses(point):
		return TaxiTripClasses.Point(point.x, point.y)

	#Boil a polygon down to a single float value for the purposes of sorting polygons
	def sortKey(poly):
		return (poly.centroid.x**2 + poly.centroid.y**2)

	#Return an ants path lenght for the purposes of sorting
	def sortPath(ant):
		return ant.pathLength()


	#Construct the graph obkect based on the taxis and passengers
	def __init__(self, taxis, passengers, triplengths, city, boost, percent_cut, taxiClusterCount, passengerClusterCount, input_graph=None):
		self.TaxiLocations = []
		self.PassengerLocations = []
		self.BestPath = {}
		self.BestPathValue = -1
		self.GreedyPath = {}
		self.percent_cut = percent_cut
		self.boost = boost
		self.NumOfTaxiClusters = taxiClusterCount
		self.NumOfPassengerClusters = passengerClusterCount

		taxiLocs = []
		for taxi in taxis:
			taxiLocs.append(Graph.convertToShapely(taxi))


		#Convert a series of taxi locations to a series of polygons to generalize the taxis
		self.taxiPolies = ClusterWrapper.genInput(taxiLocs, city, taxiClusterCount)

		

		self.taxiPolies.sort(key=Graph.sortKey)

		passengerLocs = []
		for trip in passengers:
			passengerLocs.append(Graph.convertToShapely(trip))


		#Convert a series of passengers locations to a series of polygons to generalize the passengers
		self.passengerPolies = ClusterWrapper.genInput(passengerLocs, city, passengerClusterCount)
		self.passengerPolies.sort(key=Graph.sortKey)

		for i in range(len(self.taxiPolies)):
			self.TaxiLocations.append(Graph.convertToTripClasses(Graph.getCentroidPointInPoly(self.taxiPolies[i], city)))

		for i in range(len(self.passengerPolies)):
			self.PassengerLocations.append(Graph.convertToTripClasses(Graph.getCentroidPointInPoly(self.passengerPolies[i], city)))

		#Ensure that the two lists are the same size in case the clustering algorithm 
		if(len(self.PassengerLocations) != len(self.TaxiLocations)):
			if(len(self.PassengerLocations) > len(self.TaxiLocations)):
				self.PassengerLocations = self.PassengerLocations[:len(self.TaxiLocations)]
			else:
				self.TaxiLocations = self.TaxiLocations[:len(self.PassengerLocations)]


		#Generate a network containing all the possible dispatch solutions. If there exists a previous solution to load from, simply load the pheromone values
		self.network = np.ndarray(shape=(len(self.PassengerLocations), len(self.TaxiLocations)), dtype=object)
		for i in range(len(self.PassengerLocations)):
			for j in range(len(self.TaxiLocations)):
				try:
					self.network[i][j] = Node(input_graph.network[i][j].pheromoneLevels)
				except:
					self.network[i][j] = Node()


		self.TripLengths = triplengths

		#Identify the closest passenger cluster for each taxi cluster		
		for passengerIndex in range(len(self.network)):
			bestVal = 100000
			selectedTaxi = 10000
			for taxiIndex in range(len(self.network[passengerIndex])):
				if(self.getTripLength(passengerIndex, taxiIndex) < bestVal):
					bestVal = self.getTripLength(passengerIndex, taxiIndex)
					selectedTaxi = taxiIndex
			self.GreedyPath.update({passengerIndex : selectedTaxi})

		
	#Identify the travel time between a taxi and passenger cluster
	def getTripLength(self, passengerIndex, taxiIndex):

		passengerLoc = self.PassengerLocations[passengerIndex]

		taxiLoc = self.TaxiLocations[taxiIndex]
		coordMultiplier = (50/1000, 30/1000, 10/1000, 5/1000, 3/1000)

		lengthFound = False

		for i in range(5):
			lengthTable = self.TripLengths[i]
			multiplier = coordMultiplier[i]
			startX = int(taxiLoc.x*multiplier)
			startY = int(taxiLoc.y*multiplier)

			endX = int(passengerLoc.x*multiplier)
			endY = int(passengerLoc.y*multiplier)
			length = lengthTable[startX][startY][endX][endY]

			if(length > 0):
				#scale the distance for a rough estimate of the travel time
				trueEucDist = ((passengerLoc.x - taxiLoc.x)**2 + (passengerLoc.y - taxiLoc.y)**2)**0.5
				tableEucDist = ((endX/multiplier - startX/multiplier)**2 + (endY/multiplier - startY/multiplier)**2)**0.5
				if tableEucDist == 0:
					tableEucDist = 0.52/1.44*(2/multiplier**2)**0.5
				return length*trueEucDist/tableEucDist


		return 10000000000
			
	#Defines one iteration. Each ant will traverse the path and the pheromone levels will be updated
	def iteration(self, antList):
		#Ants generate paths
		for ant in antList:
			ant.travel()

		localBest = 10000

		antList.sort(key=Graph.sortPath, reverse=True)

		selectedAnts = antList[:int(len(antList)*self.percent_cut/100)]
		#Exavporation
		for i in range(len(self.network)):
			for j in range(len(self.network[i])):
				node = self.network[i][j]
				node.evaporate()

		for ant in selectedAnts:
			pathLength = ant.pathLength()
			if(self.BestPathValue == -1 or pathLength < self.BestPathValue):
				self.BestPathValue = pathLength
				self.BestPath = copy.deepcopy(ant.path)

			deltaPheromone = (self.network[0][0].Q_CONSTANT/(pathLength/self.NumOfPassengerClusters))
			for taxiIndex in ant.path:
				passengerIndex = ant.path[taxiIndex]
				node = self.network[passengerIndex][taxiIndex]
				node.addPheromones(deltaPheromone)
			
		for ant in antList:
			ant.reset()

		#RE-INFORCE BEST PATH FOUND
		boostPheromone = self.boost*(self.network[0][0].Q_CONSTANT/(self.BestPathValue/self.NumOfPassengerClusters))
		for taxiIndex in self.BestPath:
			passengerIndex = self.BestPath[taxiIndex]
			node = self.network[passengerIndex][taxiIndex]

#An ant class that defines how an ant moves and calculates a path length
class Ant:
	def __init__(self, graph, searchRange, greedy):
		self.graph = graph
		self.path = {}
		self.ALPHA = 1
		self.BETA = -1
		self.SEARCH_RANGE = searchRange
		self.GREEDY = greedy


	#how to select a taxi
	def selectTaxi(self, passengerIndex):
		selectedTaxi = -1
		#Get Possible Values and their weights
		taxiOptions = self.graph.network[passengerIndex]
		taxisTaken = self.path.keys()

		taxiWeights = np.zeros(len(taxiOptions))



		if not self.GREEDY:

			weightsTotal = 0

			#A tool to increase the search radius if all options have already been used
			multiplier = 4

			#Identify the weights for each taxi
			while weightsTotal == 0:

				taxiOptions = self.graph.network[passengerIndex]
				taxisTaken = self.path.keys()

				taxiWeights = np.zeros(len(taxiOptions))
			
				matching = self.graph.GreedyPath[passengerIndex]
				

				lowerBound = matching-self.SEARCH_RANGE*multiplier
				
				upperBound = matching+self.SEARCH_RANGE*multiplier
				

				if(lowerBound < 0):
					lowerBound = 0
				if(upperBound > len(taxiOptions)):
					upperBound = len(taxiOptions) 

				newTaxiOptions = taxiOptions[lowerBound:upperBound]

				for tIndex in range(len(newTaxiOptions)):
					taxiIndex = tIndex + lowerBound
					#Eliminate any taxis that have already been dispatched to ensure that each taxi is assigned to a unique passenger
					if taxiIndex not in taxisTaken:
						weight = int((taxiOptions[taxiIndex].pheromoneLevels**self.ALPHA)*(self.graph.getTripLength(passengerIndex, taxiIndex)**self.BETA)*1000) + 1 #In case there's no pheromones yet
						
						taxiWeights[taxiIndex] = weight
						weightsTotal += weight

				multiplier += 1
				

			#Randomly select taxi based on the weights of each taxi

			randWeight = int(random.random()*weightsTotal + 0.5)

			for taxiIndex in range(len(taxiWeights)):
				randWeight -= taxiWeights[taxiIndex]
				if randWeight <= 0:
					selectedTaxi = taxiIndex
					break

		else:
			#Simply choose the locally best option for each passenger. Eliminate any taxis that have already been dispatched to ensure that each taxi is assigned to a unique passenger
			bestVal = 100000
			selectedTaxi = 10000
			for taxiIndex in range(len(taxiOptions)):
				if taxiIndex not in taxisTaken:
					distance = self.graph.getTripLength(passengerIndex, taxiIndex)
					if(distance < bestVal):
						bestVal = distance
						selectedTaxi = taxiIndex




		self.path.update({selectedTaxi : passengerIndex})

	#Identify the length of the path found
	def pathLength(self):
		length = 0
		for taxi in self.path.keys():
			passenger = self.path[taxi]
			length += self.graph.getTripLength(passenger, taxi)



		return length

	#Traverse the graph
	def travel(self):
		for i in range(len(self.graph.network)):
			self.selectTaxi(i)

	#Reset the path to traverse it again
	def reset(self):
		self.path.clear()

#Acts as an API to the algorithm
class PathFinder:

	#Random search results are the default values
	def __init__(self, taxis, passengers, triplengths, city, numberOfAnts=500, search_range=5, percent_cut=100, boostFactor=5, alphaGrowth=1.1, betaGrowth=1.25, alphaPeak=20, betaPeak=-15, taxi_clusters=1000, passenger_clusters=1000, return_type=1, input_graph=None, greedy=False):

		self.alphaPeak = alphaPeak
		self.alphaGrowth = alphaGrowth

		self.betaPeak = betaPeak
		self.betaGrowth = betaGrowth


		
		self.graph = Graph(taxis, passengers, triplengths, city, boostFactor, percent_cut, taxi_clusters, passenger_clusters, input_graph)
		self.ants = []
		for i in range(numberOfAnts):
			self.ants.append(Ant(self.graph, search_range, greedy))

	#Update the evaporation rate
	def increaseEvaporation(self):
		currRate = self.graph.network[0][0].PHEROMONE_RETAIN_RATE

		newRate = currRate*0.995

		if(newRate < 0.8):
			newRate = 0.8

		for i in range(len(self.graph.network)):
			for j in range(len(self.graph.network[i])):
				self.graph.network[i][j].PHEROMONE_RETAIN_RATE = newRate
				self.graph.network[i][j].Q_CONSTANT = 2.5/newRate

	#Update the ants' selection formula 
	def changeSelectionFormula(self):
		for ant in self.ants:
			ant.ALPHA *= self.alphaGrowth
			ant.BETA *= self.betaGrowth

			if(ant.BETA < self.betaPeak):
				ant.BETA = self.betaPeak

			if(ant.ALPHA > self.alphaPeak):
				ant.ALPHA = self.alphaPeak

	#Complete an iteration
	def iterate(self):
		self.graph.iteration(self.ants)
		self.increaseEvaporation()
		self.changeSelectionFormula()
		
	#Return the graph object
	def getGraph(self):
		return self.graph

	#Return a path object containing the dispatch instructions
	def getBestPath(self):
		path = self.graph.BestPath
		taxiPolies = self.graph.taxiPolies
		passengerPolies = self.graph.passengerPolies

		output = Path(path, taxiPolies, passengerPolies)

		return output

	#Return the length of the best path found 
	def getBestValue(self):
		return self.graph.BestPathValue

#A path object contains the list of taxi and passenger clusters as well as dictionaries linking them (Taxi -> Passenger and Passenger -> Taxi)
class Path:
	def __init__(self, pathway, taxiPolies, passengerPolies):
		self.dispatch = pathway
		self.taxiPolies = taxiPolies
		self.passengerPolies = passengerPolies
		self.inverseDispatch = {v: k for k, v in pathway.items()}

