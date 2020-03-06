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



VERSION = 1
SAMPLE_SIZE = 24

BATCH_SIZE = 10
EPOCHS = 50

#Switch to correct directory
FILEPATHTODATA = ''

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
#Switch to correct directory
FILEPATHTOSCALERS = ''

#Generates a list of points from a file listing all the datapoints
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

#Further trains a given model with process data
def train(varBatchSize, varEpochs, model, PSIData, DSIData, PQIData, DQIData):
	#Switch to correct directory
	checkpoint = ModelCheckpoint(filepath='' + 'WEIGHTSRound3-{epoch:02d}.hdf5', monitor='loss', verbose=0, save_best_only=True, save_weights_only=False, mode='auto', period=1)
	#Switch to correct directory
	saver = ModelCheckpoint(filepath='' + 'Latest.hdf5', monitor='val_loss', verbose=0, save_best_only=False, save_weights_only=False, mode='auto', period=1)
	#Switch to correct directory
	csvlogger = CSVLogger("")
	terminator = TerminateOnNaN()
	
	reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=1, min_lr=0.0001, verbose=1)

	model.fit(x={'Pickup_Spatial_Input': PSIData[0], 'Dropoff_Spatial_Input': DSIData[0], 'Pickup_Quantity_Input' : PQIData[0], 'Dropoff_Quantity_Input' : DQIData[0]},
			  y = {'Pickup_Spatial_Output': PSIData[1], 'Dropoff_Spatial_Output': DSIData[1], 'Pickup_Quantity_Output' : PQIData[1], 'Dropoff_Quantity_Output' : DQIData[1]},
			  batch_size = varBatchSize, 
			  epochs=varEpochs, 
			  verbose=1,
			  validation_data=({'Pickup_Spatial_Input': PSIData[2], 'Dropoff_Spatial_Input': DSIData[2], 'Pickup_Quantity_Input' : PQIData[2], 'Dropoff_Quantity_Input' : DQIData[2]}, 
			  	{'Pickup_Spatial_Output': PSIData[3], 'Dropoff_Spatial_Output': DSIData[3], 'Pickup_Quantity_Output' : PQIData[3], 'Dropoff_Quantity_Output' : DQIData[3]}), 
		      callbacks=[reduce_lr, terminator, csvlogger, checkpoint, saver], shuffle=False)


#Main method. Processes data and trains the model on it.
def main():
	fileList = dp.fileListCalc(getFiles(FILELISTPATH), PSIFilePath, DSIFilePath)
	PSIScalers, PSIData = dp.processSpatialData(PSIFilePath, SAMPLE_SIZE, fileList)

	PQIScalers, PQIData = dp.processQuantityData(PQIFilePath, SAMPLE_SIZE, fileList)

	DSIScalers, DSIData = dp.processSpatialData(DSIFilePath, SAMPLE_SIZE, fileList)
	DQIScalers, DQIData = dp.processQuantityData(DQIFilePath, SAMPLE_SIZE, fileList)


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
	
	train(BATCH_SIZE, EPOCHS, network, PSIData, DSIData, PQIData, DQIData)

main()





