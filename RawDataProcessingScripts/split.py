from datetime import datetime, timedelta
import csv
import os

BASEDIR = ''

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder(BASEDIR)

createFolder(BASEDIR +'/PICKUPS')
createFolder(BASEDIR +'/DROPOFFS')
createFolder(BASEDIR +'/TRIPRECORDS')
createFolder(BASEDIR +'/TRIPRECORDSSIMULATION')

sortedPickupFile = ''
sortedDropoffFile = ''

#If the month of the file being split is before October
'''date_time_str = str(j) + "-0" + str(k) + "-21 00:00:00"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")'''

#If the month of the file being split is October or later
'''date_time_str = str(j) + "-" + str(k) + "-21 00:00:00"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")'''

#Split the pickup data
with open(sortedPickupFile, 'rb') as source:
	rdr = csv.reader(source)
	for r in rdr:
		lineDate = ""
		try:
			lineDate = datetime.strptime(r[], "%Y-%m-%d %H:%M:%S")
		except ValueError:
			print('ValueError')
		else:
			if(lineDate >= date_time_object):
				date_time_object += timedelta(minutes=15)
				isoformat = (date_time_object - timedelta(minutes=15)).isoformat()
				nameFile = isoformat.replace(":", "-") + ".csv"
				pickupFile = BASEDIR +'/PICKUPS/' + nameFile
				output = open(pickupFile, 'wb')
				output.close()

				simFile = BASEDIR +'/TRIPRECORDSSIMULATIONS/' + nameFile
				output = open(simFile, 'wb')
				output.close()

			result = open(pickupFile, 'a')
			result.write(str(r[2]) + "," + str(r[3]) + "\n")
			result.close()

			result = open(simFile, 'a')
			result.write(str(r[0]) + "," + str(r[1]) + "," + str(r[2]) + "," + str(r[3]) + "," + str(r[4]) + "," + str(r[5]) + "," + str(r[6]) + "\n")
			result.close()



#If the month of the file being split is before October
'''date_time_str = str(j) + "-0" + str(k) + "-21 00:00:00"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")'''

#If the month of the file being split is October or later
'''date_time_str = str(j) + "-" + str(k) + "-21 00:00:00"
date_time_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")'''

#Split the dropoff data
with open(sortedDropoffFile, 'rb') as source:
	rdr = csv.reader(source)
	for r in rdr:
		lineDate = ""
		try:
			lineDate = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
		except ValueError:
			print('ValueError')
		else:
			if(lineDate >= date_time_object):
				date_time_object += timedelta(minutes=15)
				isoformat = (date_time_object - timedelta(minutes=15)).isoformat()
				nameFile = isoformat.replace(":", "-") + ".csv"

				dropoffFile = BASEDIR +'/DROPOFFS/' + nameFile
				output = open(dropoffFile, 'wb')
				output.close()

				recordFile = BASEDIR +'/TRIPRECORDS/' + nameFile
				output = open(recordFile, 'wb')
				output.close()

			result = open(dropoffFile, 'a')
			result.write(str(r[4]) + "," + str(r[5]) + "\n")
			result.close()

			result = open(recordFile, 'a')
			result.write(str(r[0]) + "," + str(r[1]) + "," + str(r[2]) + "," + str(r[3]) + "," + str(r[4]) + "," + str(r[5]) + "," + str(r[6]) + "\n")
			result.close()
