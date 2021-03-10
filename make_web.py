import matplotlib 
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt 
import mpl_toolkits.mplot3d.axes3d as p3 
import matplotlib.animation as animation
plt.ion()
import numpy as np 
import seaborn as sn 
import networkx as nx
import yaml
import copy
import argparse


DEFAULT_NODE_MASS = 0.1
DEFAULT_HUB_MASS_RATIO = 10
DEFAULT_NUM_RADIALS = 16
DEFAULT_WINDING_CONSTANT = 0.5
DEFAULT_MAX_SPIRAL_RADIUS = 18
DEFAULT_FREE_ZONE_RADIUS = 5
DEFAULT_FRAME_RADIUS = 25
DEFAULT_SECOND_FRAME_RADIUS = 35
DEFAULT_MOORING_RADIUS = 45
HUB_ID = 0

DEFAULT_K1 = 100.
DEFAULT_K3 = 0.
DEFAULT_D1 = 100.
DEFAULT_D3 = 0.

SPIRAL_THREAD = 0
RADIAL_THREAD = 1

RESTING_LENGTH_WARNING = 0.1


#This is convenient class to collect all experiment parameters together
class WebParams:

    def __init__(self, node_mass, hub_mass_ratio, num_radials, winding_constant, max_spiral_radius, free_zone_radius, frame_radius, second_frame_radius, mooring_radius):

        self.node_mass = node_mass
        self.hub_mass_ratio = hub_mass_ratio
        self.num_radials = num_radials
        self.winding_constant = winding_constant
        self.max_spiral_radius = max_spiral_radius
        self.free_zone_radius = free_zone_radius
        self.frame_radius = frame_radius
        self.second_frame_radius = second_frame_radius
        self.mooring_radius = mooring_radius

        #TODO - ADD some warnings / checks here -- eg if spiral radius is greater than frame radius
        if hub_mass_ratio < 1:
            print("Warning: hub mass ratio is less than 1 -- is this what you intended?")

        if free_zone_radius > max_spiral_radius:
            print("Warning: max spiral radius is bigger than free zone radius -- no spiral will be produced")

        if frame_radius < max_spiral_radius:
            print("Warning: frame radius is less than max spiral radius")

        if second_frame_radius < frame_radius:
            print("Warning: outer frame radius is less than inner frame radius")

        if mooring_radius < second_frame_radius:
            print("Warning: mooring radius is less than outer frame radius")


    def __repr__(self):

        return "Node mass: %f\tHub mass ratio: %f\tNum radials: %d\tWinding constant: %f\tMax radius: %f\tFree zone radius: %f\tFrame radius: %f\t"


    def get_string_for_writing_to_file(self):

        return "%.3f\t%.3f\t%d\t%.3f\t%.3f\t%.3f\t%.3f\t" % (self.node_mass, 
            self.hub_mass_ratio, 
            self.num_radials, 
            self.winding_constant, 
            self.max_spiral_radius, 
            self.free_zone_radius, 
            self.frame_radius)



class Node:

    def __init__(self, id_no, x, y, z, radius, theta, mass, fixed=False):

        self.id = int(id_no)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.radius = float(radius)

        #Seems to be a strange bug (probably due to floating point numbers) where x mod 360 returns 0 below 720 and 360 above it. This fixes the error. isclose is floating point equiv of ==
        if isclose(theta, 360.000):
            theta = 0.0
        self.theta = float(theta)
        self.mass = float(mass)
        self.fixed = fixed

    
    def __repr__(self):

        return "Node %d\tX: %.3f\tY : %.3f\tZ pos: %.3f\tTheta: %.3f\n" % (self.id, self.x, self.y, self.z, self.theta) 


    def get_string_for_writing_to_file(self):

        if self.fixed:
            fixed = 1
        else:
            fixed = 0

        return "%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%d\n" % (self.id, self.x, self.y, self.z, self.radius, self.theta, self.mass, fixed)
    


class Spring:

    def __init__(self, id_no, node1, node2, resting_length, initial_length, thread_type, k1=DEFAULT_K1, k3=DEFAULT_K3, d1=DEFAULT_D1, d3=DEFAULT_D3):

        self.id_no = id_no
        self.node1 = node1
        self.node2 = node2
        self.resting_length = resting_length
        self.initial_length = initial_length
        self.type = thread_type

        self.k1 = k1
        self.k3 = k3
        self.d1 = d1
        self.d3 = d3

        #TODO - ADD warning for very small resting lengths
        if resting_length < RESTING_LENGTH_WARNING:
            print("Warning: spring %d has a short resting length of: %f" % (self.id_no, self.resting_length))

    
    def __repr__(self):

        return "Spring %d connects node %d to node %d\n" % (self.id_no, self.node1, self.node2)


    def get_string_for_writing_to_file(self):

        return "%d\t%d\t%d\t%.3f\t%.3f\t%d\t%.3f\t%.3f\t%.3f\t%.3f\n" % (self.id_no, self.node1, self.node2, self.resting_length, self.initial_length, self.type,
            self.k1, self.k3, self.d1, self.d3)
 


#This function is a floating point equivalent to ==   
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)



def make_hub(hub_mass):

    nodes = []
    hub = Node(0, 0, 0, 0, 0, 0, hub_mass)
    nodes.append(hub)

    return nodes



def make_spiral(nodes, springs, node_index, spring_index, params):

    node_mass = params.node_mass
    num_radials = params.num_radials
    winding_constant = params.winding_constant
    max_spiral_radius = params.max_spiral_radius
    free_zone_radius = params.free_zone_radius

    #The outer loop will proceed around the web in steps given by 360 / num_radials
    theta_step = np.deg2rad(360) / num_radials
    theta = 0

    #We will move along the spiral in steps given by theta_step, placing a node at each intersecting point
    radius = 0
    #We will add a spring connecting each node to the previous node in this loop. The first_node flag is used to ensure this is skipped for the first node we add. 
    first_node = True

    while (radius < max_spiral_radius):

        radius = theta * winding_constant

        #Only add a node if we are outside of the free zone
        if (radius > free_zone_radius):
            x_pos = radius * np.cos(theta)
            y_pos = radius * np.sin(theta)
            z_pos = 0

            #Add the node
            new_node = Node(node_index, x_pos, y_pos, z_pos, radius, np.rad2deg(theta) % 360, node_mass)
            nodes.append(new_node)

            #Skip spring creation for first spiral node
            if first_node:
                first_node = False
            else:
                resting_length = get_resting_length_from_ids(node_index, node_index-1, nodes)
                new_spring = Spring(spring_index, node_index, node_index-1, resting_length, resting_length, SPIRAL_THREAD)
                springs.append(new_spring)
                spring_index = spring_index + 1

            node_index = node_index + 1

        theta = theta + theta_step

    return (nodes, springs, node_index, spring_index)



def make_radials(nodes, springs, spring_index, params, num_nodes):

    node_mass = params.node_mass
    num_radials = params.num_radials

    '''
    Now we will add the springs connecting radial threads
    We will do this by looping through the nodes (skipping the hub) and adding a spring connecting it to the next node with the same angle. 
    This node will be given by index + num_radials
    '''
    for (i, node) in enumerate(nodes):

        #Skip first node as this is the hub
        if i > 0:

            #Add connections to the hub for the inner nodes
            if i <= num_radials:
                resting_length = get_resting_length_from_ids(i, 0, nodes)
                new_spring = Spring(spring_index, 0, i, resting_length, resting_length, RADIAL_THREAD)
                #print("Spring %d connects node %d to node %d has resting length %f\n" % (spring_index, 0, i, resting_length))
                springs.append(new_spring)
                spring_index = spring_index + 1

            #Now add a spring along the radial
            #First we have to calculate the index of the next (radial) node
            next_node_index = i + num_radials

            #Only add the spring if the node exists
            if next_node_index <= num_nodes:
                resting_length = get_resting_length_from_ids(i, next_node_index, nodes)
                new_spring = Spring(spring_index, i, next_node_index, resting_length, resting_length, RADIAL_THREAD)
                #print("Spring %d connects node %d to node %d has resting length %f\n" % (spring_index, i, next_node_index, resting_length))
                springs.append(new_spring)
                spring_index = spring_index + 1

    return (springs, spring_index)



def make_primary_frame(nodes, springs, node_index, spring_index, params):

    '''
    We need to draw a decagon around the web.
    As we go round, we also need to create a node every time the decagon intersects with a radial thread 
    '''
    node_mass = params.node_mass
    num_radials = params.num_radials
    max_spiral_radius = params.max_spiral_radius
    frame_radius = params.frame_radius

    '''
    First we build the list of angles we need to add a node at. As we do this, we store:
    - Whether an angle corresponds to a frame or an radial node
    - Which node radial nodes should be connected to
    '''

    radial_angle = 0.
    radial_angle_step = 360. / num_radials
    frame_angle = 0.
    frame_angle_step = 36. 
    #Store frame nodes for when we draw the secondary frame
    frame_nodes = []
    first_node = True
    first_node_index = copy.deepcopy(node_index)

    while radial_angle < 360:

        #This node connects to a radial and is part of the frame. This means we need to connect it with two springs
        if isclose(frame_angle, radial_angle):

            #First make the node
            #Convert to cartesian co-ordinates
            theta = frame_angle
            x_pos = frame_radius * np.cos(np.deg2rad(theta))
            y_pos = frame_radius * np.sin(np.deg2rad(theta))
            z_pos = 0

            #Add the nodes
            new_node = Node(node_index, x_pos, y_pos, z_pos, frame_radius, theta, node_mass)
            nodes.append(new_node)

            #Now we need to find the correct spiral node to join to
            spiral_index = copy.deepcopy(first_node_index) - 1
            while not isclose(theta, nodes[spiral_index].theta):
                spiral_index = spiral_index - 1

            #Now we make the spring
            resting_length = resting_length = get_resting_length_from_ids(node_index, spiral_index, nodes)
            new_spring = Spring(spring_index, node_index, spiral_index, resting_length, resting_length, RADIAL_THREAD)
            springs.append(new_spring)
            spring_index = spring_index + 1

            #Now we connect it to the previous node unless it is the first node
            if first_node:
                first_node = False
            else:
                resting_length = resting_length = get_resting_length_from_ids(node_index, node_index-1, nodes)
                new_spring = Spring(spring_index, node_index, node_index-1, resting_length, resting_length, RADIAL_THREAD)
                springs.append(new_spring)
                spring_index = spring_index + 1

            frame_nodes.append(copy.deepcopy(node_index))
            node_index = node_index + 1
            frame_angle = frame_angle + frame_angle_step
            radial_angle = radial_angle + radial_angle_step

        else:
            #This node is a frame node. It connects only to the preceding node
            if radial_angle > frame_angle:

                theta = frame_angle
                x_pos = frame_radius * np.cos(np.deg2rad(theta))
                y_pos = frame_radius * np.sin(np.deg2rad(theta))
                z_pos = 0

                #Add the nodes
                new_node = Node(node_index, x_pos, y_pos, z_pos, frame_radius, theta, node_mass)
                nodes.append(new_node)

                #Now we connect to the previous node unless this is the first node
                if first_node:
                    first_node = False
                else:
                    resting_length = resting_length = get_resting_length_from_ids(node_index, node_index-1, nodes)
                    new_spring = Spring(spring_index, node_index, node_index-1, resting_length, resting_length, RADIAL_THREAD)
                    springs.append(new_spring)
                    spring_index = spring_index + 1

                frame_nodes.append(copy.deepcopy(node_index))
                node_index = node_index + 1
                frame_angle = frame_angle + frame_angle_step

            else:
                #This node is due to the intersection with a radial thread

                theta = radial_angle

                '''
                We can calculate the intersection radius using some geometry. This is relatively simple to understand visually, but a little tricky
                in text. Briefly, a decagon has an interior angle of 36 degrees, which means we can inscribe it with 10 triangles, each with interior angle of 36
                and other angles of 72 degrees. Our intersection point is a second triangle with an interior angle given by the difference between the frame and radial angles
                We can then use the sine law to calculate the intersection radius
                '''
                #Interior angle of the triangle made by the intersection radius and one of the inscribed angles
                alpha = frame_angle  - radial_angle
                #Sine law. 72 and 108 due to the decagon geometry
                intersection_radius = frame_radius * np.sin(np.deg2rad(72)) / (np.sin(np.deg2rad(108 - alpha)))

                x_pos = intersection_radius * np.cos(np.deg2rad(theta))
                y_pos = intersection_radius * np.sin(np.deg2rad(theta))
                z_pos = 0

                #Add the nodes
                new_node = Node(node_index, x_pos, y_pos, z_pos, frame_radius, theta, node_mass)
                nodes.append(new_node)

                #Now we need to find the correct spiral node to join to
                spiral_index = copy.deepcopy(first_node_index)
                while not isclose(theta, nodes[spiral_index].theta):
                    spiral_index = spiral_index - 1

                #Now we make the spring
                resting_length = resting_length = get_resting_length_from_ids(node_index, spiral_index, nodes)
                new_spring = Spring(spring_index, node_index, spiral_index, resting_length, resting_length, RADIAL_THREAD)
                springs.append(new_spring)
                spring_index = spring_index + 1

                #Now we connect it to the previous node unless it is the first node
                if first_node:
                    first_node = False
                else:
                    resting_length = resting_length = get_resting_length_from_ids(node_index, node_index-1, nodes)
                    new_spring = Spring(spring_index, node_index, node_index-1, resting_length, resting_length, RADIAL_THREAD)
                    springs.append(new_spring)
                    spring_index = spring_index + 1


                node_index = node_index + 1
                radial_angle = radial_angle + radial_angle_step

    #If we have less than 10 radials, we might miss some frame nodes. This final loop will add any we missed
    while frame_angle < 360:
        theta = frame_angle
        x_pos = frame_radius * np.cos(np.deg2rad(theta))
        y_pos = frame_radius * np.sin(np.deg2rad(theta))
        z_pos = 0

        #Add the nodes
        new_node = Node(node_index, x_pos, y_pos, z_pos, frame_radius, theta, node_mass)
        nodes.append(new_node)

        #Now we connect to the previous node 
        resting_length = resting_length = get_resting_length_from_ids(node_index, node_index-1, nodes)
        new_spring = Spring(spring_index, node_index, node_index-1, resting_length, resting_length, RADIAL_THREAD)
        springs.append(new_spring)
        spring_index = spring_index + 1

        frame_nodes.append(copy.deepcopy(node_index))
        node_index = node_index + 1
        frame_angle = frame_angle + frame_angle_step


    #We need to add a final spring connecting the first node to the last node
    resting_length = resting_length = get_resting_length_from_ids(first_node_index, node_index-1, nodes)
    new_spring = Spring(spring_index, first_node_index, node_index-1, resting_length, resting_length, RADIAL_THREAD)
    springs.append(new_spring)
    spring_index = spring_index + 1

    return (nodes, springs, node_index, spring_index, frame_nodes)



def make_secondary_frame(nodes, springs, node_index, spring_index, params, frame_nodes):

    '''
    Now we need to add the secondary frame
    To do this we will step around the web in steps of 72 degrees, adding a spring connecting each new node to a pair of frame nodes
    We start at theta = 18 so the first node is placed in between the first two frame nodes
    '''

    node_mass = params.node_mass
    num_radials = params.num_radials
    max_spiral_radius = params.max_spiral_radius
    second_frame_radius = params.second_frame_radius

    theta = 18.
    theta_step = 72.
    connecting_node_index = 0

    for i in range(5):
        #Convert to cartesian co-ordinates
        x_pos = second_frame_radius * np.cos(np.deg2rad(theta))
        y_pos = second_frame_radius * np.sin(np.deg2rad(theta))
        z_pos = 0

        #Add the nodes
        new_node = Node(node_index, x_pos, y_pos, z_pos, second_frame_radius, theta, node_mass)
        nodes.append(new_node)

        #Now add the springs
        connecting_node = frame_nodes[connecting_node_index]
        resting_length = get_resting_length_from_ids(node_index, connecting_node, nodes)
        new_spring = Spring(spring_index, node_index, connecting_node, resting_length, resting_length, RADIAL_THREAD)
        springs.append(new_spring)
        spring_index = spring_index + 1

        connecting_node = frame_nodes[connecting_node_index+1]
        resting_length = get_resting_length_from_ids(node_index, connecting_node, nodes)
        new_spring = Spring(spring_index, node_index, connecting_node, resting_length, resting_length, RADIAL_THREAD)
        springs.append(new_spring)
        spring_index = spring_index + 1

        connecting_node_index = connecting_node_index + 2
        node_index = node_index + 1
        theta = theta + theta_step

    return (nodes, springs, node_index, spring_index)



def make_moorings(nodes, springs, node_index, spring_index, params):

    node_mass = params.node_mass
    num_radials = params.num_radials
    max_spiral_radius = params.max_spiral_radius
    frame_radius = params.frame_radius
    mooring_radius = params.mooring_radius

    #Now we need to add the moorings
    #This is the same as the previous nodes, just at a greater radius
    theta = 18.
    theta_step = 72.
    for i in range(5):
        #Convert to cartesian co-ordinates
        x_pos = mooring_radius * np.cos(np.deg2rad(theta))
        y_pos = mooring_radius * np.sin(np.deg2rad(theta))
        z_pos = 0

        #Add the nodes
        new_node = Node(node_index, x_pos, y_pos, z_pos, mooring_radius, theta, node_mass)
        #Set mooring nodes to be fixed
        new_node.fixed = True
        nodes.append(new_node)

        #Now add the springs
        #We need to connect this node to the node with index 5 less
        resting_length = get_resting_length_from_ids(node_index, node_index-5, nodes)
        new_spring = Spring(spring_index, node_index, node_index-5, resting_length, resting_length, RADIAL_THREAD)
        springs.append(new_spring)
        spring_index = spring_index + 1

        node_index = node_index + 1
        theta = theta + theta_step

    return (nodes, springs, node_index, spring_index)



'''
This function makes a mass-spring-damper network that represents a spiders web. 
The web consists of a central hub, a number of radial threads, a spiral, a frame, a secondary frame and some moorings. 
The web is defined in the X-Y plane. This means transverse vibrations are applied in the Z direction. 
hub_mass_ratio (float): This is the ratio between the mass of the hub node and the mass of the other nodes that make up the web
num_radials (int): This is the number of radial threads the web consists of
winding_constant (float): The spiral geometry is defined by the equation r = winding_constant * theta. 
This corresponds to an archimedian spiral with a constant separation of 2 * pi * winding_constant between turns
max_spiral_radius: This is the maximum radius of the spiral
free_zone_radius: This is the minimum radius of the spiral
'''
def make_web(params):

    hub_mass_ratio = params.hub_mass_ratio
    node_mass = params.node_mass
    num_radials = params.num_radials
    winding_constant = params.winding_constant
    max_spiral_radius = params.max_spiral_radius
    free_zone_radius = params.free_zone_radius
    frame_radius = params.frame_radius
    second_frame_radius = params.second_frame_radius
    mooring_radius = params.mooring_radius

    springs = []
    node_index = 0
    spring_index = 0

    #First make the hub at (0, 0)
    nodes = make_hub(hub_mass_ratio * node_mass)
    node_index = node_index + 1

    (nodes, springs, node_index, spring_index) = make_spiral(nodes, springs, node_index, spring_index, params)
    num_nodes = node_index - 1

    #print("The spiral consists of %d nodes" % num_nodes)

    (springs, spring_index) = make_radials(nodes, springs, spring_index, params, num_nodes)

    (nodes, springs, node_index, spring_index, frame_nodes) = make_primary_frame(nodes, springs, node_index, spring_index, params)
    (nodes, springs, node_index, spring_index) = make_secondary_frame(nodes, springs, node_index, spring_index, params, frame_nodes)
    (nodes, springs, node_index, spring_index) = make_moorings(nodes, springs, node_index, spring_index, params)

    return (nodes, springs)



#This function calculates the resting length for two nodes given their indexes and the list of nodes
def get_resting_length_from_ids(node1_index, node2_index, nodes):

    #Get nodes
    node1 = nodes[node1_index]
    node2 = nodes[node2_index]

    #Get displacements
    x_disp = node1.x - node2.x
    y_disp = node1.y - node2.y
    z_disp = node1.z - node2.z

    #Pythagoras to get length
    return np.sqrt(x_disp**2 + y_disp**2 + z_disp**2)



def animate_web2D(node_history, springs):

    fig = plt.figure()
    ax = fig.add_subplot(111)


    for (i, nodes) in enumerate(node_history):

        ax.clear()
        plot_web2D(nodes, springs, ax)
        ax.text(-25, 25, "Step: %d" % i )
        plt.pause(0.05)



#This function plots the web in 2D -- used for displaying the web during the web creation process
def plot_web2D(nodes, springs, ax=None):
    
    #For storing data about the nodes
    xs = []
    ys = []
    ids = []

    #Read data from classes into lists for plotting
    for node in nodes:

        ids.append(node.id)
        xs.append(node.x)
        ys.append(node.y)

    #Make the figure / axis if one was not passed in
    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    #Plot the node positions
    ax.scatter(xs, ys)

    #Add labels to nodes
    for (i, id_no) in enumerate(ids):
        ax.annotate(str(id_no), (xs[i], ys[i]))

    #Now we need to draw the lines representing the springs
    for spring in springs:

    #Get the nodes connected by this spring
        node1 = nodes[spring.node1]
        node2 = nodes[spring.node2]

        #Get the co-ordinates
        x1 = node1.x
        x2 = node2.x
        y1 = node1.y
        y2 = node2.y

        #Draw the connecting line
        if spring.type == SPIRAL_THREAD:
            ax.plot([x1, x2], [y1, y2], 'b')
        else:
            ax.plot([x1, x2], [y1, y2], 'r')



#This initialises the plot for the animation
def init3D(nodes, springs, txt_pos, lims, ax=None):

    #If we aren't given an axis, then make one
    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    #Turn list of nodes into lists of co-ordinates
    xs = []
    ys = []
    zs = []
    for node in nodes:
        xs.append(node.x)
        ys.append(node.y)
        zs.append(node.z)

    #Plot the nodes
    scatter = ax.scatter(xs, ys, zs)

    step_label = ax.text(txt_pos[0], txt_pos[1], txt_pos[2], "Step: %d" % 0)

    #We need to build a list of plot objects that change during the animation. Scatter is the first of these objects
    plot_obj = [scatter, step_label]

    #Now we loop over the springs, drawing a line for each
    for spring in springs:
        #Get the node IDs for this spring
        node1 = nodes[spring.node1]
        node2 = nodes[spring.node2]

        #Get the co-ordinates for this spring
        x1 = node1.x
        x2 = node2.x
        y1 = node1.y
        y2 = node2.y
        z1 = node1.z 
        z2 = node2.z 

        #Draw the connecting line
        if spring.type == SPIRAL_THREAD:
            #Spirals are blue
            line, = ax.plot([x1, x2], [y1, y2], [z1, z2], 'b')
        else:
            #Radials are red
            line, = ax.plot([x1, x2], [y1, y2], [z1, z2], 'r')

        plot_obj.append(line)

    #Set axis limits
    ax.set_xlim3d(lims[0])
    ax.set_ylim3d(lims[1])
    ax.set_zlim3d(lims[2])

    return plot_obj



def update_animation3D(i, plot_data, plot_obj, draw_nodes):

    Xs, Ys, Zs, X1s, Y1s, Z1s, X2s, Y2s, Z2s = plot_data

    if draw_nodes:
        #Scatter plot is the first plot object
        scat = plot_obj[0]
        scat._offsets3d = (Xs[i, :], Ys[i, :], Zs[i, :])

    #Label text is the second plot object
    label = plot_obj[1]
    label.set_text("Step: %d" % i)

    #Remaining plot objects are line plots
    for (j, line) in enumerate(plot_obj[2:]):
        line.set_data([X1s[i, j], X2s[i, j]], [Y1s[i, j], Y2s[i, j]])
        line.set_3d_properties([Z1s[i, j], Z2s[i, j]])

    if draw_nodes:
        #If we are updating nodes then draw them
        return plot_obj
    else:
        #If not, skip the first item. This should speed up the animation
        return plot_obj[1:]


#This function tries to determine sensible axis limits for the plot based on the plot data
def get_plot_settings(plot_data):

    (Xs, Ys, Zs, X1s, Y1s, Z1s, X2s, Y2s, Z2s) = plot_data

    x_max = np.max(Xs) * 1.05
    x_min = np.min(Xs) * 1.05

    y_max = np.max(Ys) * 1.05
    y_min = np.min(Ys) * 1.05

    z_max = np.max(Zs) * 1.05
    z_min = np.min(Zs) * 1.05

    #This is the position of the step label text
    txt_x = 0
    txt_y = y_max * 0.75
    txt_z = z_max * 0.5

    return ([txt_x, txt_y, txt_z], [[x_min, x_max], [y_min, y_max], [z_min, z_max]])



def convert_history_to_arrays(node_history, springs):

    #First turn data into numpy arrays
    #Xs, Ys, Zs are nodal positions
    Xs = []
    Ys = []
    Zs = []

    #These are for the spring end points
    X1s = []
    Y1s = []
    Z1s = []
    X2s = []
    Y2s = []
    Z2s = []

    for nodes in node_history:
        xs = []
        ys = []
        zs = []
        for node in nodes:
            xs.append(node.x)
            ys.append(node.y)
            zs.append(node.z)

        Xs.append(xs)
        Ys.append(ys)
        Zs.append(zs)

        x1s = []
        y1s = []
        z1s = []
        x2s = []
        y2s = []
        z2s = []

        for spring in springs:
            node1 = nodes[spring.node1]
            node2 = nodes[spring.node2]

            #Get the co-ordinates
            x1s.append(node1.x)
            x2s.append(node2.x)
            y1s.append(node1.y)
            y2s.append(node2.y)
            z1s.append(node1.z) 
            z2s.append(node2.z) 

        X1s.append(x1s)
        Y1s.append(y1s)
        Z1s.append(z1s)
        X2s.append(x2s)
        Y2s.append(y2s)
        Z2s.append(z2s)


    Xs = np.array(Xs)
    Ys = np.array(Ys)
    Zs = np.array(Zs)
    X1s = np.array(X1s)
    Y1s = np.array(Y1s)
    Z1s = np.array(Z1s)
    X2s = np.array(X2s)
    Y2s = np.array(Y2s)
    Z2s = np.array(Z2s)

    return (Xs, Ys, Zs, X1s, Y1s, Z1s, X2s, Y2s, Z2s)



def write_web_to_file(file_name, nodes, springs, params):

    with open(file_name, 'w') as f:

        #First write out the number of nodes
        num_nodes = len(nodes)
        f.write("Nodes\t%d\n" % num_nodes)

        #Now write each node to the file
        for node in nodes:
            f.write(node.get_string_for_writing_to_file())


        #Now write out the number of springs
        num_springs = len(springs)
        f.write("Springs\t%d\n" % num_springs)

        #Now write each node to the file
        for spring in springs:
            f.write(spring.get_string_for_writing_to_file())

        #Now write out the parameters used to create the web
        f.write("Params\n")
        f.write(params.get_string_for_writing_to_file())



def read_simulation_output(file_name):

    nodes = []
    springs = []

    history = []

    with open(file_name, 'r') as f:

        #First line should have number of nodes
        line = f.readline()
        num_nodes = int(line.split('\t')[1])

        #Next line should have number of springs
        line = f.readline()
        num_springs = int(line.split('\t')[1])

        #Next line should have timestep
        line = f.readline()
        dt = float(line.split('\t')[1])

        #Next line should have timestep
        line = f.readline()
        num_timesteps = int(line.split('\t')[1])

        #Now read data about the springs
        springs = []
        for s in range(num_springs):
            line = f.readline()
            split_line = line.split(',')
            (id_no, node1, node2) = [int(val) for val in split_line[:3]]
            (resting_length, initial_length) = [float(val) for val in split_line[3:5]]
            thread_type = int(split_line[5])
            (k1, k3, d1, d3) = [float(val) for val in split_line[6:]]
            new_spring = Spring(id_no, node1, node2, resting_length, initial_length, thread_type, k1, k3, d1, d3)
            springs.append(new_spring)

        #Now get nodal positions for each timestep
        for t in range(num_timesteps):

            nodes = []

            for i in range(num_nodes):
                line = f.readline()
                (id_no, x_pos, y_pos, z_pos, x_vel, y_vel, z_vel) =  [float(val) for val in line.split('\t')]
                #Last three arguments are 0 as radius / theta / mass don't matter for plotting
                new_node = Node(id_no, x_pos, y_pos, z_pos, 0, 0, 0)
                nodes.append(new_node)

            #Store the node list for this timestep
            history.append(copy.deepcopy(nodes))
            #Skip the blank line between timesteps
            line = f.readline()

        #Still need to read springs here

    return (history, springs)

def load_default():
    
    file_name = 'web.csv'
    params = WebParams(DEFAULT_NODE_MASS, DEFAULT_HUB_MASS_RATIO, 
        DEFAULT_NUM_RADIALS, DEFAULT_WINDING_CONSTANT, 
        DEFAULT_MAX_SPIRAL_RADIUS, DEFAULT_FREE_ZONE_RADIUS, 
        DEFAULT_FRAME_RADIUS, DEFAULT_SECOND_FRAME_RADIUS, 
        DEFAULT_MOORING_RADIUS)

    (nodes, springs) = make_web(params)
    write_web_to_file(file_name, nodes, springs, params)
    
    return (file_name, params)



def main():

    parser = argparse.ArgumentParser(description='Make a csv file describing a spiders web')
    parser.add_argument('-from_file', dest='input_file', nargs=1, help='Read parameters from a file, making a web for each line')
    parser.add_argument('-params', dest='params', nargs=10, help='Pass paramaters via command line')
    parser.add_argument('-gui', dest='use_gui', action='store_const', const=1, help='Launch GUI')
    
    input_cmd = parser.parse_args()

    if input_cmd.input_file is not None:
        print("Read from file")

    elif input_cmd.params is not None:
        print("Read from cmd line")

    elif input_cmd.use_gui is not None:
        print("Launch gui")
    else:
        print("Use default behavior")
    (file_name, params) = load_default()
    (nodes, springs) = make_web(params)
    write_web_to_file(file_name, nodes, springs, params)

    
    #(node_history, springs) = read_simulation_output('text.txt')
    
    #plot_data = convert_history_to_arrays(node_history, springs)
    #(txt_pos, lims) = get_plot_settings(plot_data)


    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ###plot_web2D(node_history[0], springs)
    #plot_obj = init3D(node_history[0], springs, txt_pos, lims, ax)
    #draw_nodes = True
    #animated_plot = animation.FuncAnimation(fig, update_animation3D, frames=2000, repeat=True, interval=5, blit=True, fargs=(plot_data, plot_obj, draw_nodes))
    ##animated_plot.save('test.mp4', fps=30, extra_args = ['-vcodec', 'libx264'])
    #plt.pause(0)
    

if __name__ == "__main__":
    main()

