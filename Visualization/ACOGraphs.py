import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import pandas as pd
import os
from pandas.plotting import register_matplotlib_converters
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

#Plots for PPT style
'''
register_matplotlib_converters()

mpl.rc('font',family='DIN Alternate')
mpl.rcParams.update({'font.size':15})

plt.style.use('dark_background')


listOfFiles = os.listdir('ACOResults')
listOfFiles = listOfFiles[1:]

xVals = []
yVals = []

for name in listOfFiles:
	filepath = 'ACOResults/' + name
	BASE = 0
	latest = -1
	with open(filepath) as input_file:
		for i,line in enumerate(input_file):
			if i == 0:
				pass
			elif i == 1:
				BASE = float(line)
			else:
				#Only store the points where a better path is formed to represent how long it takes to find better solutions over time and the improvement levels of the new solutions.
				vals = line.split(',')
				xVal = datetime.datetime.strptime('0' + vals[0], '%H:%M:%S.%f')
				xVal = (xVal.hour*3600 + xVal.minute*60 + xVal.second)/60
				yVal = float(vals[1])/BASE*100

				if(abs(yVal - latest) > 0.1):
					xVals.append(xVal)
					yVals.append(yVal)
					latest = yVal


#Generate the line of fit
lineOfBestFitVals = np.polyfit(xVals, yVals, 3)
#Convert and x value to the line of best fit value
def convertToLineOfBestFit(xVal):
	runVal = 0

	for i in range(len(lineOfBestFitVals)):
		runVal += lineOfBestFitVals[-1*(i+1)]*xVal**(i)
	return runVal
#Take a list of coeffecients and generate a string with the equation written in
def genEquation(coefficients):
	output = ''
	for i in range(len(coefficients)):
		if i != 0:
			output =   "{:10.4f}".format(coefficients[-1*(i+1)])[1:] + 'x^' + str(i) + ' +' + output
		else:
			output = "{:10.4f}".format(coefficients[-1*(i+1)]) + 'x^' + str(i)

	return output


sortX = sorted(xVals)

sortX[0] = 0

sortX[-1] = 70

bestY = [convertToLineOfBestFit(i) for i in sortX]

benchmark = [100 for i in range(len(sortX))]


df=pd.DataFrame({'x': xVals, 'sortX' : sortX, 'yVals' : yVals, 'benchmark' : benchmark, 'best' : bestY})

plt.figure().set_facecolor('#262626')

equation = genEquation(lineOfBestFitVals)

plt.scatter( 'x', 'yVals', data=df, color='#5294e2', linewidth=3, label="ACO Optimization Points")
plt.plot( 'sortX', 'benchmark', data=df, marker='', linestyle='dashed', color='white', linewidth=2, label="Local Greedy Algorithm")
plt.plot( 'sortX', 'best', data=df, marker='',  color='#e91d28', linewidth=5, label="Line Of Best Fit")
plt.legend(facecolor='#262626', fontsize=15)
plt.xticks(np.arange(0, 65, 5), fontsize=18)
plt.yticks(np.arange(50, 160, 10), fontsize=18)
plt.text(0.2, 51, 'Line Of Best Fit:' + equation)
axes = plt.gca()

axes.set_ylim([50,150])
axes.set_xlim([0,61])
axes.set_facecolor('#262626')

plt.suptitle('Dispatch Route Length Found Over Time', fontname='DIN Alternate', fontsize=36)
plt.xlabel('Minutes In Computational Time',fontname='DIN Alternate', fontsize=24)
plt.ylabel('Route Length (100 = Greedy Algorithm Length)',fontname='DIN Alternate', fontsize=24)
plt.show()

'''
#Plots for project report style
register_matplotlib_converters()

mpl.rc('font',family='Helvetica')
mpl.rcParams.update({'font.size':15})



listOfFiles = os.listdir('ACOResults')
listOfFiles = listOfFiles[1:]

xVals = []
yVals = []


for name in listOfFiles:
	filepath = 'ACOResults/' + name
	BASE = 0
	latest = -1
	with open(filepath) as input_file:
		for i,line in enumerate(input_file):
			if i == 0:
				pass
			elif i == 1:
				BASE = float(line)
			else:
				vals = line.split(',')
				xVal = datetime.datetime.strptime('0' + vals[0], '%H:%M:%S.%f')
				xVal = (xVal.hour*3600 + xVal.minute*60 + xVal.second)/60
				yVal = float(vals[1])/BASE*100
				#Only store the points where a better path is formed to represent how long it takes to find better solutions over time and the improvement levels of the new solutions.
				if(abs(yVal - latest) > 0.1):
					xVals.append(xVal)
					yVals.append(yVal)
					latest = yVal


#Generate the line of fit
lineOfBestFitVals = np.polyfit(xVals, yVals, 3)

#Convert and x value to the line of best fit value
def convertToLineOfBestFit(xVal):
	runVal = 0

	for i in range(len(lineOfBestFitVals)):
		runVal += lineOfBestFitVals[-1*(i+1)]*xVal**(i)
	return runVal

#Take a list of coeffecients and generate a string with the equation written in
def genEquation(coefficients):
	output = ''
	for i in range(len(coefficients)):
		if i != 0:
			output =   "{:10.4f}".format(coefficients[-1*(i+1)])[1:] + 'x^' + str(i) + ' +' + output
		else:
			output = "{:10.4f}".format(coefficients[-1*(i+1)]) + 'x^' + str(i)

	return output


#Generate actual graph using data
sortX = sorted(xVals)

sortX[0] = 0

sortX[-1] = 70

bestY = [convertToLineOfBestFit(i) for i in sortX]

benchmark = [100 for i in range(len(sortX))]


df=pd.DataFrame({'x': xVals, 'sortX' : sortX, 'yVals' : yVals, 'benchmark' : benchmark, 'best' : bestY})


equation = genEquation(lineOfBestFitVals)

plt.scatter( 'x', 'yVals', data=df, color='#5294e2', linewidth=3, label="ACO Optimization Points")
plt.plot( 'sortX', 'benchmark', data=df, marker='', linestyle='dashed', color='black', linewidth=2, label="Local Greedy Algorithm")
plt.plot( 'sortX', 'best', data=df, marker='',  color='#e91d28', linewidth=5, label="Line Of Best Fit")
plt.legend(fontsize=15)
plt.xticks(np.arange(0, 65, 5), fontsize=18)
plt.yticks(np.arange(50, 160, 10), fontsize=18)
plt.text(0.2, 51, 'Line Of Best Fit:' + equation)
axes = plt.gca()

axes.set_ylim([50,150])
axes.set_xlim([0,61])

plt.suptitle('Dispatch Route Length Found Over Time', fontname='Helvetica', fontsize=36)
plt.xlabel('Minutes In Computational Time',fontname='Helvetica', fontsize=24)
plt.ylabel('Route Length (100 = Greedy Algorithm Length)',fontname='Helvetica', fontsize=24)
plt.show()