# ScienceFair2020
A machine learning framework for real-time taxi dispatching

# What the program does?

In the provided software there are three key components: visualization scripts used to generate plots, processing scripts to synthesize raw data from the NYC TLC Yellow Taxi Trip dataset into a format usable for the algorithm and the developed algorithm itself.

The developed algorithm works by initially predicting a set of taxi trips that will occur in the next 90 minutes. The predictions are generated through the developed deep learning taxi demand prediction model and the developed monte carlo algorithm. The algorithm then approxamates the locations of taxis and passengers for the next 90 minutes. Initially, it assumes that the taxis will be dispatched to the passengers for the inital 75 minutes. The algorithm also starts running the developed ACO on the furthest timestep (taxi trips for 75-90 minutes ahead).

Every 15 minutes this same process repeats. Now the algorithm only assumes local greedy dispatching until 60 minutes ahead, and the ACO algorithm is run concurrently for the furthest two timesteps (0-75 minutes and 75-90 minutes ahead). This process repeats until the ACO algorithm is running on all predicted timesteps (0-90 minutes ahead). 

At this point the algorithm is continously outputting a dispatch route every 15 minutes. This dispatch route splits the city into 1000 taxi regions and 1000 passenger regions. Each taxi region is linked with a passenger resion, meaning that if a taxi driver is vacant that outputted path way will direct it to the optimal location to search for a passenger.

Along with the developed algorithm, a simulator has been created. This simulator can simulate a taxi fleet managed by the developed algorithm and one managed through the existing system where taxis attempt to search for the closest passenger in their region. The simulator will concurrently run the algorithm and simulate a fleet of taxis searching for and picking up passengers. Though the machine that the simulator was developed on was able to handle both of these tasks concurrently, it may be advisable to have these tasks run sequentially. This would be a quick and easy change.

The simulator outputs a passenger and taxi log. The passenger log contains a list of all of the passenegrs present in the scenario, their pickup time, their dropoff time, and their trip's fee. The taxi log contains a list of all of the taxi's assignemnts (both dispatches and passenger trips) and their length. The visualizations folder contains multple scripts to visualize the performance of the fleet.

Using the simulator and visualization software is very easy. For the simulator, all that needs to be specified is whether the developed algorithm or base algorithm should be used to manage the fleet. Additionally, the RAWDATA.zip file should be unzipped as well as the Model.zip file (located in DevelopedAlgorithm/PyACO/PyMonteCarlo). The visualization sofwtare simply requires the output logs of a simulation on the developed algorithm and status quo system to be placed in a folder called SIMULATORLOGS and then into either ALGO_RESULTS or BASE_RESULTS.

Raw data is available at: https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page

# Libraries Used:

Tensorflow 2.0, sklearn, numpy, scipy, pandas, shapely, datetime, subprocess, multiprocessing, random, joblib, copy, os, sys, matplotlib, operater, csv, interruptingcow, cv2, PIL, imageio, pickle, time, statistics, pydot, graphviz

# Environment in which code works on:

macOS 10.14.6
python 3.6.6

# Set up:

The code should work as is in any environment that has the neccessary libraries as well as the correct version of python. All zip files within the repository will have to be unzipped as well. There is an unix executable contained in the PyClusterize model of this program for the redistictring algorithm. If a non-unix environment is utilized, a makefile located in the C-Code file on the PyClusterize model can be utilized to generate a new executable. Note the executable would have to be moved to the PyClusterize module and some adjustments will have to made depending on the machine used.


