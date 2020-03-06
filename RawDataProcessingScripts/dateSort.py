import csv
import operator

inputFile = ''
pickupOutputFile = ''
dropoffOutputFile = ''

#Sort by pickup datetime

ifile =open(inputFile, 'rb')
infile = csv.reader(ifile)

infile = [row for row in infile if row] # ignore empty lines


# create the sorted list
sortedlist = sorted(
        (r for r in infile if len(r) > 1),
        key=lambda r: (r[0])) #Sorted by pickup date

ifile.close
# open the output file
outfile = csv.writer(open(pickupOutputFile, 'w'), delimiter=',')

# write the sorted list
for row in sortedlist:
		outfile.writerow(row)
# processing finished, close the output file



#Sort by dropoff datetime


ifile =open(inputFile, 'rb')
infile = csv.reader(ifile)


infile = [row for row in infile if row] # ignore empty lines


# create the sorted list
sortedlist = sorted(
        (r for r in infile if len(r) > 1),
        key=lambda r: (r[1])) #Sorted by dropoff date

ifile.close
# open the output file
outfile = csv.writer(open(dropoffOutputFile, 'w'), delimiter=',')

# write the sorted list
for row in sortedlist:
		outfile.writerow(row)
# processing finished, close the output file
