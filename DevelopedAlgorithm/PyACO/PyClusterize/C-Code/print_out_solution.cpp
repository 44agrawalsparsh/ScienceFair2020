#include <iostream>
#include <iomanip>      // std::setprecision
#include <cmath>
#include "point.hpp"
#include "print_out_solution.hpp"
#include <fstream>

using namespace std;

void print_out(const vector<Point> centers, const vector<double> &weights, const vector<Point> &clients,
	      const Assignment &assignment){
  ofstream outputFile;
  outputFile.open("PyACO/PyClusterize/Temp/do_redistrict_output.txt");
  int num_centers = centers.size();
  int num_clients = clients.size();
  //cout << num_centers << " " << num_clients << endl;
  outputFile << num_centers << " " << num_clients << endl;
  //cout << setprecision(12);
  for(int j = 0; j < num_centers; j++){
    //cout << centers[j].x << " " << centers[j].y << " " << sqrt(weights[j]) << endl;
    outputFile << centers[j].x << " " << centers[j].y << " " << sqrt(weights[j]) << endl;
  }
  for(int i = 0; i < num_clients; i++){
      //cout << clients[i].x << " " << clients[i].y ;
      outputFile << clients[i].x << " " << clients[i].y ;
      for (AssignmentElement ae : assignment[i]){
    	  //cout << " "<< ae.center <<" " << ae.flow ;	
        outputFile << " "<< ae.center <<" " << ae.flow ;
      }
      //cout << endl;
      outputFile << endl;
  }
}
