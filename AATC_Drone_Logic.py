import AATC_Drone,threading,queue,math,time

def LaunchDroneLogic(FlightQueue,StatusQueue):
    Exit = False
    while not Exit:
        try:
            D = AATC_Drone.CreateDroneInterface()
            LoginSucess,Message = D.Login("ZiniDrone","Purrword")
            print(Sucess,Message)
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
                FSucess,Message,FlightData = D.GetFlight(FlightID)
                WSucess,Message,FlightWaypointsData = D.GetFlightWaypoints(FlightID)
                if not (FSucess and WSucess):
                    raise Exception("FlightData or FlightWaypointData was not sucessfully obtained")
                
                
                Flight = AATC_Drone.GetFlightObject(Message,FlightData)
                Waypoints = AATC_Drone.GetWaypointObjects(Message,FlightWaypointsData)
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
                        D.MarkComplete(Status["MarkComplete"])
        except Exception as e:
            print("Error occured",str(e))
        
def CalculateVector(Coords,TargetCoords,Speed):
    dx = TargetCoords.x- Coords.x
    dy = TargetCoords.y- Coords.y
    dz = TargetCoords.z- Coords.z
    v = math.sqrt(dx**2+dy**2+ dz**2)
    ratio = speed/v
    svx = dx*ratio  #Gets Speed vector
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
    return Coord


def PutStatus(StatusQueue,Coords,Battery,MarkComplete = False):
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
                PutStatus(StatusQueue,Cooords,Battery)
                print(Coords)
            print("Reached Start Coordinate")

            for point in Waypoints:
                while not AtWaypoint(Coords,point.Coord,xSize,ySize,zSize):
                    VectorCoord = CalculateVector(Coords,point.Coord,Speed)
                    Coords = AddCoords(Coords,VectorCoord)
                    PutStatus(StatusQueue,Cooords,Battery)
                    print(Coords)
                print("Reached Waypoint",point.WaypointNumber)
                
            while not AtWaypoint(Coords,Flight.EndCoord,xSize,ySize,zSize):
                VectorCoord = CalculateVector(Coords,Flight.EndCoord,Speed)
                Coords = AddCoords(Coords,VectorCoord)
                PutStatus(StatusQueue,Cooords,Battery)
                print(Coords)
            print("Reached End Coordinate")
            PutStatus(StatusQueue,Coords,Battery,Flight.FlightID)  # Updates Status and marks flight as complete.
            FlightQueue.task_done()

            
