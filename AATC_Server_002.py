import codecs,ast,socket,recvall,os,math,random,time,pickle
import AATC_AStar,AATC_DB, AATC_Crypto
from AATC_Coordinate import *

def GetTime():
    return int(time.time())

def CoordLessThanOrEqual(Coord1,Coord2):# True if Coord1 <= Coord2
    List1 = list(Coord1)
    List2 = list(Coord2)
    BoolList = []
    for x in range(len(List1)):  #Goes through each item in the lists
        if List1[x] <= List2[x]:   #If The Coord1[x] <= Coord2[x]
            BoolList.append(True)
        else:
            BoolList.append(False)
    return all(BoolList)

           

    
    
    
class UserConnection:
    def __init__(self,Thread_Name,Thread_Queue,Connection):
        self.DB = AATC_DB.DBConnection()
        self.Thread_Name = Thread_Name
        self.Thread_Queue = Thread_Queue
        self.con = Connection
        self.Crypto = AATC_Crypto.Crypter(self.con, mode = "SERVER" )
        self.UserID = -1  #Used to identify if has logged in yet
        self.NOFLYZONE_THRESHOLD_COST = 50
        self.GRAPHFOLDERNAME = "GraphFolder"
    def Send(self,data):
        self.con.sendall(self.Crypto.Encrypt(codecs.encode(str(data))))
    def Recv(self):
        try:
            data = self.Crypto.Decrypt(recvall.recvall(self.con))
            data = ast.literal_eval(codecs.decode(data))
            #      (Command,Arguments)
            return data
            #return data[0],data[1],data[2]
        except Exception as e:
            print("UserID:",self.UserID," Socket data recive error",e)
            data = ("",())#Never references a command

    def Connection_Loop(self):
        """
            Keeps looping in request for user,
            Recived data in format (CommandString,(Arg1,Arg2...))
            Calls function in format FunctionX(ArgumentTuple)
            This is to move argument processing to the specific Section
            UserID is passed as argument on server side only for security

            Arguments may be converted from Tuple to Dict in future for clarity
        """
        Exit = False
        while not Exit:
            try:
                data = self.Recv()
                Command,Arguments = data[0],data[1]
                if self.UserID == -1:
                    if Command == "Login":
                        Sucess,Message,Data = self.Login(Arguments)
                    elif Command == "AddUser":  # If adding a new user, one must create it first, then log in seperatly
                        Sucess,Message,Data = self.AddUser(Arguments)
                    elif Command == "Exit":
                        Sucess,Message,Data = self.Exit(Arguments)
                        Exit = True
                    else:
                        Sucess,Message,Data = False,"Command does not exist",[]
                        
                else:
                    if Command == "GetNoFlyZones":
                        Sucess,Message,Data = self.GetNoFlyZones(Arguments)
                    elif Command == "AddNoFlyZone":
                        Sucess,Message,Data = self.AddNoFlyZone(Arguments)
                    elif Command == "RemoveNoFlyZone":
                        Sucess,Message,Data = self.RemoveNoFlyZone(Arguments)
                    elif Command == "ModifyNoFlyZoneLevel":
                        Sucess,Message,Data = self.ModifyNoFlyZoneLevel(Arguments)
                        
                    elif Command == "AddDrone":
                        Sucess,Message,Data = self.AddDrone(Arguments)
                    elif Command == "RemoveDrone":
                        Sucess,Message,Data = self.RemoveDrone(Arguments)
                    elif Command == "GetDroneID":
                        Sucess,Message,Data = self.GetDroneID(Arguments)
                    elif Command == "GetDroneCredentials":
                        Sucess,Message,Data = self.GetDroneCredentials(Arguments)
                    elif Command == "SetDroneCredentials":
                        Sucess,Message,Data = self.SetDroneCredentials(Arguments)
                    elif Command == "CheckDroneOwnership":
                        Sucess,Message,Data = self.CheckDroneOwnership(Arguments)
                    elif Command == "GetDroneInfo":
                        Sucess,Message,Data = self.GetDroneInfo(Arguments)
                    elif Command == "GetDronesUser":
                        Sucess,Message,Data = self.GetDronesUser(Arguments)
                    elif Command == "GetDronesAll":
                        Sucess,Message,Data = self.GetDronesAll(Arguments)

                    elif Command == "Login":   #Can then change UserID without restarting, UserID is changed as well as components on client side
                        Sucess,Message,Data = self.Login(Arguments)
                    elif Command == "GetUserID":
                        Sucess,Message,Data = self.GetUserID(Arguments)
                    elif Command == "GetUsername":
                        Sucess,Message,Data = self.GetUsername(Arguments)
                    elif Command == "SetUserPublicVisibleFlights":
                        Sucess,Message,Data = self.SetUserPublicVisibleFlights(Arguments)
                    elif Command == "SetAccountType":
                        Sucess,Message,Data = self.SetAccountType(Arguments)
                    
                    elif Command == "GetFlightsUser":
                        Sucess,Message,Data = self.GetFlightsUser(Arguments)
                    elif Command == "GetFlightsAll":
                        Sucess,Message,Data = self.GetFlightsAll(Arguments)
                    elif Command == "AddFlight":
                        Sucess,Message,Data = self.AddFlight(Arguments)
                    elif Command == "RemoveFlight":
                        Sucess,Message,Data = self.RemoveFlight(Arguments)
                    
                    elif Command == "GetFlightWaypointsUser":
                        Sucess,Message,Data = self.GetFlightWaypointsUser(Arguments)
                    elif Command == "GetFlightWaypointsAll":
                        Sucess,Message,Data = self.GetFlightWaypointsAll(Arguments)
                    
                    elif Command == "GetMonitorID":
                        Sucess,Message,Data = self.GetMonitorID(Arguments)
                    elif Command == "GetMonitorName":
                        Sucess,Message,Data = self.GetMonitorName(Arguments)
                    
                    elif Command == "AddMonitorPermission":
                        Sucess,Message,Data = self.AddMonitorPermission(Arguments)
                    elif Command == "RemoveMonitorPermission":
                        Sucess,Message,Data = self.RemoveMonitorPermission(Arguments)
                    elif Command == "ModifyMonitorPermissionDate":
                        Sucess,Message,Data = self.ModifyMonitorPermissionDate(Arguments)
                    elif Command == "GetMonitorPermissionUser":
                        Sucess,Message,Data = self.GetMonitorPermissionUser(Arguments)

                    elif Command == "Exit":
                        Sucess,Message,Data = self.Exit(Arguments)
                        Exit = True
                    #Else if command doesnt exist send back Failure
                    else:
                        Sucess,Message,Data = False,"Command does not exist",[]
                        print("User tried to use unregistered command")
                        
            except Exception as e:
                Sucess,Message,Data = False,"An Error occured"+str(e),[]
                print("Error occured with UserID:",str(self.UserID),". Error :",str(e),". Sending failure message")
                
            try:
                self.Send((Sucess,Message,Data))
            except Exception as e:
                print("UserID:",self.UserID," disconnected")
                Exit = True
                
            if not self.Thread_Queue.empty():
                data = Thread_Queue.get()
                Command,Arguments = data[0],data[1]
                if Command == "Exit":
                    Exit = True


##        
##        try:
##            Exit = False
##            while self.UserID == -1 and not Exit:#Repeats until logs in
##                data = self.Recv()
##                try:
##                    Command,Arguments = data[0],data[1]
##                    if Command == "Login":
##                        Sucess,Message,Data = self.Login(Arguments)
##                    elif Command == "AddUser":  # If adding a new user, one must create it first, then log in seperatly
##                        Sucess,Message,Data = self.AddUser(Arguments)
##                    else:
##                        Sucess,Message,Data = False,"Command does not exist",[]
##                except Exception as e:
##                    Sucess,Message,Data = False,"An Error occured"+str(e),[]
##                    print("Error occured with UserID:",str(self.UserID),"Error :",str(e)," Sending failure message")
##                self.Send((Sucess,Message,Data))
##                    
##
##            while not Exit:
##                data = self.Recv()
##                try:
##                    Command,Arguments = data[0],data[1]
##                    if Command == "GetNoFlyZones":
##                        Sucess,Message,Data = self.GetNoFlyZones(Arguments)
##                    elif Command == "AddNoFlyZone":
##                        Sucess,Message,Data = self.AddNoFlyZone(Arguments)
##                    elif Command == "RemoveNoFlyZone":
##                        Sucess,Message,Data = self.RemoveNoFlyZone(Arguments)
##                    elif Command == "ModifyNoFlyZoneLevel":
##                        Sucess,Message,Data = self.ModifyNoFlyZoneLevel(Arguments)
##                        
##                    elif Command == "AddDrone":
##                        Sucess,Message,Data = self.AddDrone(Arguments)
##                    elif Command == "RemoveDrone":
##                        Sucess,Message,Data = self.RemoveDrone(Arguments)
##                    elif Command == "GetDroneID":
##                        Sucess,Message,Data = self.GetDroneID(Arguments)
##                    elif Command == "GetDroneCredentials":
##                        Sucess,Message,Data = self.GetDroneCredentials(Arguments)
##                    elif Command == "SetDroneCredentials":
##                        Sucess,Message,Data = self.SetDroneCredentials(Arguments)
##                    elif Command == "CheckDroneOwnership":
##                        Sucess,Message,Data = self.CheckDroneOwnership(Arguments)
##                    elif Command == "GetDroneInfo":
##                        Sucess,Message,Data = self.GetDroneInfo(Arguments)
##                    elif Command == "GetDronesUser":
##                        Sucess,Message,Data = self.GetDronesUser(Arguments)
##                    elif Command == "GetDronesAll":
##                        Sucess,Message,Data = self.GetDronesAll(Arguments)
##
##                    elif Command == "Login":   #Can then change UserID without restarting, UserID is changed as well as components on client side
##                        Sucess,Message,Data = self.Login(Arguments)
##                    elif Command == "GetUserID":
##                        Sucess,Message,Data = self.GetUserID(Arguments)
##                    elif Command == "GetUsername":
##                        Sucess,Message,Data = self.GetUsername(Arguments)
##                    elif Command == "SetUserPublicVisibleFlights":
##                        Sucess,Message,Data = self.SetUserPublicVisibleFlights(Arguments)
##                    elif Command == "SetAccountType":
##                        Sucess,Message,Data = self.SetAccountType(Arguments)
##                    
##                    elif Command == "GetFlightsUser":
##                        Sucess,Message,Data = self.GetFlightsUser(Arguments)
##                    elif Command == "GetFlightsAll":
##                        Sucess,Message,Data = self.GetFlightsAll(Arguments)
##                    elif Command == "AddFlight":
##                        Sucess,Message,Data = self.AddFlight(Arguments)
##                    elif Command == "RemoveFlight":
##                        Sucess,Message,Data = self.RemoveFlight(Arguments)
##                    
##                    elif Command == "GetFlightWaypointsUser":
##                        Sucess,Message,Data = self.GetFlightWaypointsUser(Arguments)
##                    elif Command == "GetFlightWaypointsAll":
##                        Sucess,Message,Data = self.GetFlightWaypointsAll(Arguments)
##                    
##                    elif Command == "GetMonitorID":
##                        Sucess,Message,Data = self.GetMonitorID(Arguments)
##                    elif Command == "GetMonitorName":
##                        Sucess,Message,Data = self.GetMonitorName(Arguments)
##                    
##                    elif Command == "AddMonitorPermission":
##                        Sucess,Message,Data = self.AddMonitorPermission(Arguments)
##                    elif Command == "RemoveMonitorPermission":
##                        Sucess,Message,Data = self.RemoveMonitorPermission(Arguments)
##                    elif Command == "ModifyMonitorPermissionDate":
##                        Sucess,Message,Data = self.ModifyMonitorPermissionDate(Arguments)
##                    elif Command == "GetMonitorPermissionUser":
##                        Sucess,Message,Data = self.GetMonitorPermissionUser(Arguments)
##
##                    elif Command == "Exit":
##                        Sucess,Message,Data = self.Exit(Arguments)
##                        Exit = True
##                    #Else if command doesnt exist send back Failure
##                    else:
##                        Sucess,Message,Data = False,"Command does not exist",[]
##                        print("User tried to use unregistered command")
##                except Exception as e:
##                    Sucess,Message,Data = False,"An Error occured"+str(e),[]
##                    print("Error occured with UserID:",str(self.UserID),". Error :",str(e),". Sending failure message")
##                self.Send((Sucess,Message,Data))
##        except Exception as e:
##            if type(e) == BrokenPipeError:
##                print("UserID:",self.UserID," disconnected")
##            else:
##                print("Serious exception occured with UserID ",self.UserID," Error",e)
        print("Process will now exit")
            
    def Login(self,Arguments):
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message,self.UserID = self.DB.CheckCredentials(Username,Password)
        return Sucess,Message,[]

    ########################################################
    def GetNoFlyZones(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetNoFlyZones()
        return Sucess,Message,Data

    def AddNoFlyZone(self,Arguments):
        if len(Arguments) == 3:
            Coord1,Coord2,Level = Arguments[0],Arguments[1],Arguments[2]
            Coord1,Coord2 = ast.literal_eval(Coord1),ast.literal_eval(Coord2)
            Sucess,Message = self.DB.AddNoFlyZone(Coord1,Coord2,Level,self.UserID)
        else:
            Sucess,Message = False,"Incorrect Argument format"
        return Sucess,Message,[]

    def RemoveNoFlyZone(self,Arguments):
        ZoneID = Arguments[0]
        Sucess,Message = self.DB.RemoveNoFlyZone(self.UserID,ZoneID)
        return Sucess,Message,[]
    
    def ModifyNoFlyZoneLevel(self,Arguments):
        ZoneID,Level = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.ModifyNoFlyZoneLevel(self.UserID,ZoneID,Level)
        return Sucess,Message,[]


    ########################################################
    def AddDrone(self,Arguments):
        DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight = Arguments[0],Arguments[1],Arguments[2],Arguments[3],Arguments[4],Arguments[5]
        Sucess,Message = self.DB.AddDrone(self.UserID,DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight)
        return Sucess,Message,[]
    
    def RemoveDrone(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message = self.DB.RemoveDrone(self.UserID,DroneID)
        return Sucess,Message,[]

    def GetDroneID(self,Arguments):
        DroneName = Arguments[0]
        Sucess,Message,Data = self.DB.GetDroneID(self.UserID,DroneName)
        return Sucess,Message,Data

    def GetDroneCredentials(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message,Data = self.DB.GetDroneCredentials(self.UserID,DroneID)
        return Sucess,Message,Data
    
    def SetDroneCredentials(self,Arguments):
        DroneID,DronePassword = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.SetDroneCredentials(self.UserID,DroneID,DronePassword)
        return Sucess,Message,[]

    def CheckDroneOwnership(self,Arguments):
        UserID,DroneID = Arguments[0],Arguments[1]
        Sucess,Message,Data = self.DB.CheckDroneOwnership(UserID,DroneID)
        return Sucess,Message,Data
    
    def GetDroneInfo(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message,Data = self.DB.GetDroneInfo(self.UserID,DroneID)
        return Sucess,Message,Data
    
    def GetDronesUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetDronesUser(self.UserID)
        return Sucess,Message,Data

    def GetDronesAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetDronesAll()
        return Sucess,Message,Data

    ########################################################
        
##    def GetUserID(self,Argument):
##    def CheckCredentials(self,Arguments):

    def GetUserID(self,Arguments):
        Username = Arguments[0]
        Sucess,Message,Data = self.DB.GetUserID(Username)
        return Sucess,Message,Data
    
    def GetUsername(self,Arguments):
        UserID = Arguments[0]
        Sucess,Message,Data = self.DB.GetUsername(UserID)
        return Sucess,Message,Data

        
    def AddUser(self,Arguments):
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.AddUser(Username,Password)
        return Sucess,Message,[]


    def SetUserPublicVisibleFlights(self,Arguments):
        Value = Arguments[0]
        Sucess,Message = self.DB.SetUserPublicVisibleFlights(self.UserID,Value)
        return Sucess,Message,[]

        
    def SetAccountType(self,Arguments):
        Value = Arguments[0]
        Sucess,Message = self.DB.SetAccountType(self.UserID,Value)
        return Sucess,Message,[]

    #######################################################
    
    
    def GetFlightsUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightsUser(self.UserID)
        return Sucess,Message,Data

    def GetFlightsAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightsAll()
        return Sucess,Message,Data
    
    def AddFlight(self,Arguments):
        DroneID,HighPoints,StartTime = Arguments[0],Arguments[1],Arguments[2]
        if StartTime < GetTime():
            return False,"Attempting to add flight in the past",[]
        #load graph
        filename = os.path.join(os.getcwd(),self.GRAPHFOLDERNAME,"Graph.graph")
        file = open(filename,"rb")
        graph = pickle.load(file)
        file.close()
        graph.ImportGraph()

        temp = []
        for point in HighPoints:
            temp.append(ast.literal_eval(point))
        HighPoints = temp
        

        HighPointOK = []
        try:
            for point in HighPoints:  #Checks all points are not NoFlyZones
                NodeID = graph.Find_NodeID(*point)
                if graph.GetNode(NodeID).Cost > self.NOFLYZONE_THRESHOLD_COST: #If it exceeds Threshold one cannot go through here
                    HighPointOK.append(False)
                else:
                    HighPointOK.append(True)
        except Exception as e:
            print(e)
            HighPointOK.append(False)  #If out of bounds the loop will generate an exception. This will then cause the program to return.

        if not all(HighPointOK):
            return False,"A point in this set is in a restricted area or not in service area. Flight denied.",[]
              
        
        S_,M_,Result = self.DB.CheckDroneOwnership(self.UserID,DroneID)
        if Result != []:
            Start = 0
            Next = 1
            Max = len(HighPoints)
            Path = []
            Sucess = True
            while Next < Max:
                StartNodeID = graph.Find_NodeID(*HighPoints[Start])
                NextNodeID = graph.Find_NodeID(*HighPoints[Next])
                TempPath = AATC_AStar.AStar2(graph,StartNodeID,NextNodeID)
                
                if TempPath != None:
                    Path += TempPath
                    Start += 1
                    Next += 1
                else:
                    Sucess = False
                    break
            if not Sucess:
                return False,"Pathfinding was not able to find a path between the two nodes "+str([HighPoints[Start],HighPoints[Next]]),[]
            
            else:
                XOffset,YOffset,ZOffset = round(random.random()*0.5*graph.xSize,8),round(random.random()*0.5*graph.ySize,8),round(random.random()*0.5*graph.zSize,8)
                CoordList = []
                for NodeID in Path:
                    Node = graph.GetNode(NodeID)
                    Coords = Node.Coords
                    Coords.x, Coords.y, Coords.z = Coords.x+XOffset,  Coords.y+YOffset, Coords.z+ZOffset
                    CoordList.append({"Coords":Coords})
                    
                Time = StartTime
                _,Columns,DroneData = self.DB.GetDroneInfo(self.UserID,DroneID)
                Columns = ast.literal_eval(Columns)
                DroneData = DroneData[0]
                SpeedIndex,RangeIndex = Columns.index("DroneSpeed"),Columns.index("DroneRange")
                DroneSpeed,DroneRange = DroneData[SpeedIndex],DroneData[RangeIndex]                
            
                TotalDistance = 0
                for x in range(len(CoordList)):
                    if x != 0: #If not first Coord add the difference in distance to time etc
                        Distance = DeltaCoordToMetres(CoordList[x]["Coords"],CoordList[x-1]["Coords"]) #Gets distance in metres
                        TotalDistance += Distance
                        DeltaTime = Distance/DroneSpeed
                        Time = Time + DeltaTime
                    CoordList[x]["Time"] = Time

                EndTime = Time # Time at which it would probably complete it



                #Adding Flight to Database
                self.DB.AddFlight(self.UserID,DroneID,HighPoints[0],HighPoints[len(HighPoints)-1],StartTime,EndTime,EndTime,TotalDistance,XOffset,YOffset,ZOffset)

                ######################
                ###################### TEMP WORKAROUND ##########
                self.DB.cur.execute("SELECT FlightID FROM Flight WHERE DroneID = %s AND StartTime = %s",(DroneID,StartTime))
                FlightID = self.DB.cur.fetchall()[0][0]
                ######################
                ######################
                
                for WaypointNumber in range(len(CoordList)):
                    self.DB.AddWaypoint(self.UserID,FlightID,WaypointNumber+1,CoordList[WaypointNumber]["Coords"],CoordList[WaypointNumber]["Time"])

                return True,"['FlightID','NumberOfWaypoints','StartTime','EndTime','Distance']",[(FlightID,len(CoordList),StartTime,EndTime,TotalDistance)] #Returns data about the flight

        else:
            return False,"You do not own this drone. Flight denied",[]



                
        #Stuff I still need to do
        #Eg add to tempoary PrebookFlight Table
        #User pathfinding to translate to Waypoints,Flight and remove from table
        return Sucess,Message,[]

    def RemoveFlight(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message = self.DB.RemoveFlight(self.UserID,FlightID)
        return Sucess,Message,[]

    #######################################################

    def GetFlightWaypointsUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightWaypointsUser(self.UserID)
        return Sucess,Message,Data


    def GetFlightWaypointsAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightWaypointsAll()
        return Sucess,Message,Data

    #######################################################

    def GetMonitorID(self,Arguments):
        MonitorName = Arguments[0]
        Sucess,Message,Data = self.DB.GetMonitorID(MonitorName)
        return Sucess,Message,Data


    def GetMonitorName(self,Arguments):
        MonitorID = Arguments[0]
        Sucess,Message,Data = self.DB.GetMonitorName(MonitorID)
        return Sucess,Message,Data


    #######################################################

    def AddMonitorPermission(self,Arguments):
        MonitorID,ExpiryDate = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.AddMonitorPermission(self.UserID,MonitorID,ExpiryDate)
        return Sucess,Message,[]

        
    def RemoveMonitorPermission(self,Arguments):
        MonitorID = Arguments[0]
        Sucess,Message = self.DB.RemoveMonitorPermission(self.UserID,MonitorID)
        return Sucess,Message,[]

        
    def ModifyMonitorPermissionDate(self,Arguments):
        MonitorID,NewDate = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.ModifyMonitorPermissionDate(self.UserID,MonitorID,NewDate)
        return Sucess,Message,[]

        
    def GetMonitorPermissionUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorPermissionUser(self.UserID)
        return Sucess,Message,Data


    #################################################

    def Exit(self,Arguments = None):
        self.DB.db_con.close()
        print("Process for UserID:",self.UserID," is exiting..")
        return True,"Server process is exiting",[]




class MonitorConnection:
    def __init__(self,Thread_Name,Thread_Queue,Connection):
        self.DB = AATC_DB.DBConnection()
        self.Thread_Name = Thread_Name
        self.Thread_Queue = Thread_Queue
        self.con = Connection
        self.Crypto = AATC_Crypto.Crypter(self.con, mode = "SERVER")
        self.MonitorID = -1  #Used to identify if has logged in yet
    def Send(self,data):
        self.con.sendall(self.Crypto.Encrypt(codecs.encode(str(data))))
    def Recv(self):
        try:
            data = self.Crypto.Decrypt(recvall.recvall(self.con))
            data = ast.literal_eval(codecs.decode(data))
            #      (Command,Arguments)
            return data
            #return data[0],data[1],data[2]
        except Exception as e:
            print("MonitorID:",self.MonitorID," Socket data recive error")

    def Connection_Loop(self):
        """
            Keeps looping in request for Monitor,
            Recived data in format (CommandString,(Arg1,Arg2...))
            Calls function in format FunctionX(ArgumentTuple)
            This is to move argument processing to the specific Section
            Monitor is passed as argument on server side only for security

            Arguments may be converted from Tuple to Dict in future for clarity
        """
        Exit = False
        while not Exit:
            try:
                data = self.Recv()
                Command,Arguments = data[0],data[1]
                if self.MonitorID == -1:
                    if Command == "Login":
                        Sucess,Message,Data = self.Login(Arguments)
                    elif Command == "AddMonitor":  # If adding a new Monitor, one must create it first, then log in seperatly
                        Sucess,Message,Data = self.AddMonitor(Arguments)
                    elif Command == "Exit":
                        Sucess,Message,Data = self.Exit(Arguments)
                        Exit = True
                    else:
                        Sucess,Message,Data = False,"Command does not exist",[]

                else:
                    if Command == "GetNoFlyZones":
                        Sucess,Message,Data = self.GetNoFlyZones(Arguments)
                        
                    elif Command == "GetDronesAll":
                        Sucess,Message,Data = self.GetDronesAll(Arguments)
                        
                    elif Command == "GetUserID":
                        Sucess,Message,Data = self.GetUserID(Arguments)
                    elif Command == "GetUsername":
                        Sucess,Message,Data = self.GetUsername(Arguments)

                    elif Command == "GetMonitorDrones":
                        Sucess,Message,Data = self.GetMonitorDrones(Arguments)
                    elif Command == "GetMonitorFlights":
                        Sucess,Message,Data = self.GetMonitorFlights(Arguments)
                    elif Command == "GetMonitorFlightWaypoints":
                        Sucess,Message,Data = self.GetMonitorFlightWaypoints(Arguments)

                    elif Command == "GetMonitorID":
                        Sucess,Message,Data = self.GetMonitorID(Arguments)
                    elif Command == "GetMonitorName":
                        Sucess,Message,Data = self.GetMonitorName(Arguments)

                    elif Command == "RemoveMonitorPermission":
                        Sucess,Message,Data = self.RemoveMonitorPermission(Arguments)
                    elif Command == "GetMonitorPermissionMonitor":
                        Sucess,Message,Data = self.GetMonitorPermissionMonitor(Arguments)

                    elif Command == "GetFlightsAll":
                        Sucess,Message,Data = self.GetFlightsAll(Arguments)

                    elif Command == "GetFlightWaypointsAll":
                        Sucess,Message,Data = self.GetFlightWaypointsAll(Arguments)

                    elif Command == "Exit":
                        Sucess,Message,Data = self.Exit(Arguments)
                        Exit = True

                    #Else if command doesnt exist send back Failure
                    else:
                        Sucess,Message,Data = False,"Command does not exist",[]
                        print("Monitor tried to use unregistered command")
            except Exception as e:
                Sucess,Message,Data = False,"An Error occured"+str(e),[]
                print("Error occured with MonitorID:",str(self.MonitorID),"Error :",str(e)," Sending failure message")
            try:
                self.Send((Sucess,Message,Data))
            except Exception as e:
                print("MonitorID:",self.MonitorID," disconnected")
                Exit = True

            if not self.Thread_Queue.empty():
                data = Thread_Queue.get()
                Command,Arguments = data[0],data[1]
                if Command == "Exit":
                    Exit = True
                

                
##        try:
##            Exit = False
##            while self.MonitorID == -1 and not Exit:#Repeats until logs in
##                data = self.Recv()
##                try:
##                    Command,Arguments = data[0],data[1]
##                    if Command == "Login":
##                        Sucess,Message,Data = self.Login(Arguments)
##                    elif Command == "AddMonitor":  # If adding a new Monitor, one must create it first, then log in seperatly
##                        Sucess,Message,Data = self.AddMonitor(Arguments)
##                    else:
##                        Sucess,Message,Data = False,"Command does not exist",[]
##                except Exception as e:
##                    Sucess,Message,Data = False,"An Error occured"+str(e),[]
##                    print("Error occured with MonitorID:",str(self.MonitorID),"Error :",str(e)," Sending failure message")
##                self.Send((Sucess,Message,Data))
##
##                    
##            while not Exit:
##                data = self.Recv()
##                try:
##                    Command,Arguments = data[0],data[1]
##                    if Command == "GetNoFlyZones":
##                        Sucess,Message,Data = self.GetNoFlyZones(Arguments)
##                        
##                    elif Command == "GetDronesAll":
##                        Sucess,Message,Data = self.GetDronesAll(Arguments)
##                        
##                    elif Command == "GetUserID":
##                        Sucess,Message,Data = self.GetUserID(Arguments)
##                    elif Command == "GetUsername":
##                        Sucess,Message,Data = self.GetUsername(Arguments)
##
##                    elif Command == "GetMonitorDrones":
##                        Sucess,Message,Data = self.GetMonitorDrones(Arguments)
##                    elif Command == "GetMonitorFlights":
##                        Sucess,Message,Data = self.GetMonitorFlights(Arguments)
##                    elif Command == "GetMonitorFlightWaypoints":
##                        Sucess,Message,Data = self.GetMonitorFlightWaypoints(Arguments)
##
##                    elif Command == "GetMonitorID":
##                        Sucess,Message,Data = self.GetMonitorID(Arguments)
##                    elif Command == "GetMonitorName":
##                        Sucess,Message,Data = self.GetMonitorName(Arguments)
##
##                    elif Command == "RemoveMonitorPermission":
##                        Sucess,Message,Data = self.RemoveMonitorPermission(Arguments)
##                    elif Command == "GetMonitorPermissionMonitor":
##                        Sucess,Message,Data = self.GetMonitorPermissionMonitor(Arguments)
##
##                    elif Command == "GetFlightsAll":
##                        Sucess,Message,Data = self.GetFlightsAll(Arguments)
##
##                    elif Command == "GetFlightWaypointsAll":
##                        Sucess,Message,Data = self.GetFlightWaypointsAll(Arguments)
##
##                    elif Command == "Exit":
##                        Sucess,Message,Data = self.Exit(Arguments)
##                        Exit = True
##
##                    #Else if command doesnt exist send back Failure
##                    else:
##                        Sucess,Message,Data = False,"Command does not exist",[]
##                        print("Monitor tried to use unregistered command")
##                except Exception as e:
##                    Sucess,Message,Data = False,"An Error occured"+str(e),[]
##                    print("Error occured with MonitorID:",str(self.MonitorID),"Error :",str(e)," Sending failure message")
##    ##            print(Message,str(Data))
##                self.Send((Sucess,Message,Data))
##                
##        except Exception as e:
##            if type(e) == BrokenPipeError:
##                print("MonitorID:",self.MonitorID," disconnected")
##            else:
##                print("Serious exception occured with MonitorID ",self.MonitorID," Error",e)
        print("Process is exiting")

    ################################
    def Login(self,Arguments):
        MonitorName,MonitorPassword = Arguments[0],Arguments[1]
        Sucess,Message,self.MonitorID = self.DB.MonitorCheckCredentials(MonitorName,MonitorPassword)
        return Sucess,Message,[]

    ######### No Fly Zone  ##################
    def GetNoFlyZones(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetNoFlyZones()
        return Sucess,Message,Data
    
    ####### Drones   ################

    def GetDronesAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetDronesAll()
        return Sucess,Message,Data

    ####### User    #################

    def GetUserID(self,Arguments):
        Username = Arguements[0]
        Sucess,Message,Data = self.DB.GetUserID(Username)
        return Sucess,Message,Data
    
    def GetUsername(self,Arguments):
        UserID = Arguments[0]
        Sucess,Message,Data = self.DB.GetUsername(UserID)
        return Sucess,Message,Data


    ###### Monitor  ################

    def AddMonitor(self,Arguments):
        MonitorName,MonitorPassword = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.AddMonitor(MonitorName,MonitorPassword)
        return Sucess,Message,[]

    def GetMonitorDrones(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorDrones(self.MonitorID)
        return Sucess,Message,Data

    def GetMonitorFlights(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorFlights(self.MonitorID)
        return Sucess,Message,Data

    def GetMonitorFlightWaypoints(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorFlightWaypoints(self.MonitorID)
        return Sucess,Message,Data
        
    def GetMonitorID(self,Arguments):
        MonitorName = Arguments[0]
        Sucess,Message,Data = self.DB.GetMonitorID(MonitorName)
        return Sucess,Message,Data

    def GetMonitorName(self,Arguments):
        MonitorID = Arguments[0]
        Sucess,Message,Data = self.DB.GetMonitorName(MonitorID)
        return Sucess,Message,Data

    ######## Monitor Permisssion ############

    def RemoveMonitorPermission(self,Arguments):
        UserID = Arguments[0]
        Sucess,Message = self.DB.RemoveMonitorPermission(UserID,self.MonitorID)
        return Sucess,Message,[]

    def GetMonitorPermissionMonitor(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorPermissionMonitor(self.MonitorID)
        return Sucess,Message,Data

    ###################################################
    def GetFlightsAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightsAll()
        return Sucess,Message,Data
    
    def GetFlightWaypointsAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightWaypointsAll()
        return Sucess,Message,Data

    #############################################

    def Exit(self,Arguments = None):
        self.DB.db_con.close()
        print("Process for MonitorID:",self.MonitorID," is exiting..")
        return True,"Server process is exiting",[]




class DroneConnection:
    def __init__(self,Thread_Name,Thread_Queue,Connection):
        self.DB = AATC_DB.DBConnection()
        self.Thread_Name = Thread_Name
        self.Thread_Queue = Thread_Queue
        self.con = Connection
        self.Crypto = AATC_Crypto.Crypter(self.con, mode = "SERVER")
        self.DroneID = -1  #Used to identify if has logged in yet
    def Send(self,data):
        self.con.sendall(self.Crypto.Encrypt(codecs.encode(str(data))))
    def Recv(self):
        try:
            data = self.Crypto.Decrypt(recvall.recvall(self.con))
            data = ast.literal_eval(codecs.decode(data))
            #      (Command,Arguments)
            return data
            #return data[0],data[1],data[2]
        except Exception as e:
            print("DroneID:",self.DroneID," Socket data recive error")
            

    def Connection_Loop(self):
        """
            Keeps looping in request for Drone,
            Recived data in format (CommandString,(Arg1,Arg2...))
            Calls function in format FunctionX(ArgumentTuple)
            This is to move argument processing to the specific Section
            Drone is passed as argument on server side only for security

            Arguments may be converted from Tuple to Dict in future for clarity
        """
        Exit = False
        while not Exit:
            try:
                data = self.Recv()
                Command,Arguments = data[0],data[1]
                if self.DroneID == -1:
                    if Command == "Login":
                        Sucess,Message,Data = self.Login(Arguments)
                    elif Command == "Exit":
                        Sucess,Message,Data = self.Exit(Arguments)
                        Exit = True
                    else:
                        Sucess,Message,Data = False,"Command does not exist",[]

                else:
                    if Command == "UpdateDroneStatus":
                        Sucess,Message,Data = self.UpdateDroneStatus(Arguments)

                    elif Command == "DroneGetDroneInfo":
                        Sucess,Message,Data = self.DroneGetDroneInfo(Arguments)
                        
                    elif Command == "CheckForFlight":
                        Sucess,Message,Data = self.CheckForFlight(Arguments)
                    elif Command == "GetFlight":
                        Sucess,Message,Data = self.GetFlight(Arguments)
                    elif Command == "GetFlightWaypoints":
                        Sucess,Message,Data = self.GetFlightWaypoints(Arguments)
                    elif Command == "MarkFlightComplete":
                        Sucess,Message,Data = self.MarkFlightComplete(Arguments)

                    elif Command == "Exit":
                        Sucess,Message,Data = self.Exit(Arguments)
                        Exit = True

                    #Else if command doesnt exist send back Failure
                    else:
                        Sucess,Message,Data = False,"Command does not exist",[]
                        print("Drone tried to use unregistered command")

            except Exception as e:
                Sucess,Message,Data = False,"An Error occured"+str(e),[]
                print("Error occured with DroneID:",str(self.DroneID),"Error :",str(e)," Sending failure message")
            try:
                self.Send((Sucess,Message,Data))
            except Exception as e:
                print("DroneID:",self.DroneID," disconnected")
                Exit = True

            if not self.Thread_Queue.empty():
                data = Thread_Queue.get()
                Command,Arguments = data[0],data[1]
                if Command == "Exit":
                    Exit = True
                
       
        
##        try:
##            Exit = False
##            while self.DroneID == -1 and not Exit:#Repeats until logs in
##                data = self.Recv()
##                try:
##                    Command,Arguments = data[0],data[1]
##                    if Command == "Login":
##                        Sucess,Message,Data = self.Login(Arguments)
##
##                    else:
##                        Sucess,Message,Data = False,"Command does not exist",[]
##                except Exception as e:
##                    Sucess,Message,Data = False,"An Error occured"+str(e),[]
##                    print("Error occured with DroneID:",str(self.DroneID),"Error :",str(e)," Sending failure message")
##                self.Send((Sucess,Message,Data))
##                    
##            
##            while not Exit:
##                data = self.Recv()
##                try:
##                    Command,Arguments = data[0],data[1]
##                    if Command == "UpdateDroneStatus":
##                        Sucess,Message,Data = self.UpdateDroneStatus(Arguments)
##
##                    elif Command == "DroneGetDroneInfo":
##                        Sucess,Message,Data = self.DroneGetDroneInfo(Arguments)
##                        
##                    elif Command == "CheckForFlight":
##                        Sucess,Message,Data = self.CheckForFlight(Arguments)
##                    elif Command == "GetFlight":
##                        Sucess,Message,Data = self.GetFlight(Arguments)
##                    elif Command == "GetFlightWaypoints":
##                        Sucess,Message,Data = self.GetFlightWaypoints(Arguments)
##                    elif Command == "MarkFlightComplete":
##                        Sucess,Message,Data = self.MarkFlightComplete(Arguments)
##
##                    elif Command == "Exit":
##                        Sucess,Message,Data = self.Exit(Arguments)
##
##                    #Else if command doesnt exist send back Failure
##                    else:
##                        Sucess,Message,Data = False,"Command does not exist",[]
##                        print("Drone tried to use unregistered command")
##                except Exception as e:
##                    if type(e) != TypeError:# if this error type occurs connection has failed and would otherwise flood console with irrelevant errors
##                        print("Error occured with DroneID:",str(self.DroneID),"Error :",str(e)," Sending failure message")
##                    Sucess,Message,Data = False,"An Error occured"+str(e),[]
##        
##                self.Send((Sucess,Message,Data))
##                
##        except Exception as e:
##            if type(e) == BrokenPipeError:
##                print("DroneID:",self.DroneID," disconnected")
##            else:
##                print("Serious exception occured with DroneID ",self.DroneID," Error",e)
        print("Process is exiting")

    def Login(self,Arguments):
        DroneID,DronePassword = Arguments[0],Arguments[1]
        Sucess,Message,self.DroneID = self.DB.DroneCheckCredentials(DroneID,DronePassword)
        return Sucess,Message,[]

    ########################################################

    def UpdateDroneStatus(self,Arguments):
        LastCoords,LastBattery = Coordinate(*Arguments[0]),Arguments[1]
        Sucess,Message = self.DB.UpdateDroneStatus(self.DroneID,LastCoords,LastBattery)
        return Sucess,Message,[]

    ########################################################

    def DroneGetDroneInfo(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message,Data = self.DB.DroneGetDroneInfo(self.DroneID)
        return Sucess,Message,Data
    
    ##########################################################

    def CheckForFlight(self,Arguments):
        MaxLookAheadTime = Arguments[0] # How many seconds until flight start should the search allow. Would lead to the drone being locked into that flight most likely.
        Sucess,Message,Data = self.DB.CheckForFlight(self.DroneID,MaxLookAheadTime)
        return Sucess,Message,Data 

    def GetFlight(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message,Data = self.DB.GetFlight(self.DroneID,FlightID)
        return Sucess,Message,Data

    def GetFlightWaypoints(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message,Data = self.DB.GetFlightWaypoints(self.DroneID,FlightID)
        return Sucess,Message,Data

    def MarkFlightComplete(self,Arguments):
        FlightID,Code = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.MarkFlightComplete(self.DroneID,FlightID,Code)
        return Sucess,Message,[]

    ######################################################

    def Exit(self,Arguments = None):
        self.DB.db_con.close()
        print("Process for DroneID:",self.DroneID," is exiting..")
        return True,"Server process is exiting",[]





def Cleaner(Thread_Name,Thread_Queue,Interval = 36000,EndTimeThreshold = 72000):
    Exit = False
    while not Exit:
        try:
            DB = AATC_DB.DBConnection()
            while not Exit:
                print("Cleaner starting cleaning")
                DB.CleanMonitorPermissions()
                
                Sucess,Message,FlightIDs = DB.GetCompletedFlightIDs(EndTimeThreshold)
                DB.CleanCompletedFlights(EndTimeThreshold)
                
                for WrappedID in FlightIDs: #Wrapped as will be in for FlightIDs = [[a,],[b,],[c,]] where letters mean flightIDs
                    DB.CleanCompletedFlightWaypoints(WrappedID[0])
                print("Cleaner completed cleaning. Sleeping..")
                time.sleep(Interval)

                if not Thread_Queue.empty():
                    data = Thread_Queue.get()
                    Command,Arguments = data[0],data[1]
                    if Command == "Exit":
                        Exit = True
            
        except Exception as e:
            print("Error in Cleaner",e)
    


















if __name__ == "__main__": #For testing purposes
    HOST = ''
    PORT = 8000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print( 'Socket created')

    try:
        s.bind((HOST, PORT))
    except:
        print("Error binding port")
        s.close()
        sys.exit()
         
    print( 'Socket bind complete')
    s.listen(10)
    print( 'Socket now listening')


    while 1:
        try:
            conn, addr = s.accept()
            print( '\nConnected with ' + addr[0] + ':' + str(addr[1]))
            UConn = MonitorConnection(conn)
            UConn.Connection_Loop()
        except Exception as e:
            print(str(e))






