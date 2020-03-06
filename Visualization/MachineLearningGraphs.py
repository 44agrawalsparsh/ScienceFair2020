import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import pandas as pd

#Graphs created with a dark background
'''
mpl.rc('font',family='DIN Alternate')


mpl.rcParams.update({'font.size':15})

plt.style.use('dark_background')

x = [(datetime.datetime(1,1,1) + datetime.timedelta(minutes=15*i)).time() for i in range(1,49)]

trainedYRaw = [] #Add the trained model's results

persistYRaw = [] #Add the persistence model's results

cycleYRaw = [0 for i in range(48)] #Add the cyclical model's results

baseValue = persistYRaw[0]

trainedY = [i/baseValue*100 for i in trainedYRaw]
persistY = [i/baseValue*100 for i in persistYRaw]
cycleY = [i/baseValue*100 for i in cycleYRaw]



benchmark = [persistY[0] for i in range(48)]

df=pd.DataFrame({'x': x, 'trained': trainedY, 'persist': persistY, 'cycle': cycleY, 'benchmark' : benchmark})
plt.figure().set_facecolor('#262626')
plt.plot( 'x', 'trained', data=df, color='#5294e2', linewidth=3, label="Trained Model")
plt.plot( 'x', 'persist', data=df, color='#e91d28', linewidth=3, label="Persistence Model")
plt.plot( 'x', 'cycle', data=df, color='#219897', linewidth=3, label="Cyclical Model")
plt.plot( 'x', 'benchmark', data=df, marker='', linestyle='dashed', color='white', linewidth=2, label="Persistence Error For Predicting One Timestep (15 minutes)")
plt.legend(facecolor='#262626', fontsize=15)
plt.xticks(np.arange(60*60, 60*60*12+1, 60*60), fontsize=18)
plt.yticks(fontsize=18)
axes = plt.gca()
axes.set_ylim([0,6500])
axes.set_xlim([15*60,60*60*12])
axes.invert_yaxis()
axes.set_facecolor('#262626')


plt.suptitle('Pickup Quantity Prediction Errors Over Time', fontname='DIN Alternate', fontsize=36)
plt.xlabel('Hours Ahead Predicted',fontname='DIN Alternate', fontsize=24)
plt.ylabel('Scaled Mean Squared Errors (100 = Persistence Model t+15 min)',fontname='DIN Alternate', fontsize=20)
plt.show()
'''

#Graphs created with a light background
mpl.rc('font',family='Helvetica')


mpl.rcParams.update({'font.size':15})

x = [(datetime.datetime(1,1,1) + datetime.timedelta(minutes=15*i)).time() for i in range(1,49)]


trainedYRaw = [] #Add the trained model results

persistYRaw = [] #Add the persistence model results

cycleYRaw = [0 for i in range(48)] #Add the cycle model result

baseValue = persistYRaw[0]

trainedY = [i/baseValue*100 for i in trainedYRaw]
persistY = [i/baseValue*100 for i in persistYRaw]
cycleY = [i/baseValue*100 for i in cycleYRaw]

benchmark = [persistY[0] for i in range(48)]

df=pd.DataFrame({'x': x, 'trained': trainedY, 'persist': persistY, 'cycle': cycleY, 'benchmark' : benchmark})
 
plt.plot( 'x', 'trained', data=df, color='#5294e2', linewidth=3, label="Trained Model")
plt.plot( 'x', 'persist', data=df, color='#e91d28', linewidth=3, label="Persistence Model")
plt.plot( 'x', 'cycle', data=df, color='#219897', linewidth=3, label="Cyclical Model")
plt.plot( 'x', 'benchmark', data=df, marker='', linestyle='dashed', color='black', linewidth=2, label="Persistence Error For Predicting One Timestep (15 minutes)")
plt.legend(fontsize=15)
plt.xticks(np.arange(60*60, 60*60*12+1, 60*60), fontsize=18)
plt.yticks(fontsize=18)
axes = plt.gca()
axes.set_ylim([0,6500])
axes.set_xlim([15*60,60*60*12])
axes.invert_yaxis()


plt.suptitle('Dropoff Quantity Prediction Errors Over Time', fontname='Helvetica', fontsize=36)
plt.xlabel('Hours Ahead Predicted',fontname='Helvetica', fontsize=24)
plt.ylabel('Scaled Mean Squared Errors (100 = Persistence Model t+15 min)',fontname='Helvetica', fontsize=20)
plt.show()
