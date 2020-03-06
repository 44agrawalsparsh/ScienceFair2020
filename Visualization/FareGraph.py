import csv
import operator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

'''
mpl.rc('font',family='DIN Alternate')
mpl.rcParams.update({'font.size':15})

plt.style.use('dark_background')

xVals = range(25)

BasePath = 'SIMULATORLOGS/BASE_RESULTS/PASSENGERLOG.txt'
AlgoPath = 'SIMULATORLOGS/ALGO_RESULTS/PASSENGERLOG.txt'

BaseFaresCollected = [0]
AlgoFaresCollected = [0]

baseFare = 0
algoFare = 0



date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

with open(BasePath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				BaseFaresCollected.append(baseFare)
				date_time_object += timedelta(minutes=60)
			
			if r[2] != 'NOT YET PICKED UP':
				baseFare += float(r[3])
BaseFaresCollected.append(baseFare)

date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

with open(AlgoPath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				AlgoFaresCollected.append(algoFare)
				date_time_object += timedelta(minutes=60)
			
			if r[2] != 'NOT YET PICKED UP':
				algoFare += float(r[3])
AlgoFaresCollected.append(algoFare)


AlgoFaresCollected = [i/1000 for i in AlgoFaresCollected]
BaseFaresCollected = [i/1000 for i in BaseFaresCollected]

df=pd.DataFrame({'x': xVals, 'algoY' : AlgoFaresCollected, 'baseY' : BaseFaresCollected})

plt.figure().set_facecolor('#262626')


plt.plot( 'x', 'algoY', data=df, ms=10, mec='#5294e2', mew=2, mfc='#ffffff',   marker = 'o',color='#5294e2', linewidth=5, label="Developed Algorithm")
plt.plot( 'x', 'baseY', data=df, ms=10, mec='#e91d28', mew=2, mfc='#ffffff' , marker='o',  color='#e91d28', linewidth=5, label="Local Greedy Algorithm")





fmt = '${x:,.0f}K'
tick = mtick.StrMethodFormatter(fmt)

plt.legend(facecolor='#262626', fontsize=15)
plt.xticks(np.arange(0, 25, 1), fontsize=18)
plt.yticks(np.arange(0,3751,500), fontsize=18)
axes = plt.gca()

axes.set_ylim([-10,3760])
axes.yaxis.set_major_formatter(tick)
axes.set_xlim([-0.1,24.1])
axes.set_facecolor('#262626')

plt.suptitle('Fleet Fares Collected Over Simulated Day (March 22, 2019)', fontname='DIN Alternate', fontsize=36)
plt.xlabel('Hour of Day',fontname='DIN Alternate', fontsize=24)
plt.ylabel('Fleet Fares Collected',fontname='DIN Alternate', fontsize=24)



plt.show()

'''

mpl.rc('font',family='Helvetica')
mpl.rcParams.update({'font.size':15})


xVals = range(25)

BasePath = 'SIMULATORLOGS/BASE_RESULTS/PASSENGERLOG.txt'
AlgoPath = 'SIMULATORLOGS/ALGO_RESULTS/PASSENGERLOG.txt'

BaseFaresCollected = [0]
AlgoFaresCollected = [0]

baseFare = 0
algoFare = 0



date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

with open(BasePath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				BaseFaresCollected.append(baseFare)
				date_time_object += timedelta(minutes=60)
			
			if r[2] != 'NOT YET PICKED UP':
				baseFare += float(r[3])
BaseFaresCollected.append(baseFare)

date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

with open(AlgoPath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				AlgoFaresCollected.append(algoFare)
				date_time_object += timedelta(minutes=60)
			
			if r[2] != 'NOT YET PICKED UP':
				algoFare += float(r[3])
AlgoFaresCollected.append(algoFare)


AlgoFaresCollected = [i/1000 for i in AlgoFaresCollected]
BaseFaresCollected = [i/1000 for i in BaseFaresCollected]

df=pd.DataFrame({'x': xVals, 'algoY' : AlgoFaresCollected, 'baseY' : BaseFaresCollected})



plt.plot( 'x', 'algoY', data=df, ms=10, mec='#5294e2', mew=2, mfc='#ffffff',   marker = 'o',color='#5294e2',linewidth=5, label="Developed Algorithm")
plt.plot( 'x', 'baseY', data=df, ms=10,mec='#e91d28',  mew=2, mfc='#ffffff' , marker='o', color='#e91d28',   linewidth=5, label="Local Greedy Algorithm")





fmt = '${x:,.0f}K'
tick = mtick.StrMethodFormatter(fmt)

plt.legend(fontsize=15)
plt.xticks(np.arange(0, 25, 1), fontsize=18)
plt.yticks(np.arange(0,3751,500), fontsize=18)
axes = plt.gca()

axes.set_ylim([-10,3760])
axes.yaxis.set_major_formatter(tick)
axes.set_xlim([-0.1,24.1])
plt.suptitle('Fleet Fares Collected Over Simulated Day (March 22, 2019)', fontname='Helvetica', fontsize=36)
plt.xlabel('Hour of Day',fontname='Helvetica', fontsize=24)
plt.ylabel('Fleet Fares Collected',fontname='Helvetica', fontsize=24)



plt.show()