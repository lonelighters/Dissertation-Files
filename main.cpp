#define _USE_MATH_DEFINES
#include <cstdlib>
#include <ctime>
#include <string>
#include <fstream>
#include <chrono>
#include <iomanip>
#include "Spring.cpp"
#include "Node.cpp"
#include "Eigen/Dense"
#include "Eigen/QR"
#include <vector>
#include "SpringMassNetwork.cpp"


using namespace std;
using namespace Eigen;

const int PI = 3.141591;

//Hub mass ratio is the ratio of the hub node's mass to the other nodes in the web


unsigned long long rdtsc()
{
    unsigned int lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((unsigned long long)hi << 32) | lo;
}


int read_web_from_file(char *filename, vector<Node> *nodes, vector<Spring> *springs)
{

  ifstream input;
  string line;
  input.open(filename);

  if (input.is_open())
  {

    //First read the number of nodes in the file
    string skip;
    int num_nodes;
    int num_springs;

    //The first line of the input file should look like: Nodes: <num_nodes>. If it doesn't, throw an error
    input >> skip;
    if (skip != "Nodes")
    {
      cout << "Error: Expected first line to contain number of nodes" << endl;
      return 0;
    }

    input >> num_nodes;

    //Now read the next num_nodes lines to get the node information
    for (int i = 0;i<num_nodes;i++)
    {
      int id, fixed;
      float x, y, z, radius, theta, mass;

      input >> id >> x >> y >> z >> radius >> theta >> mass >> fixed;
      Node new_node(id, x, y, z, mass);

      if (fixed)
      {
        new_node.set_fixed(true);
      }
      nodes->push_back(new_node);
    }

    //Now read the number of springs

    input >> skip;
    if (skip !="Springs")
    {
       cout << "Error: Expected next line to contain number of springs" << endl;
      return 0;     
    }

    input >> num_springs;

    for (int i =0;i<num_springs;i++)
    {
      int id;
      int node1;
      int node2;
      float resting_length;
      float initial_length;
      int type;
      float k1;
      float k3;
      float d1;
      float d3;

      input >> id >> node1 >> node2 >> resting_length >> initial_length >> type >> k1 >> k3 >> d1 >> d3;

      Spring new_spring(id, node1, node2, resting_length, initial_length, k1, k3, d1, d3);
      new_spring.set_type(type);
      springs->push_back(new_spring);
    }
  }

  input.close();

  return 1;
}

int main(int argc, char** argv)
{

    auto begin = std::chrono::high_resolution_clock::now();

    srand(rdtsc());

    char *filename;

    if (argc < 2)
    {
      printf("Error: No input file provided\n");
      return 1;
    }
    else if (argc == 2)
    {
      filename = argv[1];
    }

    vector<Node> nodes;
    vector<Spring> springs;

    if (!read_web_from_file(filename, &nodes, &springs))
    {
      cout << "Error reading file" << endl;
    }

    int num_timesteps = 20000; // 200000 at 10ms
    double dt = 0.01; // 0.01 at 10ms
    double tmax = num_timesteps * dt;

    SpringMassNetwork network(nodes, springs, dt, tmax);

    network.run();

    /*
    auto end = std::chrono::high_resolution_clock::now();
    cout << "The time it took for the programme to run in total in milliseconds: ";
    std::cout << std::chrono::duration_cast<std::chrono::milliseconds>(end-begin).count() << "ms" << endl;
    */

    return 0;

}



   