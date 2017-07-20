# AATC
!!!!! WORK IN PROGRESS !!!!!
Autonomous air traffic control system for *Drones*  

This will be a centralized system which *Drones*,*Users* and *Monitors* can connect to in order to autonomously fly *Drones* to a target, avoiding NoFlyZones and in the future other *Drones*. The current project target is to devise a system which provides the navigation for *Drone*s automatically, but cannot prevent collisions reliably.  
Note: Inability to preempt collisions actually may be of benifit as it removes the serialization constraint from the pathfinding (in other words, the paths of the *Drones* no longer affect each other). This means that, due to this independance, processing of flight paths can happen in parralel, VASTLY increasing scalability of the flight planner as well as reducing path finding time itself.

**Systems:**  
There are 4 components to the system : The **Server, *Drones*, *Users* and *Monitors****. Each **Drone**,**User** or **Monitor** can connect to the Server in order to obtain data, change preferences and set flights. The Server will automatically find a path for the *Drone* to follow around NoFlyZones using an A* Search.

**Drone ->** Simply a client attached to a *Drone* for example which recives a set of waypoints to follow when the a *User*(The owner) sets a flight for the *Drone*

**User ->** This can be a human or automated system. The *User* will use calls to the server to login and manage *Drones*,NoFlyZones and *Monitor* Permissions. The *User* cannot control the objects belonging to other *User*s unless they have permission to, this not only prevents security issues but isolates each process serving each *User*, allowing to concurrent writes to the database without issues. A *User* can add a *Monitor* to watch the position and paths of it's *Drone*s. Additionally a *User* can set thier flights to be visible to the public or not, as well as giving specific *Monitor*s permission to view the position and paths of the *Drones*.

***Monitor* ->** Can be seen as a watcher. A *Monitor* can view all the public flight data and all non public flight data which it has been given permission to view. This could be used to create a visulization of the current flight situation and/or provide customers a real time view on when the *Drone* will arrive at its destination.

