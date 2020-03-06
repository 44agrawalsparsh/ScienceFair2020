#File used to prepare distribution data samples for training the prediction model

from interruptingcow import timeout
import os
import PyACO.PyMonteCarlo.MonteCarlo as mc

PATHTOINPUTFILES = 'RAWDATA/TRIPRECORDS'

# For each file in a set of inputs, process the output
def process():
	startTime = datetime.now()
	for fileName in os.listdir(PATHTOINPUTFILES):
		try:
			with timeout(100, exception = RuntimeError):
				mc.preparePoints(fileName)
		except RuntimeError:
			pass

process()