import AATC_Drone,threading,queue,math,time,AATC_GPIO,random, AATC_Config
import AATC_Coordinate

class DroneLogicSystem:
    def __init__(self,DroneID,DronePassword,FlightQueue,StatusQueue,GPIO_Queue,Sleep_Time = 30):
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
                        print("Entering Flight Check Mode")
                        self.GPIO_Queue.put(("GREEN","Function",(AATC_GPIO.Pattern,( [(21,1,5),(21,0,1)],))))  #Let the Thread for the GREEN LED blink on pin 21 at 0.5 Hz for 1 cycle repeatedly until stopped
                        self.CheckForFlight()
                        InFlight = True
                    else:
                        print("Entering Run Flight Mode")
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
        
        self.FlightQueue.put((False,(DroneInfo,Flight,Waypoints)))

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
            
        




def GetAllFlightInfo(D,DRONEID,FlightID):    #Gets all drone flight information and packages the information into objects
    DSucess,DroneMessage,DroneData = D.DroneGetDroneInfo()
    FSucess,FlightMessage,FlightData = D.GetFlight(FlightID)
    WSucess,WaypointsMessage,FlightWaypointsData = D.GetFlightWaypoints(FlightID)
    if not (DSucess and FSucess and WSucess):
        print(DroneMessage,FlightMessage,WaypointsMessage)
        raise Exception("FlightData or FlightWaypointData was not sucessfully obtained")

    DroneInfo = AATC_Drone.MakeDroneInfo(DroneMessage, DroneData)
    Flight = AATC_Drone.GetFlightObject(FlightMessage,FlightData)
    Waypoints = AATC_Drone.GetWaypointObjects(WaypointsMessage,FlightWaypointsData)

    return DroneInfo,Flight,Waypoints



def SimulateMovement(Coord,VectorCoord,Sleep_Time = 0.1):
    Coord = AATC_Coordinate.AddCoords(Coord,VectorCoord)
    time.sleep(Sleep_Time)
    return Coord


def PutStatus(StatusQueue,Coords,Battery,MarkComplete = None,EmptyOverride = False):
    if StatusQueue.empty() or EmptyOverride:  #Prevents adding a thousands of items into the queue, with the sending delayed by server speed. This method will cause the reported position to lag behind by a constant amount rather than getting progressivly further behind.
        data = {"Coords":Coords.getTuple(),"Battery":Battery}
        if MarkComplete != None:
            data["MarkComplete"] = MarkComplete
        StatusQueue.put(data)


def DecrementBattery(DroneInfo,CoordA,CoordB,Battery):
    distance = AATC_Coordinate.DeltaCoordToMetres(CoordA,CoordB)
    decAmount = (distance/DroneInfo.Get_DroneRange())*100*(1+random.randint(-1,1)*0.1) * AATC_Config.DRONE_BATTERY_DRAIN_MULT
    Battery -= decAmount
    return Battery
    
def DroneHardware(FlightQueue,StatusQueue):
    Battery = AATC_Config.DEFAULT_DRONE_BATTERY_VALUE
    Coords = AATC_Drone.Coordinate(*AATC_Config.DEFAULT_DRONE_COORDINATE)
    xSize,ySize,zSize = AATC_Config.DEFAULT_DRONE_ATWAYPOINT_SIZES
    
    while True:
        time.sleep(1)
        PutStatus(StatusQueue,Coords,Battery)
        if not FlightQueue.empty():
            data = FlightQueue.get()
            DroneInfo,Flight,Waypoints = data[1][0],data[1][1],data[1][2]
            

            AllWaypoints = [Flight.Get_StartCoord()]+Waypoints+[Flight.Get_EndCoord()]
            
            for number,point in enumerate(AllWaypoints):
                while not AATC_Coordinate.AtWaypoint(Coords,point.Get_Coord(),xSize,ySize,zSize):
                    LastCoord = Coords.copy()
                    VectorCoord = AATC_Coordinate.CalculateVector(Coords,point.Get_Coord(),DroneInfo.DroneSpeed)
                    Coords = SimulateMovement(Coords,VectorCoord)
                    Battery = DecrementBattery(DroneInfo,Coords,LastCoord,Battery)
                    PutStatus(StatusQueue,Coords,Battery)

                if number == 0:
                    print("Reached Start Coordinate")
                elif number == len(AllWaypoints)-1:
                    print("Reached End Coordinate")
                else:
                    print("Reached Waypoint",point.Get_WaypointNumber())







##            while not AtWaypoint(Coords,Flight.StartCoord,xSize,ySize,zSize):
##                VectorCoord = AATC_Coordinate.CalculateVector(Coords,Flight.StartCoord,DroneInfo.DroneSpeed)
##                Coords = SimulateMovement(Coords,VectorCoord)
##                PutStatus(StatusQueue,Coords,Battery)
##
##            print("Reached Start Coordinate")
##            Coords.Print()
##            
##
##            for point in Waypoints:
##                while not AtWaypoint(Coords,point.Coord,xSize,ySize,zSize):
##                    VectorCoord = AATC_Coordinate.CalculateVector(Coords,point.Coord,DroneInfo.DroneSpeed)
##                    Coords = SimulateMovement(Coords,VectorCoord)
##                    PutStatus(StatusQueue,Coords,Battery)
##                    
##                print("Reached Waypoint",point.WaypointNumber)
##                Coords.Print()
##                
##                
##            while not AtWaypoint(Coords,Flight.EndCoord,xSize,ySize,zSize):
##                VectorCoord = AATC_Coordinate.CalculateVector(Coords,Flight.EndCoord,DroneInfo.DroneSpeed)
##                Coords = SimulateMovement(Coords,VectorCoord)
##                PutStatus(StatusQueue,Coords,Battery)
##
##            print("Reached End Coordinate")
##            Coords.Print()

            
            PutStatus(StatusQueue,Coords,Battery,Flight.Get_FlightID(),EmptyOverride = True)  # Updates Status and marks flight as complete.
            FlightQueue.task_done()















            
def Startup(DroneID,DronePassword):
    FlightQueue = queue.Queue()
    StatusQueue = queue.Queue()
    
    GPIO_Queue = AATC_GPIO.Create_Controller()
    for thread_name in ["GREEN","RED"]:
        GPIO_Queue.put(("Controller","Create_Thread",(thread_name,)))

    droneLogicObject = DroneLogicSystem(DroneID,DronePassword,FlightQueue,StatusQueue,GPIO_Queue)
    
    HardwareThread = threading.Thread(target = DroneHardware,args = (FlightQueue,StatusQueue))
    LogicThread = threading.Thread(target = droneLogicObject.Main)

    HardwareThread.start()
    LogicThread.start()
