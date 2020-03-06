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

#Graph created with a dark background
mpl.rc('font',family='DIN Alternate')
mpl.rcParams.update({'font.size':15})

plt.style.use('dark_background')

xVals = [i + 0.5 for i in range(24)]

path = ''

lessThanFive = []
fiveToTen = []
tenToFifteen = []
notPicked = []

localFive = 0
localTen = 0
localFifteen = 0
localFailure = 0

date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

#For each hour identify how many passenghers were picked up within 5 minutes, 5-10 minutes, 10-15 minutes, or missed
with open(path, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				lessThanFive.append(localFive)
				fiveToTen.append(localTen)
				tenToFifteen.append(localFifteen)
				notPicked.append(localFailure)

				localFive = 0
				localTen = 0
				localFifteen = 0
				localFailure = 0

				date_time_object += timedelta(minutes=60)
			
			if r[2] == 'NOT YET PICKED UP':
				localFailure += 1
			else:
				dropTime = datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S.%f")

				travelTime = (dropTime - deployTime).total_seconds()/60

				if travelTime <= 5:
					localFive += 1
				elif travelTime <= 10:
					localTen += 1
				else:
					localFifteen += 1

lessThanFive.append(localFive)
fiveToTen.append(localTen)
tenToFifteen.append(localFifteen)
notPicked.append(localFailure)

lessThanFive = [i for i in lessThanFive]
fiveToTen = [i for i in fiveToTen]
tenToFifteen = [i for i in tenToFifteen]
notPicked = [i for i in notPicked]


localFive = 0
localTen = 0
localFifteen = 0
localFailure = 0

plt.figure().set_facecolor('#262626')

width=1

p1 = plt.bar(xVals, lessThanFive, width, color='#5294e2')
p2 = plt.bar(xVals, fiveToTen, width, bottom=lessThanFive, color='#e91d28')

bottom = [lessThanFive[i] + fiveToTen[i] for i in range(len(lessThanFive))]

p3 = plt.bar(xVals, tenToFifteen, width, bottom=bottom, color='#219897')

bottom = [lessThanFive[i] + fiveToTen[i] + tenToFifteen[i] for i in range(len(lessThanFive))]

p4 = plt.bar(xVals, notPicked, width, bottom=bottom, color='#FFD700')

plt.ylabel('Number Of Passengers',fontname='DIN Alternate', fontsize=24)
plt.xlabel('Hour of Day',fontname='DIN Alternate', fontsize=24)
plt.suptitle('Developed Algorithm Passenger Wait Times Over Simulated Day (March 22, 2019)', fontname='DIN Alternate', fontsize=24)

plt.xticks(np.arange(0, 25, 1), fontsize=18)
plt.yticks(np.arange(0,20000,2500), fontsize=18)

plt.legend((p1[0], p2[0], p3[0], p4[0]), ('0-5 Minutes Waiting', '5-10 Minutes Waiting', '10-15 Minutes Waiting', '> 15 Minutes (Counted as Not Picked Up)'), facecolor='#262626', fontsize=15)


axes = plt.gca()

axes.set_ylim([-1,18010])
axes.set_xlim([-0.01,24.01])
axes.set_facecolor('#262626')


plt.ylabel('Number Of Passengers',fontname='DIN Alternate', fontsize=24)



plt.show()



#Graph created with a light background
'''
mpl.rc('font',family='Helvetica')
mpl.rcParams.update({'font.size':15})


xVals = [i + 0.5 for i in range(24)]

path = ''

lessThanFive = []
fiveToTen = []
tenToFifteen = []
notPicked = []

localFive = 0
localTen = 0
localFifteen = 0
localFailure = 0

date_time_str = "2019-03-22 01:00:00.000000"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

#For each hour identify how many passenghers were picked up within 5 minutes, 5-10 minutes, 10-15 minutes, or missed
with open(path, 'r') as source:
	rdr = csv.reader(source)
	for r in rdr:
		if(r[1] != 'tpep_dropoff_datetime'):
			deployTime = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f")

			if deployTime > date_time_object:
				lessThanFive.append(localFive)
				fiveToTen.append(localTen)
				tenToFifteen.append(localFifteen)
				notPicked.append(localFailure)

				localFive = 0
				localTen = 0
				localFifteen = 0
				localFailure = 0

				date_time_object += timedelta(minutes=60)
			
			if r[2] == 'NOT YET PICKED UP':
				localFailure += 1
			else:
				dropTime = datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S.%f")

				travelTime = (dropTime - deployTime).total_seconds()/60

				if travelTime <= 5:
					localFive += 1
				elif travelTime <= 10:
					localTen += 1
				else:
					localFifteen += 1

lessThanFive.append(localFive)
fiveToTen.append(localTen)
tenToFifteen.append(localFifteen)
notPicked.append(localFailure)

lessThanFive = [i for i in lessThanFive]
fiveToTen = [i for i in fiveToTen]
tenToFifteen = [i for i in tenToFifteen]
notPicked = [i for i in notPicked]

localFive = 0
localTen = 0
localFifteen = 0
localFailure = 0

width=1

p1 = plt.bar(xVals, lessThanFive, width, color='#5294e2')
p2 = plt.bar(xVals, fiveToTen, width, bottom=lessThanFive, color='#e91d28')

bottom = [lessThanFive[i] + fiveToTen[i] for i in range(len(lessThanFive))]

p3 = plt.bar(xVals, tenToFifteen, width, bottom=bottom, color='#219897')

bottom = [lessThanFive[i] + fiveToTen[i] + tenToFifteen[i] for i in range(len(lessThanFive))]

p4 = plt.bar(xVals, notPicked, width, bottom=bottom, color='#043927')

plt.ylabel('Number Of Passengers',fontname='Helvetica', fontsize=24)
plt.xlabel('Hour of Day',fontname='Helvetica', fontsize=24)
plt.suptitle('Developed Algorithm Passenger Wait Times Over Simulated Day (March 22, 2019)', fontname='Helvetica', fontsize=36)

plt.xticks(np.arange(0, 25, 1), fontsize=20)
plt.yticks(np.arange(0,20000,2500), fontsize=20)

plt.legend((p1[0], p2[0], p3[0], p4[0]), ('0-5 Minutes Waiting', '5-10 Minutes Waiting', '10-15 Minutes Waiting', '> 15 Minutes Waiting (Counted as Not Picked Up)'),  fontsize=18)

axes = plt.gca()
axes.set_ylim([-1,18010])
axes.set_xlim([-0.01,24.01])

plt.ylabel('Number Of Passengers',fontname='Helvetica', fontsize=24)

plt.show()
'''
