import os
import numpy as np
from sklearn import preprocessing
import pandas as pd 

'''Used to seperate the file input, which is arranged as

x, y, r
x, y, r
x, y, r
...

,into 3 lists.
'''
def seperate(originalArr):
	rotated = list(zip(*originalArr[::-1]))
	xCoord = list(rotated[0])[::-1]
	yCoord = list(rotated[1])[::-1]
	radius = list(rotated[2])[::-1]


	return xCoord, yCoord, radius

#Take 3 lists (x-coord values, y-coord values, and the radius sizes) and flatten them into a 1d list
def mergeData(x,y,r):
	output = []
	for i in range(0,len(x)):
		currentData = []
		for j in range(0,len(x[i])):
			dataPiece = [x[i][j], y[i][j], r[i][j]]

			currentData.extend(dataPiece)
		output.append(currentData)
	return(output)

#Generate X and Y samples from a series of data points
def genData(rawData, sampleSize):
	numData = len(rawData)
	dataX = []
	dataY = []
	for i in range(0,numData - sampleSize - 1):
		sampleX = rawData[i:i+sampleSize]
		sampleY = rawData[i+sampleSize+1]

		dataX.append(sampleX)
		dataY.append(sampleY)

	return dataX, dataY

#Just generate the X samples to predict an unknown value
def genDataPrediction(rawData, sampleSize):
	numData = len(rawData)
	dataX = []
	for i in range(0,numData - sampleSize):
		sampleX = rawData[i:i+sampleSize]
		dataX.append(sampleX)

	return dataX[-1:]

#Filter out corrupt samples from within a list of filenames
def fileListCalc(fileList, PSD, DSD):

	fileListPSD = []
	fileListDSD = []
	
	finalFileList = []
	for fileName in fileList:
		try:
			var = pd.read_csv(PSD + '/' + fileName)
			var = var.to_numpy()
			var = var.tolist()
			

			if(len(var) >= 99):
				fileListPSD.append(fileName)
		except:
			pass
	for fileName in fileList:
		try:
			var = pd.read_csv(DSD + '/' + fileName)
			var = var.to_numpy()
			var = var.tolist()
			

			if(len(var) >= 99):
				fileListDSD.append(fileName)

		except:
			pass

	for fileName in fileListPSD:
		if fileName in fileListDSD:
			finalFileList.append(fileName)

	return finalFileList	


#Used to create all the neccessary data pieces during training the model for distribution data
def processSpatialData(directory, sampleSize,fileList, partition=0.9):
	xCoords = []
	yCoords = []
	radiuses = []

	
	c = 0
	n = 0
	dtypes = ['float', 'float', 'float']

	xMean = []
	yMean = []
	rMean = []
	for fileName in fileList:
		var = pd.read_csv(directory + '/' + fileName)
		var = var.to_numpy()
		var = var.tolist()
		

		if(len(var) == 100):
			xCoord, yCoord, radius = seperate(var)

			xCoord = [x - spatialXMean() for x in xCoord]
			yCoord = [y - spatailYMean() for y in yCoord]
			radius = [r - spatialRadiusMean() for r in radius]
			xCoords.append(xCoord)
			yCoords.append(yCoord)
			radiuses.append(radius)

		elif(len(var) == 99):
			xCoord, yCoord, radius = seperate(var)
			
			xCoord.append(0)
			yCoord.append(0)
			radius.append(0)

			xCoord = [x - spatialXMean() for x in xCoord]
			yCoord = [y - spatailYMean() for y in yCoord]
			radius = [r - spatialRadiusMean() for r in radius]

			xCoords.append(xCoord)
			yCoords.append(yCoord)
			radiuses.append(radius)

	trainXCoord = xCoords[:int(len(xCoords)*partition)]
	trainYCoord = yCoords[:int(len(yCoords)*partition)]
	trainRadius = radiuses[:int(len(radiuses)*partition)]

	valXCoord = xCoords[int(len(xCoords)*partition):]
	valYCoord = yCoords[int(len(yCoords)*partition):]
	valRadius = radiuses[int(len(radiuses)*partition):]

	xScaler = preprocessing.MinMaxScaler().fit(trainXCoord)
	yScaler = preprocessing.MinMaxScaler().fit(trainYCoord)
	rScaler = preprocessing.MinMaxScaler().fit(trainRadius)

	trainXCoord = xScaler.transform(trainXCoord)
	trainYCoord = yScaler.transform(trainYCoord)
	trainRadius = rScaler.transform(trainRadius)

	valXCoord = xScaler.transform(valXCoord)
	valYCoord = yScaler.transform(valYCoord)
	valRadius = rScaler.transform(valRadius)

	trainData = mergeData(trainXCoord,trainYCoord, trainRadius)
	valData = mergeData(valXCoord, valYCoord, valRadius)

	trainX, trainY = genData(trainData, sampleSize)
	valX, valY = genData(valData, sampleSize)

	trainX = np.array(trainX)
	trainY = np.array(trainY)

	valX = np.array(valX)
	valY = np.array(valY)

	scalers = [xScaler, yScaler, rScaler]
	data = [trainX, trainY, valX, valY]

	return scalers, data

#Used to create all the neccessary data pieces during training the model for quantity data
def processQuantityData(directory, sampleSize,fileList, partition=0.9):
	data = []
	
	sum = 0
	for fileName in fileList:
		dataFile = open(directory + "/" + fileName,"r")
		var = [float(dataFile.read()) - quantityMean()]
		dataFile.close()
		data.append(var)

	trainQuantity = data[:int(len(data)*partition)]
	
	valQuantity = data[int(len(data)*partition):]

	scaler = preprocessing.MinMaxScaler().fit(trainQuantity)

	
	trainQuantity = scaler.transform(trainQuantity)

	valQuantity = scaler.transform(valQuantity)

	
	trainX, trainY = genData(trainQuantity, sampleSize)
	valX, valY = genData(valQuantity, sampleSize)
	trainX = np.array(trainX)
	trainY = np.array(trainY)

	valX = np.array(valX)
	valY = np.array(valY)

	
	data = [trainX, trainY, valX, valY]
	scalers = [scaler]

	return scalers, data
		
#Used to create all the neccessary data pieces to predict distribution data
def processSpatialDataWithScalers(directory, sampleSize,fileList, scalers):
	xCoords = []
	yCoords = []
	radiuses = []
	
	c = 0
	n = 0
	dtypes = ['float', 'float', 'float']

	xMean = []
	yMean = []
	rMean = []
	for fileName in fileList:
		var = pd.read_csv(directory + '/' + fileName)
		var = var.to_numpy()
		var = var.tolist()
		

		if(len(var) == 100):
			xCoord, yCoord, radius = seperate(var)
			xCoords.append(xCoord)
			yCoords.append(yCoord)
			radiuses.append(radius)

		elif(len(var) == 99):
			xCoord, yCoord, radius = seperate(var)
			
			xCoord.append(0)
			yCoord.append(0)
			radius.append(0)


			xCoords.append(xCoord)
			yCoords.append(yCoord)
			radiuses.append(radius)

	xScaler = scalers[0]
	yScaler = scalers[1]
	rScaler = scalers[2]

	

	xCoords = xScaler.transform(xCoords)
	yCoords = yScaler.transform(yCoords)
	radiuses = rScaler.transform(radiuses)

	data = mergeData(xCoords, yCoords, radiuses)

	data = genDataPrediction(data, sampleSize)

	data = np.array(data)
	return data

#Used to create all the neccessary data pieces to predict quanity data
def processQuantityDataWithScalers(directory, sampleSize,fileList, scaler):
	data = []
	for fileName in fileList:
		dataFile = open(directory + "/" + fileName,"r")
		var = [float(dataFile.read())]
		dataFile.close()
		data.append(var)
	data = scaler.transform(data)
	data = genDataPrediction(data, sampleSize)
	data = np.array(data)
	return data





