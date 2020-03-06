#During the training of the taxi demand prediction model, the following code was used to ensure that all four demand components (pickup quantity, dropoff quantity, pickup distribution, dropoff distribution) had the same data points
FILEPATHTODATA = ''
import os
os.chdir(FILEPATHTODATA)

DQPoints = os.listdir('DropoffQuantity')
DSPoints = os.listdir('DropoffSpatial')
PQPoints = os.listdir('RequestQuantity')
PSPoints = os.listdir('RequestSpatial')


univeralPoints = []

for point in DQPoints:
	if point in DSPoints:
		if point in PQPoints:
			if point in PSPoints:
				univeralPoints.append(point)



print(univeralPoints)
print(len(univeralPoints))
outputCSV = open('listOfPoints.csv', 'w')

for point in univeralPoints:
	outputCSV.write(point + "\n")
outputCSV.close()