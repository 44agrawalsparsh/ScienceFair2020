import csv
import convertor

inputFile = ''
outputFile = ''

with open(inputFile,"r") as source:
	rdr= csv.reader( source )
	with open(outputFile,"wb") as result:
		wtr= csv.writer( result )
		for r in rdr:
			#For data where exact coordinates are provided
			'''
			if(r != [] and (r[5] != '0' and r[6] != '0') and (r[9] != '0' and r[10] != '0') and (r[0] != 'VendorID')):
				try:

					pickupLongtitude = str(r[5])
					pickupLatttitude = str(r[6])

					dropoffLongtitude = str(r[9])
					dropoffLatttitude = str(r[10])

					#pickup time, dropoff time, pickup longtitude, pickup lattitude, dropoff longtitude, dropoff lattitude, Fare
					wtr.writerow((r[1], r[2], pickupLongtitude, pickupLatttitude, dropoffLongtitude, dropoffLatttitude, r[-1]))
							
				except:
					pass

			'''


			#For data where only the taxi zones are provided
			'''
			if(r != [] and (r[7] != '0' and r[8] != '0') and (r[7] != 'PULocationID' and r[8] != 'DOLocationID')):
				try:
						
					pickupPoint = convertor.convert(int(r[7]))
					dropoffPoint = convertor.convert(int(r[8]))

					pickupLongtitude = str(pickupPoint.x)
					pickupLatttitude = str(pickupPoint.y)

					dropoffLongtitude = str(dropoffPoint.x)
					dropoffLatttitude = str(dropoffPoint.y)

					#pickup time, dropoff time, pickup longtitude, pickup lattitude, dropoff longtitude, dropoff lattitude, Fare
					wtr.writerow((r[1], r[2], pickupLongtitude, pickupLatttitude, dropoffLongtitude, dropoffLatttitude, r[-2]))
							
				except:
					pass

			'''