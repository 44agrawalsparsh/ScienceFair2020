import random
import datetime

#Custom made point class created to be able to readily sort points along the line y=x
class Point:

	def __init__ (self,xVal,yVal):
		#x and y values should never change after creation so that the object can be hashable
		self.x = xVal
		self.y = yVal

	# <=, <, >=, > comparisions based on x**2+y**2 vals
	# =, != based on if the x and y values are the same
	def __lt__(self, other):
		return ((self.x**2 + self.y**2) < (other.x**2 + other.y**2))
	def __le__(self, other):
		return ((self.x**2 + self.y**2) <= (other.x**2 + other.y**2))
	def __gt__(self, other):
		return ((self.x**2 + self.y**2) > (other.x**2 + other.y**2))
	def __ge__(self, other):
		return ((self.x**2 + self.y**2) >= (other.x**2 + other.y**2))
	def __eq__(self, other):
		return ((self.x == other.x) and (self.y == other.y))
	def __hash__(self):
		return hash((self.x, self.y))
	def __repr__(self):
		return "<x:%s y:%s>" % (self.x, self.y)
	def __str__(self):
		return "(%s, %s)" % (self.x, self.y)


#Monte Carlo algorithm wrapper for predicted polygon
class Cluster:
	def __init__ (self, point, size, amount, pickup):
		self.centroid = point
		self.count = int(amount + 0.5)
		self.pickup = pickup
		self.radius = size
		self.trips = []
		self.possibleTrips = []

	def addTrip(self, inputParam=None):
		try:
			trip = 0
			if(inputParam == None):
				trip = random.choice(self.possibleTrips)
				if(self.pickup):
					counterpartApp = trip.end
				else:
					counterpartApp = trip.start
				counterpartApp.addTrip(trip)
			else:
				trip = inputParam
			self.trips.append(trip)

			if(len(self.trips) > self.count):
				itemToDelete = random.choice(self.trips)
				self.trips.remove(itemToDelete) #Don't need to worry about other cluster as it deletes the object itself
		except IndexError:
			pass

	def addPossibleTrip(self, trip):
		if(self.pickup):
			counterpartApp = trip.end.possibleTrips
			counterpartApp.append(trip)
			self.possibleTrips.append(trip)
		else:
			counterpartApp = trip.start.possibleTrips
			counterpartApp.append(trip)
			self.possibleTrips.append(trip)

#Simply stores a series of pickup and dropoff clusters
class Timestep:
	def __init__ (self, pickupPolies, dropoffPolies):
		self.pickupClusters = pickupPolies
		self.dropoffClusters = dropoffPolies

#Trip object used while converging to set of optimal trips
class Trip:
	def __init__ (self, cluster1, cluster2, length):
		self.start = cluster1
		self.end = cluster2
		self.duration = length
	
#Input trips are wrapped into this class as are predicted trips.
class TripRecord:

	def __init__(self, point1, point2, startTime, endTime):
		self.startingPoint = point1
		self.endingPoint = point2
		self.startingTime = startTime
		self.endingTime = endTime
		self.length = (endTime - startTime).total_seconds()/60

	def __lt__(self, other):
		return self.startingPoint < other.startingPoint
	def __le__(self, other):
		return self.startingPoint <= other.startingPoint
	def __gt__(self, other):
		return self.startingPoint > other.startingPoint
	def __ge__(self, other):
		return self.startingPoint >= other.startingPoint