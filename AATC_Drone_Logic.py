import AATC_Drone,threading,queue,math,time,AATC_GPIO


class DroneLogicSystem:
    def __init__(DroneID,DronePassword,FlightQueue,StatusQueue,GPIO_Queue,Sleep_Time = 60):
        self.DroneID = DroneID
        self.DronePassword = DronePassword
        self.FlightQueue = FlightQueue
        self.StatusQueue = StatusQueue
        self.GPIO_Queue = GPIO_Queue
        self.Sleep_Time = Sleep_Time

    def Main(self):
        Exit = False
        InFlight = False
        while not Exit:
            try:
                self.D = AATC_Drone.CreateDroneInterface()
                LoginSucess,Message = self.D.Login(self.DroneID,self.DronePassword)
                
                if LoginSucess:  
                    if not InFlight:
                        self.GPIO_Queue.put(("GREEN","Function",(AATC_GPIO.Pattern,( [(21,1,5),(21,0,1)],))))  #Let the Thread for the GREEN LED blink on pin 21 at 0.5 Hz for 1 cycle repeatedly until stopped
                        self.CheckForFlight()
                    else:
                        self.GPIO_Queue.put(("GREEN","Function",(AATC_GPIO.Blink,(21,0.5,1,True))))  #Let the Thread for the GREEN LED blink on pin 21 at 0.5 Hz for 1 cycle repeatedly until stopped
                        self.RunFlight()

                    InFlight = False #Once RunFlight has completed sucessfully go back to checking for flights. Will only complete once finished, if crashes will not pass here.

                else:
                    self.GPIO_Queue.put(("RED","Function",(AATC_GPIO.Blink,(11,1,10,False))))  #Let the Thread for RED LED blink on pin 11 at 1Hz 10 times and not repeat.
                    print("Login failure",Message)
                    time.sleep(self.Sleep_Time)  #To prevent spamming server
                    
            except Exception as e:
                print("Error occured in DroneLogic Main",e)
                self.GPIO_Queue.put(("RED","Function",(AATC_GPIO.Blink,(11,3,30,False))))  #Let the Thread for RED LED blink on pin 11 at 3Hz 30 times and not repeat.
                time.sleep(self.Sleep_Time)  #To prevent spamming server
                
            
            

    def CheckForFlight(self):
        AvailableFlight = False
        while not AvailableFlight:
            
            if not self.StatusQueue.empty():   #Updates status
                Status = self.StatusQueue.get()
                self.StatusQueue.task_done()
                self.D.UpdateDroneStatus(Status["Coords"],Status["Battery"])#dfjsafkdsajdfjs
                
            Sucess,Message,FlightID  = self.D.CheckForFlight()
            AvailableFlight = Sucess
            
            time.sleep(self.Sleep_Time)  #At the end to pause to wait so that if the server is still writing waypoints it can finish.
            

        FlightID = FlightID[0][0]   
        print("Obtaining flight and drone information. FlightID :",FlightID)
        DroneInfo, Flight, Waypoints = GetAllFlightInfo(self.D,self.DroneID,FlightID)
        
        FlightQueue.put((False,(DroneInfo,Flight,Waypoints)))

    def RunFlight(self):
        complete = False
        while not complete:    #While drone not at target location
            while self.StatusQueue.empty():
                time.sleep(self.Sleep_Time)
                
            Status = self.StatusQueue.get()
            self.StatusQueue.task_done()
            
            Sucess,Message = self.D.UpdateDroneStatus(Status["Coords"],Status["Battery"])
            if "MarkComplete" in Status:
                complete = True
                print("Flight ",Status["MarkComplete"]," complete")
                Sucess,Message = self.D.MarkFlightComplete(Status["MarkComplete"],1)
                print("Sucess",Sucess,"   Message:",Message)
            time.sleep(self.Sleep_Time)
            
        

##def LaunchDroneLogic(DRONEID,DRONEPASSWORD,FlightQueue,StatusQueue,GPIO_Queue,SLEEP_TIME = 60):
##    Exit = False
##    while not Exit:
##        try:
##            D = AATC_Drone.CreateDroneInterface()
##            LoginSucess,Message = D.Login(DRONEID,DRONEPASSWORD)
##            print(LoginSucess,Message)
##            if LoginSucess:
##                
##                AvailableFlight = False
##                while not AvailableFlight:
##                    
##                    if not StatusQueue.empty():
##                        Status = StatusQueue.get()
##                        StatusQueue.task_done()
##                        D.UpdateDroneStatus(Status["Coords"],Status["Battery"])#dfjsafkdsajdfjs
##                        
##                    Sucess,Message,FlightID  = D.CheckForFlight()
##                    AvailableFlight = Sucess
##                    time.sleep(SLEEP_TIME)  #At the end to pause to wait so that if the server is still writing waypoints it can finish.
##                    
##
##                FlightID = FlightID[0][0]
##                print("Obtaining flight and drone information. FlightID :",FlightID)
##                DroneInfo, Flight, Waypoints = GetAllFlightInfo(D,DRONEID,FlightID)
##                
##                FlightQueue.put((False,(DroneInfo,Flight,Waypoints)))
##                
##        except Exception as e:
##            print("Error occured in Drone Logic",str(e))
##            AvailableFlight = False
##
##        if AvailableFlight:
##            
##            complete = False
##            crashed = False
##            while not complete:    #While drone not at target location
##                try:
##                    if crashed:
##                        D = AATC_Drone.CreateDroneInterface()
##                        LoginSucess,Message = D.Login(DRONEID,DRONEPASSWORD)
##                        crashed = False
##                    while StatusQueue.empty():
##                        time.sleep(SLEEP_TIME)
##                    Status = StatusQueue.get()
##                    StatusQueue.task_done()
##                    Sucess,Message = D.UpdateDroneStatus(Status["Coords"],Status["Battery"])
##                    if "MarkComplete" in Status:
##                        complete = True
##                        print("Flight ",Status["MarkComplete"]," complete")
##                        Sucess,Message = D.MarkFlightComplete(Status["MarkComplete"],1)
##                        print("Sucess",Sucess,"   Message:",Message)
##                    time.sleep(SLEEP_TIME)
##                except Exception as e:
##                    print("Error in drone logic flight stage",e)
##                    crashed = True


def GetAllFlightInfo(D,DRONEID,FlightID):    #Gets all drone flight information and packages the information into objects
    DSucess,DroneMessage,DroneData = D.DroneGetDroneInfo(DRONEID)
    FSucess,FlightMessage,FlightData = D.GetFlight(FlightID)
    WSucess,WaypointsMessage,FlightWaypointsData = D.GetFlightWaypoints(FlightID)
    if not (DSucess and FSucess and WSucess):
        raise Exception("FlightData or FlightWaypointData was not sucessfully obtained")

    DroneInfo = AATC_Drone.MakeDroneInfo(DroneMessage, DroneData)
    Flight = AATC_Drone.GetFlightObject(FlightMessage,FlightData)
    Waypoints = AATC_Drone.GetWaypointObjects(WaypointsMessage,FlightWaypointsData)

    return DroneInfo,Flight,Waypoints


def AtWaypoint(Coords,WaypointCoords,xSize,ySize,zSize):
    x,y,z = False,False,False
    if abs(Coords.x-WaypointCoords.x) <= xSize:
        x = True
    if abs(Coords.y-WaypointCoords.y) <= ySize:
        y = True
    if abs(Coords.z-WaypointCoords.z) <= zSize:
        z = True
    return all([x,y,z])


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
                VectorCoord = AATC_Coordinate.CalculateVector(Coords,Flight.StartCoord,DroneInfo.DroneSpeed)
                Coords = AATC_Coordinate.AddCoords(Coords,VectorCoord)
                PutStatus(StatusQueue,Coords,Battery)

            print("Reached Start Coordinate")

            for point in Waypoints:
                while not AtWaypoint(Coords,point.Coord,xSize,ySize,zSize):
                    VectorCoord = AATC_Coordinate.CalculateVector(Coords,point.Coord,DroneInfo.DroneSpeed)
                    Coords = AATC_Coordinate.AddCoords(Coords,VectorCoord)
                    PutStatus(StatusQueue,Coords,Battery)
                    
                print("Reached Waypoint",point.WaypointNumber)
                
            while not AtWaypoint(Coords,Flight.EndCoord,xSize,ySize,zSize):
                VectorCoord = AATC_Coordinate.CalculateVector(Coords,Flight.EndCoord,DroneInfo.DroneSpeed)
                Coords = AATC_Coordinate.AddCoords(Coords,VectorCoord)
                PutStatus(StatusQueue,Coords,Battery)

            print("Reached End Coordinate")

            
            PutStatus(StatusQueue,Coords,Battery,Flight.FlightID,EmptyOverride = True)  # Updates Status and marks flight as complete.
            FlightQueue.task_done()

            
def Startup(DroneID,DronePassword):
    FlightQueue = queue.Queue()
    StatusQueue = queue.Queue()
    GPIO_Queue = AATC_GPIO.Create_Controller()

    droneLogicObject = DroneLogicSystem(DroneID,DronePassword,FlightQueue,StatusQueue,GPIO_Queue)
    
    HardwareThread = threading.Thread(target = DroneHardware,args = (FlightQueue,StatusQueue))
    LogicThread = threading.Thread(target = droneLogicObject.Main)

    HardwareThread.start()
    LogicThread.start()
