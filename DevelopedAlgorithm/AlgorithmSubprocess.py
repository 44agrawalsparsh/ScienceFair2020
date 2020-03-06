#Unfortunately Tensorflow isn't fully multprocess safe, but it can however be run in a seperate subprocess. I created a seperate file to run the MainAlgorithm so that the simulator could call it as a subprocess.

import MainAlgorithm
import pickle

#Load the input bench

infile = open('SubProcessFiles/Input/INPUTBENCH', 'rb')

bench = pickle.load(infile)

infile.close()

#Load the file to run the algorithm on as well as the amount of processing time appropriated

infile = open('SubProcessFiles/Input/InputDetails.txt', 'r')

dataDir = str(infile.readline())[:-1]

processingTime = int(infile.readline())

infile.close()

#Run the algorithm
newBench, bestPath = MainAlgorithm.calculateTimeStep(bench, dataDir, processingTime)

#Pickle the output of the algorithm
outfile = open('SubProcessFiles/Output/OUTPUTBENCH', 'wb')
pickle.dump(newBench, outfile)
outfile.close()

outfile = open('SubProcessFiles/Output/PATH', 'wb')
pickle.dump(bestPath, outfile)
outfile.close()

exit()