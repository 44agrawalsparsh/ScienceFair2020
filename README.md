# ScienceFair2020
A machine learning framework for real-time taxi dispatching

# What the program does?

In the provided software there are three key components: visualization scripts used to generate plots, processing scripts to synthesize raw data from the NYC TLC Yellow Taxi Trip dataset into a format usable for the algorithm and the developed algorithm itself.

The developed algorithm works by initially predicting a set of taxi trips that will occur in the next 90 minutes. The predictions are generated through the developed deep learning taxi demand prediction model and the developed monte carlo algorithm. The algorithm then approximates the locations of taxis and passengers for the next 90 minutes. Initially, it assumes that the taxis will be dispatched to the passengers for the first 75 minutes based on a local greedy algorithm. The algorithm also starts running the developed ACO on the furthest timestep (taxi trips for 75-90 minutes ahead).

Every 15 minutes this same process repeats. Now, the algorithm only assumes local greedy dispatching until 60 minutes ahead, and the ACO algorithm is run concurrently for the furthest two timesteps (0-75 minutes and 75-90 minutes ahead). This process repeats until the ACO algorithm is running on all predicted timesteps (0-90 minutes ahead). 

At this point, the algorithm is continuously outputting a dispatch route every 15 minutes. This dispatch route splits the city into 1000 taxi regions and 1000 passenger regions. Each taxi region is linked with a passenger region, meaning that when a taxi is vacant it will be sent to the passenger region that is linked with the taxi region it is currently in.

Along with the developed algorithm, a simulator has been created. This simulator can simulate a taxi fleet managed by the developed algorithm or through the existing system where taxis attempt to search for the closest passenger in their region. The simulator will concurrently run the algorithm and simulate a fleet of taxis searching for and picking up passengers. Though the machine that the simulator was developed on was able to handle both of these tasks concurrently, it may be advisable to have these tasks run sequentially as running them together is a very computationally intensive task. This would be a quick and easy change.

The simulator outputs a passenger and taxi log. The passenger log contains a list of all of the passengers present in the scenario, their pickup time, their dropoff time, and their trip's fee. The taxi log contains a list of all of the taxi's assignments (both dispatches and passenger trips) and their length. The visualizations folder contains multiple scripts to visualize the performance of the fleet based on these logs.

Using the simulator and visualization software is very easy. For the simulator, all that needs to be specified is whether the developed algorithm or base algorithm should be used to manage the fleet. Additionally, the RAWDATA.zip file (located in DevelopedAlgorithm) should be unzipped as well as the Model.zip file (located in DevelopedAlgorithm/PyACO/PyMonteCarlo). The visualization sofwtare simply requires the output logs of a simulation on the developed algorithm and status quo system to be placed in a folder called SIMULATORLOGS and then into either ALGO_RESULTS or BASE_RESULTS.

Raw data is available at https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page

# Libraries Used:

Tensorflow 2.0, sklearn, numpy, scipy, pandas, shapely, datetime, subprocess, multiprocessing, random, joblib, copy, os, sys, matplotlib, operater, csv, interruptingcow, cv2, PIL, imageio, pickle, time, statistics, pydot, graphviz

# Development Environment:

macOS 10.14.6

python 3.6.6

# Set up:

The code should work as is in any environment that has the necessary libraries as well as the correct version of python. All zip files within the repository will have to be unzipped as well. There is an unix executable contained in the PyClusterize model of this program for the redistricting algorithm. If a non-unix environment is utilized, a makefile located in the C-Code file on the PyClusterize model can be utilized to generate a new executable. Note the executable would have to be moved to the PyClusterize module and some adjustments will have to made to the makefile depending on the machine used.

To execute the makefile after the appropriate changes have been made simply enter the command

```
make
```
# How to run the simulator

The simulator can easily be run through:

```
python Simulator.py
```

**Note that after each time the simulator is run, the data in the individual folders in DevelopedAlgorihtm/RAWDATA should be cleared. Additionally, the file DevelopedAlgorihtm/RAWDATA/listOfPoints.csv should be made blank again**

# How to train the model

Though the trained model and scalers are provided in the Model.zip file, if required, the model can be trained again. First, the raw taxi data from the NYC TLC Yellow Taxi dataset will have to be processed through the scripts in the RawDataProcessingScripts folder. 

For each file that needs to be processed, the following steps should be followed:

In the dataformatter file, a section of code will have to be uncommented. If the dataset contains the exact co-ordinates of the trip start and endpoints, the first block should be commented. If just the general taxi region is given (the header will be 'PULocationID' or 'DOLocationID'), the second block should be uncommented.

The desired input filename and output filename should also be entered.

The dataformatter script should then be run:

```
python dataformatter.py
```

Next, the data needs to be sorted through the dateSort script. The input file needs to be specified (this should be the output file of dataformatter.py) as well as the output files (sorted by pickup time and dropoff time).

The date sort file should then be run:

```
python dateSort.py
```

Finally, the data needs to be split into 15-minute timesteps. The directory to the sorted pickup and dropoff data needs to be specified as well as a directory to where the output data should be stored. Additionally, the starting datetime should be specified. This should be midnight on the first of the month's data being processed.

The split file should then be run:

```
python split.py
```

The timestep data - DROPOFFS, PICKUPS, TRIPRECORDS, TRIPRECORDSSIMULATION - should now be entered into DevelopedAlgorithm/RAWDATA

Now the training data for the deep learning algorithm should be processed by running PrepareDeepLearningInputs

```
python PrepareDeepLearningInputs.py
```

At this point, DevelopedAlgorithm/PyACO/PyMonteCarlo/Data can be moved to any desired location.

It is suggested that DevelopedAlgorithm/PyACO/PyMonteCarlo/PyTaxiNet/DataPointsIdentifier.py be run. The path to the processed data will have to be specified in the script.

```
python DataPointsIdentifier.py
```

ModelTraining.py can now be run, but file directories will have to be defined in ModelCreator.py and ModelTraining.py

```
python ModelTraining.py
```

**Note that the above process will take significant amounts of time, so it is suggested that the provided pre-trained model be used instead**
