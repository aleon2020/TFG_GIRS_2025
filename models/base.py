# Imports from libraries
import pybullet as p
import time
import pybullet_data
import math

# We connect engine with GUI
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# We set gravity (X,Y,Z)
p.setGravity(0,0, -9.8)

# We load a model (plane)
planeId = p.loadURDF("plane.urdf")

# We load new objects, with a position (x,y,z)
# and an orientation given in quaternion (C,X,Y,Z)
leftColumnId = p.loadURDF("urdf/left_column.urdf")
rightColumnId = p.loadURDF("urdf/right_column.urdf")
endEffectorId = p.loadURDF("urdf/end_effector.urdf")

# Generating 6 debugging parameters for translation and rotation
# of a scene object
tx = p.addUserDebugParameter("x_pos", 1.5, 6.5, 4)
ty = p.addUserDebugParameter("y_pos", -5, 5, 0)
tz = p.addUserDebugParameter("z_pos", 0.5, 4.5, 0.5)
rx = p.addUserDebugParameter("x_euler", 0, 2 * math.pi, math.pi)
ry = p.addUserDebugParameter("y_euler", 0, 2 * math.pi, math.pi)
rz = p.addUserDebugParameter("z_euler", 0, 2 * math.pi, math.pi)

# Main loop that executes the simulation steps
# By default, we will always use a time step of 1/240 seconds
while (1):

    # By modifying the sliders, the robot changes 
    # its position and orientation in real time
    pos_x = p.readUserDebugParameter(tx)
    pos_y = p.readUserDebugParameter(ty)
    pos_z = p.readUserDebugParameter(tz)
    rot_x = p.readUserDebugParameter(rx)
    rot_y = p.readUserDebugParameter(ry)
    rot_z = p.readUserDebugParameter(rz)

    # Euler angles in radians
    orientation = p.getQuaternionFromEuler([rot_x, rot_y, rot_z])

    # Position and orientation assignment
    p.resetBasePositionAndOrientation(endEffectorId, [pos_x, pos_y, pos_z], orientation)

    p.stepSimulation()
    time.sleep(1./240.)

p.disconnect()