import AATC_Drone,threading,queue,math,time

def LaunchDroneLogic(DRONEID,DRONEPASSWORD,FlightQueue,StatusQueue,SLEEP_TIME = 30):
    Exit = False
    while not Exit:
        try:
            D = AATC_Drone.CreateDroneInterface()
            LoginSucess,Message = D.Login(DRONEID,DRONEPASSWORD)
            print(LoginSucess,Message)
            if LoginSucess:
                
                
                AvailableFlight = False
                while not AvailableFlight:
                    
                    if not StatusQueue.empty():
                        Status = StatusQueue.get()
                        StatusQueue.task_done()
                        D.UpdateDroneStatus(Status["Coords"],Status["Battery"])#dfjsafkdsajdfjs
                        
                    Sucess,Message,FlightID  = D.CheckForFlight()
                    AvailableFlight = Sucess
                    time.sleep(SLEEP_TIME)  #At the end to pause to wait so that if the server is still writing waypoints it can finish.
                    

                FlightID = FlightID[0][0]
                print("Obtaining flight and drone information. FlightID :",FlightID)
                DSucess,DroneMessage,DroneData = D.DroneGetDroneInfo(DRONEID,DRONEPASSWORD)
                FSucess,FlightMessage,FlightData = D.GetFlight(FlightID)
                WSucess,WaypointsMessage,FlightWaypointsData = D.GetFlightWaypoints(FlightID)
                if not (DSucess and FSucess and WSucess):
                    raise Exception("FlightData or FlightWaypointData was not sucessfully obtained")
                
                DroneInfo = AATC_Drone.MakeDroneInfo(DroneMessage, DroneData)
                Flight = AATC_Drone.GetFlightObject(FlightMessage,FlightData)
                Waypoints = AATC_Drone.GetWaypointObjects(WaypointsMessage,FlightWaypointsData)
                FlightQueue.put((False,(DroneInfo,Flight,Waypoints)))
                
        except Exception as e:
            print("Error occured in Drone Logic",str(e))
            AvailableFlight = False

        if AvailableFlight:
            
            complete = False
            crashed = False
            while not complete:    #While drone not at target location
                try:
                    if crashed:
                        D = AATC_Drone.CreateDroneInterface()
                        LoginSucess,Message = D.Login(DRONEID,DRONEPASSWORD)
                        crashed = False
                    while StatusQueue.empty():
                        time.sleep(SLEEP_TIME)
                    Status = StatusQueue.get()
                    StatusQueue.task_done()
                    Sucess,Message = D.UpdateDroneStatus(Status["Coords"],Status["Battery"])
                    if "MarkComplete" in Status:
                        complete = True
                        print("Flight ",Status["MarkComplete"]," complete")
                        Sucess,Message = D.MarkFlightComplete(Status["MarkComplete"],1)
                        print("Sucess",Sucess,"   Message:",Message)
                    time.sleep(SLEEP_TIME)
                except Exception as e:
                    print("Error in drone logic flight stage",e)
                    crashed = True

def toRadian(x):
    return x*math.pi/180
        
def CalculateVector(Coords,TargetCoords,Speed):
    dx = TargetCoords.x- Coords.x
    dy = TargetCoords.y- Coords.y
    dz = TargetCoords.z- Coords.z


    yCircumference = 40008000
    xCircumference = 40075160
    #Converts to metres
    mdy = dy * yCircumference /360
    mdx = dx * xCircumference * math.cos(toRadian(TargetCoords.y)) /360
    
    v = math.sqrt(mdx**2+mdy**2+ dz**2)
    ratio = Speed/v
    svx = dx*ratio  #Gets Speed vectors
    svy = dy*ratio
    svz = dz*ratio
    return AATC_Drone.Coordinate(svx,svy,svz)

def AtWaypoint(Coords,WaypointCoords,xSize,ySize,zSize):
    x,y,z = False,False,False
    if abs(Coords.x-WaypointCoords.x) <= xSize:
        x = True
    if abs(Coords.y-WaypointCoords.y) <= ySize:
        y = True
    if abs(Coords.z-WaypointCoords.z) <= zSize:
        z = True
    return all([x,y,z])

def AddCoords(Coord,VectorCoord):   #Simulates the drone moving
    Coord.x += VectorCoord.x
    Coord.y += VectorCoord.y
    Coord.z += VectorCoord.z
    time.sleep(0.1)
    return Coord


def PutStatus(StatusQueue,Coords,Battery,MarkComplete = None,EmptyOverride = False):
    if StatusQueue.empty() or EmptyOverride:  #Prevents adding a thousands of items into the queue, with the sending delayed by server speed. This method will cause the reported position to lag behind by a constant amount rather than getting progressivly further behind.
        data = {"Coords":(Coords.x,Coords.y,Coords.z),"Battery":Battery}
        if MarkComplete != None:
            data["MarkComplete"] = MarkComplete
        StatusQueue.put(data)

    
def DroneHardware(FlightQueue,StatusQueue):
    Battery = 100
    Coords = AATC_Drone.Coordinate(0,0,0)
    xSize,ySize,zSize = 0.001,0.001,5
    
    while True:
        time.sleep(1)
        PutStatus(StatusQueue,Coords,Battery)
        if not FlightQueue.empty():
            data = FlightQueue.get()
            DroneInfo,Flight,Waypoints = data[1][0],data[1][1],data[1][2]


            while not AtWaypoint(Coords,Flight.StartCoord,xSize,ySize,zSize):
                VectorCoord = CalculateVector(Coords,Flight.StartCoord,DroneInfo.DroneSpeed)
                Coords = AddCoords(Coords,VectorCoord)
                PutStatus(StatusQueue,Coords,Battery)
                Coords.Print()
            print("Reached Start Coordinate")

            for point in Waypoints:
                while not AtWaypoint(Coords,point.Coord,xSize,ySize,zSize):
                    VectorCoord = CalculateVector(Coords,point.Coord,DroneInfo.DroneSpeed)
                    Coords = AddCoords(Coords,VectorCoord)
                    PutStatus(StatusQueue,Coords,Battery)
                    Coords.Print() #probably too verbose
                print("Reached Waypoint",point.WaypointNumber)
                
            while not AtWaypoint(Coords,Flight.EndCoord,xSize,ySize,zSize):
                VectorCoord = CalculateVector(Coords,Flight.EndCoord,DroneInfo.DroneSpeed)
                Coords = AddCoords(Coords,VectorCoord)
                PutStatus(StatusQueue,Coords,Battery)
                Coords.Print()
            print("Reached End Coordinate")
            PutStatus(StatusQueue,Coords,Battery,Flight.FlightID,EmptyOverride = True)  # Updates Status and marks flight as complete.
            FlightQueue.task_done()

            
def Startup(DroneID,DronePassword):
    FlightQueue = queue.Queue()
    StatusQueue = queue.Queue()
    HardwareThread = threading.Thread(target = DroneHardware,args = (FlightQueue,StatusQueue))
    LogicThread = threading.Thread(target = LaunchDroneLogic, args = (DroneID,DronePassword,FlightQueue,StatusQueue))

    HardwareThread.start()
    LogicThread.start()
