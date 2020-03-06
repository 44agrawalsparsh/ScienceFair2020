import csv
import operator

inputFile = ''


#Sort by pickup datetime

ifile =open(inputFile, 'rb')
infile = csv.reader(ifile)

infile = [row for row in infile if row] # ignore empty lines


# create the sorted list
sortedlist = sorted(
        (r for r in infile if len(r) > 1),
        key=lambda r: (r[0])) #Sorted by pickup date

ifile.close
# open the output file - it can be the same as the input file
outfile = csv.writer(open('', 'w'), delimiter=',')

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
# open the output file - it can be the same as the input file
outfile = csv.writer(open('', 'w'), delimiter=',')

# write the sorted list
for row in sortedlist:
		outfile.writerow(row)
# processing finished, close the output file
