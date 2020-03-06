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

#Graph created according to the style of the powerpoint presentation (dark background)

mpl.rc('font',family='DIN Alternate')
mpl.rcParams.update({'font.size':15})

plt.style.use('dark_background')

xVals = [i + 0.5 for i in range(24)]

BasePath = 'SIMULATORLOGS/BASE_RESULTS/TAXILOG.txt'
AlgoPath = 'SIMULATORLOGS/ALGO_RESULTS/TAXILOG.txt'



BaseCapRates = []
AlgoCapRates = []

AlgoLocFree = 0
AlgoLogUsed = 0

BaseLocFree = 0
BaseLogUsed = 0

date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

#Sum up the vacant and non vacant travel times of the base algorithm's taxis for each hour
with open(BasePath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				BaseCapRates.append(BaseLogUsed/(BaseLogUsed + BaseLocFree))
				BaseLocFree = 0
				BaseLogUsed = 0
				date_time_object += timedelta(minutes=60)
			
			if r[2] == 'True':
				BaseLocFree += float(r[3])
			else:
				BaseLogUsed += float(r[3])

BaseCapRates.append(BaseLogUsed/(BaseLogUsed + BaseLocFree))


date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

#Sum up the vacant and non vacant travel times of the developed algorithm's taxis for each hour
with open(AlgoPath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				AlgoCapRates.append(AlgoLogUsed/(AlgoLogUsed + AlgoLocFree))
				AlgoLocFree = 0
				AlgoLogUsed = 0
				date_time_object += timedelta(minutes=60)
			
			if r[2] == 'True':
				AlgoLocFree += float(r[3])
			else:
				AlgoLogUsed += float(r[3])

AlgoCapRates.append(AlgoLogUsed/(AlgoLogUsed + AlgoLocFree))

df=pd.DataFrame({'x': xVals, 'algoY' : AlgoCapRates, 'baseY' : BaseCapRates})

plt.figure().set_facecolor('#262626')


plt.plot( 'x', 'algoY', data=df, ms=10, mec='#5294e2', mew=2, mfc='#ffffff',   marker = 'o', color='#5294e2',linewidth=5, label="Developed Algorithm")
plt.plot( 'x', 'baseY', data=df, ms=10, mec='#e91d28', mew=2, mfc='#ffffff' , marker='o', color='#e91d28',  linewidth=5, label="Local Greedy Algorithm")

yTicks = [0.1*i for i in range(6)]


plt.legend(facecolor='#262626', fontsize=15)
plt.xticks(np.arange(0, 25, 1), fontsize=18)
plt.yticks(np.array(yTicks), fontsize=18)
axes = plt.gca()

axes.set_ylim([0,0.51])
axes.set_xlim([0,24.001])
axes.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
axes.set_facecolor('#262626')

plt.suptitle('Capacity Utilization Rates Over Simulated Day (March 22, 2019)', fontname='DIN Alternate', fontsize=36)
plt.xlabel('Hour of Day',fontname='DIN Alternate', fontsize=24)
plt.ylabel('Capacity Utilization Rate',fontname='DIN Alternate', fontsize=24)
plt.show()



#Graph created according to the style of the research paper (light background)
'''


mpl.rc('font',family='Helvetica')
mpl.rcParams.update({'font.size':15})


xVals = [i + 0.5 for i in range(24)]

BasePath = 'SIMULATORLOGS/BASE_RESULTS/TAXILOG.txt'
AlgoPath = 'SIMULATORLOGS/ALGO_RESULTS/TAXILOG.txt'



BaseCapRates = []
AlgoCapRates = []

AlgoLocFree = 0
AlgoLogUsed = 0

BaseLocFree = 0
BaseLogUsed = 0

date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

#Sum up the vacant and non vacant travel times of the base algorithm's taxis for each hour
with open(BasePath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				BaseCapRates.append(BaseLogUsed/(BaseLogUsed + BaseLocFree))
				BaseLocFree = 0
				BaseLogUsed = 0
				date_time_object += timedelta(minutes=60)
			
			if r[2] == 'True':
				BaseLocFree += float(r[3])
			else:
				BaseLogUsed += float(r[3])

BaseCapRates.append(BaseLogUsed/(BaseLogUsed + BaseLocFree))


date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

#Sum up the vacant and non vacant travel times of the developed algorithm's taxis for each hour
with open(AlgoPath, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				AlgoCapRates.append(AlgoLogUsed/(AlgoLogUsed + AlgoLocFree))
				AlgoLocFree = 0
				AlgoLogUsed = 0
				date_time_object += timedelta(minutes=60)
			
			if r[2] == 'True':
				AlgoLocFree += float(r[3])
			else:
				AlgoLogUsed += float(r[3])

AlgoCapRates.append(AlgoLogUsed/(AlgoLogUsed + AlgoLocFree))

df=pd.DataFrame({'x': xVals, 'algoY' : AlgoCapRates, 'baseY' : BaseCapRates})

plt.plot( 'x', 'algoY', data=df, ms=10, mec='#5294e2', mew=2, mfc='#ffffff',   marker = 'o',color='#5294e2', linewidth=5, label="Developed Algorithm")
plt.plot( 'x', 'baseY', data=df, ms=10, mec='#e91d28', mew=2, mfc='#ffffff' , marker='o', color='#e91d28',  linewidth=5, label="Local Greedy Algorithm")

yTicks = [0.1*i for i in range(6)]


plt.legend(fontsize=15)
plt.xticks(np.arange(0, 25, 1), fontsize=18)
plt.yticks(np.array(yTicks), fontsize=18)
axes = plt.gca()

axes.set_ylim([0,0.51])
axes.set_xlim([0,24.001])
axes.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.suptitle('Capacity Utilization Rates Over Simulated Day (March 22, 2019)', fontname='Helvetica', fontsize=36)
plt.xlabel('Hour of Day',fontname='Helvetica', fontsize=24)
plt.ylabel('Capacity Utilization Rate',fontname='Helvetica', fontsize=24)
plt.show()
'''

			