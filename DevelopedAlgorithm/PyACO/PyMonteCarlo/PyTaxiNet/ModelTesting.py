'''
This file was written in a seperate development environment for the Deep Learning algorithm. If required, the file can easily be run again with minor changes to the declared directories.
'''
import DataProcessor as dp
import ModelCreator as mc

import tensorflow as tf
from tensorflow.keras.models import model_from_json, Model
from tensorflow.keras import metrics
from tensorflow.keras.callbacks import CSVLogger, ModelCheckpoint, TerminateOnNaN, LearningRateScheduler, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam, RMSprop, SGD

import numpy as np
import statistics
import joblib


#Switch to correct directory
FILEPATHTODATA = ''

#Switch to correct directory
FILEPATHTOSCALERS = ''

PSIFilePath = FILEPATHTODATA + 'RequestSpatial'
PQIFilePath = FILEPATHTODATA + 'RequestQuantity'
DSIFilePath = FILEPATHTODATA + 'DropoffSpatial'
DQIFilePath = FILEPATHTODATA + 'DropoffQuantity'

PSIScalers = []
PSIData = []

PQIScalers = []
PQIData = []

DSIScalers = []
DSIData = []

DQIScalers = []
DQIData = []

#Switch to correct directory
FILELISTPATH = ''

VERSION = 1
SAMPLE_SIZE = 24

BATCH_SIZE = 10
EPOCHS = 50

PREDICTION_TESTS = 48

#Loads a list of points that are in the testing dataset
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

#Preporcess all the data points
def processData():
	global PSIScalers
	global PSIData
	global PQIScalers
	global DSIScalers
	global DSIData
	global DQIScalers
	global DQIData

	fileList = dp.fileListCalc(getFiles(FILELISTPATH), PSIFilePath, DSIFilePath)
	PSIScalers, PSIData = dp.processSpatialData(PSIFilePath, SAMPLE_SIZE, fileList, 0.01)
	PQIScalers, PQIData = dp.processQuantityData(PQIFilePath, SAMPLE_SIZE, fileList, 0.01)

	DSIScalers, DSIData = dp.processSpatialData(DSIFilePath, SAMPLE_SIZE, fileList, 0.01)
	DQIScalers, DQIData = dp.processQuantityData(DQIFilePath, SAMPLE_SIZE, fileList, 0.01)

#Prints out the results of all three models for all four different prediction components
def TestResults():
	global PSIScalers
	global PSIData
	global PQIScalers
	global DSIScalers
	global DSIData
	global DQIScalers
	global DQIData

	processData()


	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "PSXScaler.save"
	joblib.dump(PSIScalers[0], scaler_filename) 
	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "PSYScaler.save"
	joblib.dump(PSIScalers[1], scaler_filename) 
	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "PSRScaler.save"
	joblib.dump(PSIScalers[2], scaler_filename) 
	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "DSXScaler.save"
	joblib.dump(DSIScalers[0], scaler_filename) 
	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "DSYScaler.save"
	joblib.dump(DSIScalers[1], scaler_filename) 
	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "DSRScaler.save"
	joblib.dump(DSIScalers[2], scaler_filename)
	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "PQScaler.save"
	joblib.dump(PQIScalers[0], scaler_filename) 
	#Switch to correct directory
	scaler_filename = FILEPATHTOSCALERS + "DQScaler.save"
	joblib.dump(DQIScalers[0], scaler_filename) 



	network = mc.genModel(SAMPLE_SIZE,VERSION, 0.40,0.10,0.001)

	print(network.evaluate(x={'Pickup_Spatial_Input': PSIData[2], 'Dropoff_Spatial_Input': DSIData[2], 'Pickup_Quantity_Input' : PQIData[2], 'Dropoff_Quantity_Input' : DQIData[2]}, y = {'Pickup_Spatial_Output': PSIData[3], 'Dropoff_Spatial_Output': DSIData[3], 'Pickup_Quantity_Output' : PQIData[3], 'Dropoff_Quantity_Output' : DQIData[3]}, verbose=1))
	
	
	xVals = [PSIData[2], DSIData[2], PQIData[2], DQIData[2]]
	yVals = [PSIData[3], DSIData[3], PQIData[3], DQIData[3]]

	PSMEVals = []
	DSMEVals = []
	PQMEVals = []
	DQMEVals = []


	i = 0
	while i < (len(xVals[0]) - PREDICTION_TESTS - 1):

		predictX, predictY = createSample(i, xVals, yVals)
		losses = predictSamples(i, predictX, predictY, network)

		PSMEVals.append(losses[0])
		DSMEVals.append(losses[1])
		PQMEVals.append(losses[2])
		DQMEVals.append(losses[3])

		i += 19 #Factor of 95 (96 - 1). Otherwise it will take far too long to test

	
	averageLossesPSME = np.array(PSMEVals).mean(axis=0)
	averageLossesDSME = np.array(DSMEVals).mean(axis=0)
	averageLossesPQME = np.array(PQMEVals).mean(axis=0)
	averageLossesDQME = np.array(DQMEVals).mean(axis=0)


	for j in range(10):
		print()

	print("Trained Model Results")
	print()
	print()
	print()
	print('PSME')
	print(averageLossesPSME)
	print()
	print()
	print('DSME')

	print(averageLossesDSME)
	print()
	print()
	print('PQME')

	print(averageLossesPQME)
	print()
	print()
	print('DQME')

	print(averageLossesDQME)
	print()
	print()
	print()
	

	#Persistence Model

	persistAvgLossesPSME = []
	persistAvgLossesDSME = []
	persistAvgLossesPQME = []
	persistAvgLossesDQME = []

	for i in range(1, PREDICTION_TESTS + 1):
		PSME, DSME = SmseP(yVals[0], yVals[1], i)
		PQME, DQME = QmseP(yVals[2], yVals[3], i)

		persistAvgLossesPSME.append(PSME)
		persistAvgLossesDSME.append(DSME)

		persistAvgLossesPQME.append(PQME)
		persistAvgLossesDQME.append(DQME)

	print("Persistence Model Results")
	print()
	print()
	print()
	print('PSME')
	print(persistAvgLossesPSME)
	print()
	print()
	print('DSME')

	print(persistAvgLossesDSME)
	print()
	print()
	print('PQME')

	print(persistAvgLossesPQME)
	print()
	print()
	print('DQME')

	print(persistAvgLossesDQME)
	print()
	print()
	print()

	#Cycle Scores

	PSME, DSME = SmseC(yVals[0], yVals[1])
	PQME, DQME = QmseC(yVals[2], yVals[3])

	print("Cycle Model Results")
	print()
	print()
	print()
	print('PSME')
	print(PSME)
	print()
	print()
	print('DSME')

	print(DSME)
	print()
	print()
	print('PQME')

	print(PQME)
	print()
	print()
	print('DQME')

	print(DQME)
	print()
	print()
	print()

	exit()

#Generates initial x sample and all the y samples for a specified window for a particular data point
def createSample(index, xVals, yVals):
	initialX = [[xVals[0][index]], [xVals[1][index]], [xVals[2][index]], [xVals[3][index]]]
	testYVals = [[yVals[0][index:index+PREDICTION_TESTS]], [yVals[1][index:index+PREDICTION_TESTS]], [yVals[2][index:index+PREDICTION_TESTS]], [yVals[3][index:index+PREDICTION_TESTS]]]

	return initialX, testYVals

#Predicts for the specified window with the intial x samples and list of y samples as an input. Returns the MSE for the predictions over the window
def predictSamples(index, sampleX, sampleY, model):
	x = sampleX
	PSMSE = []
	DSMSE = []
	PQMSE = []
	DQMSE = []
	for i in range(PREDICTION_TESTS):
		predictedY = model.predict(x, batch_size=1)

		msePS = ((predictedY[0][0] - sampleY[0][0][i])**2).mean(axis=None)
		mseDS = ((predictedY[1][0] - sampleY[1][0][i])**2).mean(axis=None) 
		msePQ = ((predictedY[2][0] - sampleY[2][0][i])**2).mean(axis=None)  
		mseDQ = ((predictedY[3][0] - sampleY[3][0][i])**2).mean(axis=None)   

		

		
		nextPSX = np.array([np.concatenate([x[0][0][1:], [predictedY[0][0]]]).tolist()])
		nextDSX = np.array([np.concatenate([x[1][0][1:], [predictedY[1][0]]]).tolist()])
		nextPQX = np.array([np.concatenate([x[2][0][1:], [predictedY[2][0]]]).tolist()])
		nextDQX = np.array([np.concatenate([x[3][0][1:], [predictedY[3][0]]]).tolist()])

		x = [nextPSX, nextDSX, nextPQX, nextDQX]
		
		PSMSE.append(msePS)
		DSMSE.append(mseDS) 
		PQMSE.append(msePQ) 
		DQMSE.append(mseDQ) 
	output = [PSMSE, DSMSE, PQMSE, DQMSE] 
	return output 

#Persistence model for spatial demand prediction. Returns the MSE for the model's predictions depending for a given prediction window.
def SmseP(PSIData, DSIData, lag):
	outputPSI = 0
	outputDSI = 0

	PSIMSE = []
	DSIMSE = []

	for i in range(len(PSIData) - lag - 1):

		sampleOne = PSIData[i]
		sampleTwo = PSIData[i+lag]

		msePSI = ((sampleOne - sampleTwo)**2).mean(axis=None)


		sampleOne = DSIData[i]
		sampleTwo = DSIData[i+lag]

		mseDSI = ((sampleOne - sampleTwo)**2).mean(axis=None)

		PSIMSE.append(msePSI)
		DSIMSE.append(mseDSI)

	return (sum(PSIMSE)/len(PSIMSE)), (sum(DSIMSE)/len(DSIMSE))

#Persistence model for quantity demand prediction. Returns the MSE for the model's predictions depending for a given prediction window.
def QmseP(PQIData, DQIData, lag):
	outputPQI = 0
	outputDQI = 0

	PQIMSE = []
	DQIMSE = []

	for i in range(len(PQIData) - lag - 1):

		sampleOne = PQIData[i]
		sampleTwo = PQIData[i+lag]

		msePQI = ((sampleOne - sampleTwo)**2).mean(axis=None)


		sampleOne = DQIData[i]
		sampleTwo = DQIData[i+lag]

		mseDQI = ((sampleOne - sampleTwo)**2).mean(axis=None)

		PQIMSE.append(msePQI)
		DQIMSE.append(mseDQI)

	return (sum(PQIMSE)/len(PQIMSE)), (sum(DQIMSE)/len(DQIMSE))


#Cyclical model for spatial demand prediction. Returns the MSE for the model's predictions.
def SmseC(PSIData, DSIData):
	outputPSI = 0
	outputDSI = 0

	PSIMSE = []
	DSIMSE = []

	for i in range(len(PSIData) - 96 - 1):

		sampleOne = PSIData[i]
		sampleTwo = PSIData[i+96]

		msePSI = ((sampleOne - sampleTwo)**2).mean(axis=None)


		sampleOne = DSIData[i]
		sampleTwo = DSIData[i+96]

		mseDSI = ((sampleOne - sampleTwo)**2).mean(axis=None)

		PSIMSE.append(msePSI)
		DSIMSE.append(mseDSI)

	return (sum(PSIMSE)/len(PSIMSE)), (sum(DSIMSE)/len(DSIMSE))

#Cyclical model for quantity demand prediction. Returns the MSE for the model's predictions.
def QmseC(PQIData, DQIData):
	outputPQI = 0
	outputDQI = 0

	PQIMSE = []
	DQIMSE = []

	for i in range(len(PQIData) - 96 - 1):

		sampleOne = PQIData[i]
		sampleTwo = PQIData[i+96]

		msePQI = ((sampleOne - sampleTwo)**2).mean(axis=None)


		sampleOne = DQIData[i]
		sampleTwo = DQIData[i+96]

		mseDQI = ((sampleOne - sampleTwo)**2).mean(axis=None)

		PQIMSE.append(msePQI)
		DQIMSE.append(mseDQI)

	return (sum(PQIMSE)/len(PQIMSE)), (sum(DQIMSE)/len(DQIMSE))





TestResults()
exit()
