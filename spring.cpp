#include <iostream>
#include <cmath>
#include "spring.h"
using namespace std;



//Make a standard spring; linear with default stiffness and damping values
Spring::Spring(int id, int node_a, int node_b, double resting_length, double initial_length)
{

    this->id = id;
    this->node_a = node_a;
    this->node_b = node_b;
    this->resting_length = resting_length;
    this->length = initial_length;
    this->extension = length - resting_length;
    this->old_extension = extension;
    this->initial_length = initial_length;
    this->type = SPIRAL;

}

//Make a linear spring with specified stiffness and damping values
Spring::Spring(int id, int node_a, int node_b, double resting_length, double initial_length, double k1, double d1)
{
    this->id = id;
    this->node_a = node_a;
    this->node_b = node_b; 

    this->resting_length = resting_length;
    this->length = initial_length;
    this->extension = length - resting_length;
    this->old_extension = extension;
    this->initial_length = initial_length;

    this->k1 = k1;
    this->d1 = d1;

    this->type = SPIRAL;

}

//Make a cubic spring
Spring::Spring(int id, int node_a, int node_b, double resting_length, double initial_length, double k1, double d1, double k3, double d3)
{
    this->id = id;
    this->node_a = node_a;
    this->node_b = node_b; 

    this->resting_length = resting_length;
    this->length = initial_length;
    this->extension = length - resting_length;
    this->old_extension = extension;
    this->initial_length = initial_length;

    this->k1 = k1;
    this->d1 = d1;
    this->k3 = k3; 
    this->d3 = d3;

    this->type = SPIRAL;


};

void Spring::reset()
{
    this->length = length;
    this->extension = length - resting_length;
    this->old_extension = extension;
}

//This is the main method which is used to update the spring throughout the simulation
void Spring::update2d(double node_a_x_position, double node_a_y_position, double node_b_x_position, double node_b_y_position, double dt)
{
    //Calculate nodal displacements in terms of x/y components

    x1 = node_a_x_position;
    y1 = node_a_y_position;
    x2 = node_b_x_position;
    y2 = node_b_y_position;

    double x_displacement = node_a_x_position - node_b_x_position;
    double y_displacement = node_a_y_position - node_b_y_position;

    /*
    printf("X1: %f\n", x1);
    printf("X2: %f\n", x2);
    printf("Y1: %f\n", x1);
    printf("Y2: %f\n", x2);
    */

    //Update spring length
    length = sqrt((x_displacement * x_displacement) + (y_displacement * y_displacement));

    //Update spring extension and derivative
    old_extension = extension;
    extension = length - resting_length;
    extension_derivative = (extension - old_extension) / dt;


    //Use calculate force here to allow option of custom spring force extensions later
    force_magnitude = calculate_force();
    force_x = force_magnitude * (x_displacement / length);
    force_y = force_magnitude * (y_displacement / length);

    /*
    printf("Length: %f\n", length);
    printf("Fx: %f\n", force_x);
    printf("Fy: %f\n", force_y);
    */

    print_debug();

}

void Spring::update3d(double node_a_x_position, double node_a_y_position, double node_a_z_position, double node_b_x_position, double node_b_y_position, double node_b_z_position, double dt)
{
    //Calculate nodal displacements in terms of x/y components

    x1 = node_a_x_position;
    x2 = node_b_x_position;
    y1 = node_a_y_position;
    y2 = node_b_y_position;
    z1 = node_a_z_position;
    z2 = node_b_z_position;

    double x_displacement = node_a_x_position - node_b_x_position;
    double y_displacement = node_a_y_position - node_b_y_position;
    double z_displacement = node_a_z_position - node_b_z_position;

    /*
    printf("X1: %f\n", x1);
    printf("X2: %f\n", x2);
    printf("Y1: %f\n", x1);
    printf("Y2: %f\n", x2);
    */

    //Update spring length
    length = sqrt((x_displacement * x_displacement) + (y_displacement * y_displacement) + (z_displacement * z_displacement));

    //Update spring extension and derivative
    old_extension = extension;
    extension = length - resting_length;
    extension_derivative = (extension - old_extension) / dt;


    //Use calculate force here to allow option of custom spring force extensions later
    force_magnitude = calculate_force();
    force_x = force_magnitude * (x_displacement / length);
    force_y = force_magnitude * (y_displacement / length);
    force_z = force_magnitude * (z_displacement / length);

    /*
    printf("Length: %f\n", length);
    printf("Fx: %f\n", force_x);
    printf("Fy: %f\n", force_y);
    */

    print_debug();

}

//Currently this just calculates the force due to a cubic spring 
//Future work could use a function pointer to allow this to any force function we desire.
double Spring::calculate_force()
{
    double cubic_stiffness = -k3 * (extension * extension * extension);
    double linear_stiffness = -k1 * extension;
    double cubic_damping = -d3 * (extension_derivative * extension_derivative * extension_derivative);
    double linear_damping = -d1 * extension_derivative;

    return linear_stiffness + cubic_stiffness + linear_damping + cubic_damping;
}

void Spring::print_position()
{

    printf("%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t", id, x1, y1, z1, x2, y2, z2);
}

void Spring::print_force()
{
    printf("%d\t%.3f\t%.3f\t%.3f\t%.3f\t", id, force_magnitude, force_x, force_y, force_z);
}

void Spring::print_position_and_force()
{
    printf("%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n", id, x1, y1, z1, x2, y2, z2, force_magnitude, force_x, force_y, force_z);
}

//Add to this as necessary
void Spring::print_debug()
{
  switch(debug_level)
  {
    case 0:
        break;
    case 1:
        printf("Spring connecting node %d to node %d\n", node_a, node_b);
        printf("Length: %.3f, Force: %.3f\n", length, force_magnitude);
        break;
    case 2:
        printf("Spring connecting node %d to node %d\n", node_a, node_b);
        printf("Length: %.3f, Force: %.3f\n", length, force_magnitude);
        printf("Extension: %.3f, Deriv: %.3f\n", extension, extension_derivative);
        break;
  }
}

void Spring::set_debug_level(int new_level)
{
  debug_level = new_level;
}

double Spring::get_force_magnitude()
{
  return force_magnitude;
}

double Spring::get_force_x()
{
  return force_x;
}

double Spring::get_force_y()
{
  return force_y;
}

double Spring::get_force_z()
{
  return force_z;
}

double Spring::get_length()
{
  return length;
}

double Spring::get_extension()
{
  return extension;
}

double Spring::get_extension_derivative()
{
  return extension_derivative;
}

double Spring::get_initial_length()
{
    return initial_length;
}

double Spring::get_resting_length()
{
  return resting_length;
}

void Spring::set_resting_length(double new_resting_length)
{
  resting_length = new_resting_length;
}

int Spring::get_node_a_id()
{
  return node_a;
}

int Spring::get_node_b_id()
{
  return node_b;
}

int Spring::get_id()
{
    return id;
}

void Spring::set_type(int type)
{
    this->type = type;
}

int Spring::get_type()
{
    return type;
}

double Spring::get_k1()
{
return k1;
}

double Spring::get_k3()
{
return k3;
}

double Spring::get_d1()
{
return d1;
}

double Spring::get_d3()
{
return d3;
}

void Spring::set_k1(double k1)
{
this->k1 = k1;
}

void Spring::set_k3(double k3)
{
this->k3 = k3;
}

void Spring::set_d1(double d1)
{
this->d1 = d1;
}

void Spring::set_d3(double d3)
{
this->d3 = d3;
}