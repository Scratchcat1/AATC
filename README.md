# AATC
!!!!! WORK IN PROGRESS !!!!!
Autonomous air traffic control system for drones  

This will be a centralized system which drones,users and monitors can connect to in order to autonomously fly drones to a target, avoiding NoFlyZones and in the future other drones. The current project target is to devise a system which provides the navigation for drones automatically, but cannot prevent collisions reliably.  
Note: Inability to preempt collisions actually may be of benifit as it removes the serialization constraint from the pathfinding (in other words, the paths of the drones no longer affect each other). This means that, due to this independance, processing of flight paths can happen in parralel, VASTLY increasing scalability of the flight planner as well as reducing path finding time itself.

Systems:  
There are 4 components to the system : The Server, drones, Users and Monitors. Each drone,User or Monitor can connect to the Server in order to obtain data, change preferences and set flights. The Server will automatically find a path for the drone to follow around NoFlyZones using an A* Search.

Drone -> Simply a client attached to a drone for example which recives a set of waypoints to follow when the a User(The owner) sets a flight for the drone

User -> This can be a human or automated system. The User will use calls to the server to login and manage drones,NoFlyZones and Monitor Permissions. The User cannot control the objects belonging to other Users unless they have permission to, this not only prevents security issues but isolates each process serving each user, allowing to concurrent writes to the database without issues. A User can add a monitor to watch the position and paths of it's drones. Additionally a User can set thier flights to be visible to the public or not, as well as giving specific Monitors permission to view the position and paths of the drones.

Monitor -> Can be seen as a watcher. A Monitor can view all the public flight data and all non public flight data which it has been given permission to view. This could be used to create a visulization of the current flight situation and/or provide customers a real time view on when the drone will arrive at its destination.
