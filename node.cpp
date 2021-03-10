#include <iostream>
#include "node.h"
using namespace std;



 Node::Node(int id, double x_position, double y_position, double z_position, double mass)
 {
  this->id = id;
  this->x_position = x_position;
  this->y_position = y_position;
  this->z_position = z_position;
  this->mass = mass;

  this->x_velocity = 0;
  this->y_velocity = 0;
  this->z_velocity = 0;

  this->initial_x_position = x_position;
  this->initial_y_position = y_position;
  this->initial_z_position = z_position;
 }

//If this function is activated than the node is input node
void Node::set_input(bool state)
{
  input_node = state;
}

bool Node::is_input()
{
  return input_node;
}

bool Node::is_fixed()
{
  return fixed_node;
}

void Node::set_mass(double new_mass)
{
  mass = new_mass;
}

double Node::get_mass()
{
  return mass;
}


void Node::reset_positions()
{
  x_position = initial_x_position;
  y_position = initial_y_position;
  z_position = initial_z_position;
}


void Node::set_fixed(bool state)
{
  this->fixed_node = state;
}

void Node::print_position()
{
  printf("%d\t%.3f\t%.3f\t%.3f\n", id, x_position, y_position, z_position);
}

void Node::print_positions_and_velocities()
{
  printf("%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n", id, x_position, y_position, z_position, x_velocity, y_velocity, z_velocity);
}

double Node::get_x_position()
{
  return x_position;
}

double Node::get_y_position()
{
  return y_position;
}

double Node::get_z_position()
{
  return z_position;
}

double Node::get_x_velocity()
{
  return x_velocity;
}

double Node::get_y_velocity()
{
  return y_velocity;
}

double Node::get_z_velocity()
{
  return z_velocity;
}

double Node::get_x_acceleration()
{
  return x_acceleration;
}

double Node::get_y_acceleration()
{
  return y_acceleration;
}

double Node::get_z_acceleration()
{
  return z_acceleration;
}


//This is the function that incrementally changes the Node position in the next timestep;

void Node::apply_force(double Fx, double Fy)
{
    input_force_x += Fx;
    input_force_y += Fy;
}

void Node::apply_force(double Fx, double Fy, double Fz)
{
    input_force_x += Fx;
    input_force_y += Fy;
    input_force_z += Fz;
}

void Node::reset_forces()
{
    input_force_x = 0;
    input_force_y = 0;
    input_force_z = 0;
}

void Node::update(double dt)
{

  if (!fixed_node)
  {
  //Standard Euler integration - maybe add Runge Kutta later
      x_acceleration = input_force_x / mass;
      y_acceleration = input_force_y / mass;
      z_acceleration = input_force_z / mass;

      x_velocity += dt * x_acceleration;
      y_velocity += dt * y_acceleration;
      z_velocity += dt * z_acceleration;

      x_position += dt * x_velocity;
      y_position += dt * y_velocity;
      z_position += dt * z_velocity;
  }

}

void Node::reset_state()
{
    x_velocity = 0;
    y_velocity = 0;
    z_velocity = 0;

    x_acceleration = 0;
    y_acceleration = 0;
    z_acceleration = 0;
}

void Node::reset()
{
    this->reset_state();
    this->reset_forces();
    this->reset_positions();
}

void Node::change_update_check()
{
    update_check = 1;
}

bool Node::return_update_check()
{
    return update_check;
}

void Node::zero_update_check()
{
   update_check = 0;
}
