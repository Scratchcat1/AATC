import AATC_Drone,threading,queue,math,time

def LaunchDroneLogic(FlightQueue,StatusQueue):
    Exit = False
    while not Exit:
        try:
            D = AATC_Drone.CreateDroneInterface()
            LoginSucess,Message = D.Login(1,"Purr")
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

                FlightID = FlightID[0][0]
                FSucess,FlightMessage,FlightData = D.GetFlight(FlightID)
                WSucess,WaypointsMessage,FlightWaypointsData = D.GetFlightWaypoints(FlightID)
                if not (FSucess and WSucess):
                    raise Exception("FlightData or FlightWaypointData was not sucessfully obtained")
                
                
                Flight = AATC_Drone.GetFlightObject(FlightMessage,FlightData)
                Waypoints = AATC_Drone.GetWaypointObjects(WaypointsMessage,FlightWaypointsData)
                FlightQueue.put((False,(Flight,Waypoints)))

                complete = False
                while not complete:    #While drone not at target location
                    while StatusQueue.empty():
                        time.sleep(0.2)
                    Status = StatusQueue.get()
                    StatusQueue.task_done()
                    D.UpdateDroneStatus(Status["Coords"],Status["Battery"])
                    if "MarkComplete" in Status:
                        complete = True
                        D.MarkFlightComplete(Status["MarkComplete"],1)
        except Exception as e:
            print("Error occured in Drone Logic",str(e))

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


def PutStatus(StatusQueue,Coords,Battery,MarkComplete = None):
    data = {"Coords":(Coords.x,Coords.y,Coords.z),"Battery":Battery}
    if MarkComplete != None:
        data["MarkComplete"] = MarkComplete
    StatusQueue.put(data)

    
def DroneHardware(FlightQueue,StatusQueue):
    
    Speed = 20
    Battery = 100
    Coords = AATC_Drone.Coordinate(0,0,0)
    xSize,ySize,zSize = 0.001,0.001,5
    
    while True:
        PutStatus(StatusQueue,Coords,Battery)
        if not FlightQueue.empty():
            data = FlightQueue.get()
            Flight,Waypoints = data[1][0],data[1][1]

            while not AtWaypoint(Coords,Flight.StartCoord,xSize,ySize,zSize):
                VectorCoord = CalculateVector(Coords,Flight.StartCoord,Speed)
                Coords = AddCoords(Coords,VectorCoord)
                PutStatus(StatusQueue,Coords,Battery)
                Coords.Print()
            print("Reached Start Coordinate")

            for point in Waypoints:
                while not AtWaypoint(Coords,point.Coord,xSize,ySize,zSize):
                    VectorCoord = CalculateVector(Coords,point.Coord,Speed)
                    Coords = AddCoords(Coords,VectorCoord)
                    PutStatus(StatusQueue,Coords,Battery)
                    Coords.Print()
                print("Reached Waypoint",point.WaypointNumber)
                
            while not AtWaypoint(Coords,Flight.EndCoord,xSize,ySize,zSize):
                VectorCoord = CalculateVector(Coords,Flight.EndCoord,Speed)
                Coords = AddCoords(Coords,VectorCoord)
                PutStatus(StatusQueue,Coords,Battery)
                Coords.Print()
            print("Reached End Coordinate")
            PutStatus(StatusQueue,Coords,Battery,Flight.FlightID)  # Updates Status and marks flight as complete.
            FlightQueue.task_done()

            
def Startup():
    FlightQueue = queue.Queue()
    StatusQueue = queue.Queue()
    HardwareThread = threading.Thread(target = DroneHardware,args = (FlightQueue,StatusQueue))
    LogicThread = threading.Thread(target = LaunchDroneLogic, args = (FlightQueue,StatusQueue))

    HardwareThread.start()
    LogicThread.start()
