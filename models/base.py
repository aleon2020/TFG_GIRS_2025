# Imports from libraries
import pybullet as p
import time
import pybullet_data

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

while (1):
    p.stepSimulation()
    time.sleep(1./240.)