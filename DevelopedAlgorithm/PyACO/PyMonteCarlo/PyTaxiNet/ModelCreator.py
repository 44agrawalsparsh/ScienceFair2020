'''
This file was written in a seperate development environment for the Deep Learning algorithm. If required, the file can easily be run again with minor changes to the declared directories.
'''
#This was the workspace where differnet model archetectures were designed

import tensorflow as tf
import os
from tensorflow.keras.models import Sequential, model_from_json, Model
from tensorflow.keras.layers import Dense, LSTM, Flatten, Reshape, Conv2D, ConvLSTM2D, BatchNormalization, Conv3D, LeakyReLU, Input, concatenate, add, Dropout
from tensorflow.keras import metrics
from tensorflow.keras.callbacks import CSVLogger, ModelCheckpoint, TerminateOnNaN, LearningRateScheduler
from tensorflow.keras.optimizers import Adam, RMSprop, SGD
from tensorflow.keras.regularizers import l1,l2
from tensorflow.keras import backend as K
from tensorflow.keras.utils import plot_model
import pydot
import graphviz

FILEPATHTODIAGRAM = ''
FILEPATHTOARCHJSON = ''
FILEPATHTOWEIGHTS = ''
#Generates a keras model object for training. Model has the designed archetecture and loads the latest weights.
def genModel(sampleSize, version, spatialWeight, quantityWeight,lr):

	#Defining the input layers
	pickupSpatialInput = Input(shape=(sampleSize, 300), dtype='float32', name='Pickup_Spatial_Input')
	dropoffSpatialInput = Input(shape=(sampleSize, 300), dtype='float32', name='Dropoff_Spatial_Input')
	pickupQuantityInput = Input(shape=(sampleSize, 1), dtype='float32', name='Pickup_Quantity_Input')
	dropoffQuantityInput = Input(shape=(sampleSize, 1), dtype='float32', name='Dropoff_Quantity_Input')
	#Connecting the LSTM layers before the spatial inputs merge
	lstm_PSI = LSTM(units=150, return_sequences=True)(pickupSpatialInput)
	activationPSI = LeakyReLU()(lstm_PSI)

	lstm_DSI = LSTM(units=150, return_sequences=True)(dropoffSpatialInput)
	activationDSI = LeakyReLU()(lstm_DSI)
	#Add LSTM layers after the quantity inputs
	lstm_PQI = LSTM(units=150, return_sequences=True)(pickupQuantityInput)
	activationPQI = LeakyReLU()(lstm_PQI)

	lstm_DQI = LSTM(units=150, return_sequences=True)(dropoffQuantityInput)
	activationDQI = LeakyReLU()(lstm_DQI)
	#Merge the two spatial layers
	spatialMerge = concatenate([activationPSI, activationDSI])
	#add another LSTM layer afterwards
	lstm_post_merge = LSTM(units=150, return_sequences=True)(spatialMerge)
	activationPostMerge = LeakyReLU()(lstm_post_merge)
	#Merge the quantity with spatial data
	finalMerge = concatenate([activationPostMerge, activationPQI, activationDQI])
	#add an LSTM layer to the merged layers
	layer = LSTM(units=500, return_sequences=True)(finalMerge)
	activation = LeakyReLU()(layer)
	layer = LSTM(units=500, return_sequences=True)(activation)
	activation = LeakyReLU()(layer)
	layer = LSTM(units=500, return_sequences=True)(activation)
	activation = LeakyReLU()(layer)
	#Split the merged layer into three -> lstmPQO, lstmDQO and contined LSTM layers
	lstmPQO = LSTM(units=150, return_sequences=True)(activation)
	activationLSTMPQO = LeakyReLU()(lstmPQO)
	PQOMerge = concatenate([activationLSTMPQO, activationPQI])
	lstmPQO = LSTM(units=10, return_sequences=False)(PQOMerge)
	activationLSTMPQO = LeakyReLU()(lstmPQO)

	lstmDQO = LSTM(units=150, return_sequences=True)(activation)
	activationLSTMDQO = LeakyReLU()(lstmDQO)
	DQOMerge = concatenate([activationLSTMDQO, activationDQI])
	lstmDQO = LSTM(units=10, return_sequences=False)(DQOMerge)
	activationLSTMDQO = LeakyReLU()(lstmDQO)

	lstmSpatial = LSTM(units=150, return_sequences=True)(activation)
	activationSpatialLSTM = LeakyReLU()(lstmSpatial)
	#Output the quantity values
	pickupQuantityOutput = Dense(units=1, name='Pickup_Quantity_Output')(activationLSTMPQO)
	dropoffQuantityOutput = Dense(units=1, name='Dropoff_Quantity_Output')(activationLSTMDQO)
	#Split the merged layer -> lstmPSO, lstmDSO
	PSOMerge = concatenate([lstmSpatial, activationPSI])
	lstmPSO = LSTM(units=150, return_sequences=False)(PSOMerge)
	activationLSTMPSO = LeakyReLU()(lstmPSO)

	DSOMerge = concatenate([lstmSpatial, activationDSI])
	lstmDSO = LSTM(units=150, return_sequences=False)(DSOMerge)
	activationLSTMDSO = LeakyReLU()(lstmDSO)
	#Output the spatial values
	pickupSpatialOutput = Dense(300, name='Pickup_Spatial_Output')(activationLSTMPSO)
	dropoffSpatialOutput = Dense(300, name='Dropoff_Spatial_Output')(activationLSTMDSO)

	TaxiNet = Model(inputs=[pickupSpatialInput, dropoffSpatialInput, pickupQuantityInput, dropoffQuantityInput], outputs=[pickupSpatialOutput, dropoffSpatialOutput, pickupQuantityOutput, dropoffQuantityOutput])


	plot_model(TaxiNet,FILEPATHTODIAGRAM)

	model_json = TaxiNet.to_json()
	with open(FILEPATHTOARCHJSON, "w") as json_file:
		json_file.write(model_json)

	if(os.path.exists(FILEPATHTOWEIGHTS)):
		TaxiNet.load_weights(FILEPATHTOWEIGHTS)
	opt = tf.keras.optimizers.RMSprop(learning_rate=lr)
	TaxiNet.compile(loss={'Pickup_Spatial_Output': 'mse', 'Dropoff_Spatial_Output': 'mse', 'Pickup_Quantity_Output' : 'mse', 'Dropoff_Quantity_Output' : 'mse'}, optimizer=opt, loss_weights={'Pickup_Spatial_Output': spatialWeight, 'Dropoff_Spatial_Output': spatialWeight, 'Pickup_Quantity_Output' : quantityWeight, 'Dropoff_Quantity_Output' : quantityWeight}, metrics = ['mae'])
	return TaxiNet


