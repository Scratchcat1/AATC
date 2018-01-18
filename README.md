# AATC
!!!!! WORK IN PROGRESS !!!!!  
Autonomous air traffic control system for *Drones*  
Coordinates will be in form (x,y,z) where x is across, y is (pole to pole thing) and z is altitude ABOVE GROUND. 

This will be a centralized system which *Drones*,*Users* and *Monitors* can connect to in order to autonomously fly *Drones* to a target, avoiding NoFlyZones and in the future other *Drones*. The current project target is to devise a system which provides the navigation for *Drone*s automatically, but cannot prevent collisions reliably.  
Note: Inability to preempt collisions actually may be of benifit as it removes the serialization constraint from the pathfinding (in other words, the paths of the *Drones* no longer affect each other). This means that, due to this independance, processing of flight paths can happen in parralel, VASTLY increasing scalability of the flight planner as well as reducing path finding time itself.

**Systems:**  
There are 4 components to the system : The **Server, *Drones*, *Users* and *Monitors***. Each **Drone**,**User** or **Monitor** can connect to the Server in order to obtain data, change preferences and set flights. The Server will automatically find a path for the *Drone* to follow around NoFlyZones using an A* Search.

**Drone ->** Simply a client attached to a *Drone* for example which recives a set of waypoints to follow when the a *User*(The owner) sets a flight for the *Drone*. *Drones* will have to authenticate themselves with the server to prevent hijacking of the route and other problems. This will be done by creating a *Drone* Credential table in which each DroneID has a corresponding key. In this way *Drones* can be created by a user, DroneID and Password written to a file, placed onto a storage medium eg MicroSD card and placed into a *Drone*. This password could be unqiue for each *drone* in case it is lost. Further features could include overriding of Drone information in order to enable swapping of SD cards between *Drones* (This is low priority though and will probably not be implemented).

**User ->** This can be a human or automated system. The *User* will use calls to the server to login and manage *Drones*,NoFlyZones and *Monitor* Permissions. The *User* cannot control the objects belonging to other *User*s unless they have permission to, this not only prevents security issues but isolates each process serving each *User*, allowing to concurrent writes to the database without issues. A *User* can add a *Monitor* to watch the position and paths of it's *Drone*s. Additionally a *User* can set thier flights to be visible to the public or not, as well as giving specific *Monitor*s permission to view the position and paths of the *Drones*.

***Monitor* ->** Can be seen as a watcher. A *Monitor* can view all the public flight data and all non public flight data which it has been given permission to view. This could be used to create a visulization of the current flight situation and/or provide customers a real time view on when the *Drone* will arrive at its destination.  


Note: Use ```pycryptodome``` not ```pycrypto```. ```Pycrypto``` is outdated and insecure. ```pip install pycryptodome```
Some required modules. Install using ```pip install pycryptodome prettytable mysqlclient telepot pygame```


Cython compiler settings:  
```
cython -a CAStar.pyx  
gcc -shared -pthread -fPIC -fwrapv -O3 -Wall -fno-strict-aliasing  -mcpu=cortex-a53 -mfpu=neon-vfpv4  -floop-interchange -floop-strip-mine -floop-block -floop-parallelize-all -ftree-parallelize-loops=2   -I/usr/include/python3.4 -o CAStar.so CAStar.c
```
```
cython --cplus CAStar2.pyx  
g++ -shared -pthread -fPIC -fwrapv -O3 -Wall -L /usr/include/python3.4 -lstdc++ -fno-strict-aliasing  -mcpu=cortex-a53 -mfpu=neon-vfpv4  -floop-interchange -floop-strip-mine -floop-block -floop-parallelize-all -ftree-parallelize-loops=2   -std=gnu++11 -I/usr/include/python3.4 -o CAStar2.so CAStar2.cpp
```
recvall credit belongs to: https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

HTML5 template from here : https://www.html5webtemplates.co.uk/
The Flask website design is poor, however it functions. The menu options should be moved into their own block and sorted alphabetically however how to do this is not known.
