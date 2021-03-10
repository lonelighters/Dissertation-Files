#define _USE_MATH_DEFINES
#include <iostream>
#include <random>
#include <algorithm>
#include <cmath>
#include <ctime>
#include <vector>
#include "SpringMassNetwork.h"
#include "Eigen/Dense"
#include "Eigen/QR"
#include "Eigen/SVD"
#include "Eigen/LU"
#include <sstream>
#include <fstream>
#include <string>
#include <iomanip>
using namespace std;
using namespace Eigen;

SpringMassNetwork::SpringMassNetwork(vector<Node> &nodes, vector<Spring> &springs, double dt, double tmax)
{

	this->dt = dt;
	this->tmax = tmax;
	this->num_timesteps = int(tmax / dt);
	this->nodes = nodes;
	this->springs = springs;
	this->num_nodes = nodes.size();
	this->num_springs = springs.size();
}


void SpringMassNetwork::reset()
{

}

void SpringMassNetwork::print_edges()
{
	for (int i=0;i<num_springs;i++)
	{
		printf("%d, %d, %d, %.3f, %.3f, %d, %.3f, %.3f, %.3f, %.3f\n", 
         springs[i].get_id(), 
         springs[i].get_node_a_id(), 
         springs[i].get_node_b_id(), 
         springs[i].get_resting_length(), 
         springs[i].get_initial_length(), 
         springs[i].get_type(), 
         springs[i].get_k1(),
         springs[i].get_k3(),
         springs[i].get_d1(),
         springs[i].get_d3());
	}
}

void SpringMassNetwork::run()
{

	//Print network info
	printf("Num Nodes\t%d\nNum Springs\t%d\ntimestep\t%.3f\nnum_timesteps\t%d\n", num_nodes, num_springs, dt, num_timesteps);

	//Print edge list

	print_edges();

   	for (int i=0;i<num_timesteps;i++)
   	{
   		//First loop over spring
   		for (int j=0;j<springs.size();j++)
   		{
   			//Get indices of nodes connected by this spring
   			int first_node_id = springs[j].get_node_a_id();
   			int second_node_id = springs[j].get_node_b_id();

   			//printf("Spring %d connects node %d to node %d\n", j, first_node_id, second_node_id);

   			//Get position of first node
   			double x1 = nodes[first_node_id].get_x_position();
   			double y1 = nodes[first_node_id].get_y_position();
   			//Get position of second node
   			double x2 = nodes[second_node_id].get_x_position();
   			double y2 = nodes[second_node_id].get_y_position();

            double z1 = nodes[first_node_id].get_z_position();
            double z2 = nodes[second_node_id].get_z_position();

   			/*
		    printf("X1: %f\n", x1);
		    printf("X2: %f\n", x2);
		    printf("Y1: %f\n", x1);
		    printf("Y2: %f\n", x2);
		    */

   			//Update spring based on nodal positions
   			springs[j].update3d(x1, y1, z1, x2, y2, z2, dt);
   			//Calculate forces applied by spring
   			double f_x = springs[j].get_force_x();
   			double f_y = springs[j].get_force_y();
            double f_z = springs[j].get_force_z();
   			//Apply forces to nodes

   			nodes[first_node_id].apply_force(f_x, f_y, f_z);
   			nodes[second_node_id].apply_force(-f_x, -f_y, -f_z);

   			//springs[j].print_position_and_force();
   		}

         //Add sinusoidal force to hub for testing
         double sin_force = 5; //initially 5

         if (i > 1000) //Initially 1000
         {
            sin_force = 0;
         }

         nodes[0].apply_force(0., 0., sin_force);

   		//Now loop over nodes
   		for (int j=0;j<nodes.size();j++)
   		{
   			//Print before update to keep plotting in sync with springs
   			nodes[j].print_positions_and_velocities();
   			nodes[j].update(dt);
   			nodes[j].reset_forces();

   		}

   		cout << endl;

   	}
}

void SpringMassNetwork::print_output()
{

}
