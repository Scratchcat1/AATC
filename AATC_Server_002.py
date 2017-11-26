import codecs,ast,socket,recvall,os,math,random,time,pickle
import AATC_AStar,AATC_DB, AATC_Crypto,AATC_Config,AATC_Weather
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

           

class ClientConnection:
    """This is the base class for Connections, all other connection objects will inherit from this object.
       Will contain all similar components i.e. send, receive

    """
    def __init__(self,Thread_Name,Thread_Queue,Connection):
        self.DB = AATC_DB.DBConnection()
        self.Thread_Name = Thread_Name
        self.Thread_Queue = Thread_Queue
        self.con = Connection
        self.Crypto = AATC_Crypto.Crypter(self.con, mode = "SERVER" )
        self.ClientID = -1  #Used to identify if has logged in yet

    def Connection_Loop(self):
        """
            Keeps looping in request for Client,
            Recived data in format (CommandString,(Arg1,Arg2...))
            Calls function in format FunctionX(ArgumentTuple)
            This is to move argument processing to the specific Section
            Drone is passed as argument on server side only for security

            Arguments may be converted from Tuple to Dict in future for clarity
        """
        self.ExitLoop = False
        while not self.ExitLoop:
            try:
                data = self.Recv()
                Command,Arguments = data[0],data[1]
                Sucess,Message,Data = self.ProcessCommand(Command,Arguments)

            except Exception as e:
                Sucess,Message,Data = False,"An Error occured"+str(e),[]
                print("Error occured with",self.Thread_Name,":",str(self.ClientID),"Error :",str(e)," Sending failure message")
            try:
                self.Send((Sucess,Message,Data))
            except Exception as e:
                print(self.Thread_Name,self.ClientID," disconnected")
                self.ExitLoop = True

            if not self.Thread_Queue.empty():
                data = Thread_Queue.get()
                Command,Arguments = data[0],data[1]
                if Command == "Exit":
                    self.ExitLoop = True
                

        self.DB.Exit()
        self.con.close()
        print("Process is exiting")

    def Send(self,data):
        self.con.sendall(self.Crypto.Encrypt(codecs.encode(str(data))))
    def Recv(self):
        try:
            data = self.Crypto.Decrypt(recvall.recvall(self.con))
            data = ast.literal_eval(codecs.decode(data))
            return data
        except Exception as e:
            return ("",())#Never references a command

    def Exit(self,Arguments = None):
        #self.DB.db_con.close()
        print("Process for ",self.Thread_Name,":",self.ClientID," is exiting..")
        return True,"Server process is exiting. Ok to disconnect",[]
        
    
    
class UserConnection(ClientConnection):
    
    def ProcessCommand(self,Command,Arguments):
        if self.ClientID == -1:
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
            elif Command == "SetFlightVisibility":
                Sucess,Message,Data = self.SetFlightVisibility(Arguments)
            elif Command == "SetAccountType":
                Sucess,Message,Data = self.SetAccountType(Arguments)
            elif Command == "UserChangePassword":
                Sucess,Message,Data = self.UserChangePassword(Arguments)
            
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
                self.ExitLoop = True
            #Else if command doesnt exist send back Failure
            else:
                Sucess,Message,Data = False,"Command does not exist",[]
                print("User tried to use unregistered command")
        return Sucess,Message,Data
            
    def Login(self,Arguments):
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message,self.ClientID = self.DB.CheckCredentials(Username,Password)
        return Sucess,Message,[]

    ########################################################
    def GetNoFlyZones(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetNoFlyZones()
        return Sucess,Message,Data

    def AddNoFlyZone(self,Arguments):
        if len(Arguments) == 3:
            Coord1,Coord2,Level = Arguments[0],Arguments[1],Arguments[2]
            Coord1,Coord2 = ast.literal_eval(Coord1),ast.literal_eval(Coord2)
            Sucess,Message = self.DB.AddNoFlyZone(Coord1,Coord2,Level,self.ClientID)
        else:
            Sucess,Message = False,"Incorrect Argument format"
        return Sucess,Message,[]

    def RemoveNoFlyZone(self,Arguments):
        ZoneID = Arguments[0]
        Sucess,Message = self.DB.RemoveNoFlyZone(self.ClientID,ZoneID)
        return Sucess,Message,[]
    
    def ModifyNoFlyZoneLevel(self,Arguments):
        ZoneID,Level = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.ModifyNoFlyZoneLevel(self.ClientID,ZoneID,Level)
        return Sucess,Message,[]


    ########################################################
    def AddDrone(self,Arguments):
        DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight = Arguments[0],Arguments[1],Arguments[2],Arguments[3],Arguments[4],Arguments[5]
        Sucess,Message = self.DB.AddDrone(self.ClientID,DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight)
        return Sucess,Message,[]
    
    def RemoveDrone(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message = self.DB.RemoveDrone(self.ClientID,DroneID)
        return Sucess,Message,[]

    def GetDroneID(self,Arguments):
        DroneName = Arguments[0]
        Sucess,Message,Data = self.DB.GetDroneID(self.ClientID,DroneName)
        return Sucess,Message,Data

    def GetDroneCredentials(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message,Data = self.DB.GetDroneCredentials(self.ClientID,DroneID)
        return Sucess,Message,Data
    
    def SetDroneCredentials(self,Arguments):
        DroneID,DronePassword = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.SetDroneCredentials(self.ClientID,DroneID,DronePassword)
        return Sucess,Message,[]

    def CheckDroneOwnership(self,Arguments):
        UserID,DroneID = Arguments[0],Arguments[1]
        Sucess,Message,Data = self.DB.CheckDroneOwnership(UserID,DroneID)
        return Sucess,Message,Data
    
    def GetDroneInfo(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message,Data = self.DB.GetDroneInfo(self.ClientID,DroneID)
        return Sucess,Message,Data
    
    def GetDronesUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetDronesUser(self.ClientID)
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


    def SetFlightVisibility(self,Arguments):
        Value = Arguments[0]
        Sucess,Message = self.DB.SetFlightVisibility(self.ClientID,Value)
        return Sucess,Message,[]

        
    def SetAccountType(self,Arguments):
        Permission,Value = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.SetAccountType(self.ClientID,Permission,Value)
        return Sucess,Message,[]

    def UserChangePassword(self,Arguments):
        OldPassword,NewPassword = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.UserChangePassword(self.ClientID,OldPassword,NewPassword)
        return Sucess,Message,[]

    #######################################################
    
    
    def GetFlightsUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightsUser(self.ClientID)
        return Sucess,Message,Data

    def GetFlightsAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightsAll()
        return Sucess,Message,Data
    
    def AddFlight(self,Arguments):
        DroneID,HighPoints,StartTime = Arguments[0],Arguments[1],Arguments[2]
        if StartTime < GetTime():
            if StartTime <= 2678400:   #Allow starting of flights up to 1 month ahead. No need to enter very large numbers for no reason.
                StartTime += GetTime()
            else:
                return False,"Attempting to add flight in the past",[]
        #load graph
        graph = AATC_AStar.DynoGraph()
        graph.ImportGraph()

        tempHighPoints = HighPoints
        HighPoints = []
        try:
            for rawPoint in tempHighPoints:
                point = ast.literal_eval(rawPoint)
                HighPoints.append(point)
                NodeID = graph.Find_NodeID(*point)
                if graph.GetNode(NodeID).Get_Cost() > AATC_Config.NOFLYZONE_THRESHOLD_COST: #If it exceeds Threshold one cannot go through here
                    return False,"A point in this set is in a restricted area or not in service area. Flight denied.",[]

        except Exception as e:
            print(self.Thread_Name,":",self.ClientID,"Error in AddFlight HighPointOK assesment",e)
            return False,"A point in this set is in a restricted area or not in service area. Flight denied.",[]
            
              
        
        S_,M_,Result = self.DB.CheckDroneOwnership(self.ClientID,DroneID)
        if len(Result) !=0:
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
                    Coords.Set_X( Coords.Get_X()+XOffset),  Coords.Set_Y(Coords.Get_Y()+YOffset), Coords.Set_Z(Coords.Get_Z()+ZOffset)
                    CoordList.append({"Coords":Coords})
                    
                Time = StartTime
                _,Columns,DroneData = self.DB.GetDroneInfo(self.ClientID,DroneID)
                Columns = ast.literal_eval(Columns)
                DroneData = DroneData[0]
                SpeedIndex,RangeIndex = Columns.index("DroneSpeed"),Columns.index("DroneRange")
                DroneSpeed,DroneRange = DroneData[SpeedIndex],DroneData[RangeIndex]                

                Weather_Estimator = AATC_Weather.OWM_Control()
                Estimated_Drone_Speed = Weather_Estimator.Get_Ajusted_Speed(CoordList[0]["Coords"],CoordList[-1]["Coords"],DroneSpeed,Time)
                TotalDistance = 0
                for x in range(len(CoordList)):
                    if x != 0: #If not first Coord add the difference in distance to time etc
                        Distance = DeltaCoordToMetres(CoordList[x]["Coords"],CoordList[x-1]["Coords"]) #Gets distance in metres
                        TotalDistance += Distance

                        if AATC_Config.ENABLE_FINE_SPEED_ESTIMATION:
                            Estimated_Drone_Speed = Weather_Estimator.Get_Ajusted_Speed(CoordList[x]["Coords"],CoordList[x-1]["Coords"],DroneSpeed,Time)
                            time.sleep(AATC_Config.OWM_SLEEP_TIME)
                        DeltaTime = Distance/Estimated_Drone_Speed
                        Time = Time + DeltaTime
                    CoordList[x]["Time"] = Time

                EndTime = Time # Time at which it would probably complete it



                #Adding Flight to Database
                self.DB.AddFlight(self.ClientID,DroneID,HighPoints[0],HighPoints[len(HighPoints)-1],StartTime,EndTime,EndTime,TotalDistance,XOffset,YOffset,ZOffset)

                ######################
                ###################### TEMP WORKAROUND ##########
                self.DB.cur.execute("SELECT FlightID FROM Flight WHERE DroneID = %s AND StartTime = %s",(DroneID,StartTime))
                FlightID = self.DB.cur.fetchall()[0][0]
                ######################
                ######################

                Waypoints = []
                
                for WaypointNumber in range(len(CoordList)):
                    Waypoints.append((FlightID,WaypointNumber+1,str(CoordList[WaypointNumber]["Coords"]),int(CoordList[WaypointNumber]["Time"]),0))

                self.DB.AddWaypoints(self.ClientID,FlightID,Waypoints)

                return True,"['FlightID','NumberOfWaypoints','StartTime','EndTime','Distance']",[(FlightID,len(CoordList),StartTime,EndTime,TotalDistance)] #Returns data about the flight

        else:
            return False,"You do not own this drone. Flight denied",[]



                
        #Stuff I still need to do
        #Eg add to tempoary PrebookFlight Table
        #User pathfinding to translate to Waypoints,Flight and remove from table
        return Sucess,Message,[]

    def RemoveFlight(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message = self.DB.RemoveFlight(self.ClientID,FlightID)
        return Sucess,Message,[]

    #######################################################

    def GetFlightWaypointsUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightWaypointsUser(self.ClientID)
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
        Sucess,Message = self.DB.AddMonitorPermission(self.ClientID,MonitorID,ExpiryDate)
        return Sucess,Message,[]

        
    def RemoveMonitorPermission(self,Arguments):
        MonitorID = Arguments[0]
        Sucess,Message = self.DB.RemoveMonitorPermission(self.ClientID,MonitorID)
        return Sucess,Message,[]

        
    def ModifyMonitorPermissionDate(self,Arguments):
        MonitorID,NewDate = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.ModifyMonitorPermissionDate(self.ClientID,MonitorID,NewDate)
        return Sucess,Message,[]

        
    def GetMonitorPermissionUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorPermissionUser(self.ClientID)
        return Sucess,Message,Data


    #################################################








class BotConnection(UserConnection):
    def __init__(self,UserID,chat_id,packet,OutputQueue):
        self.ClientID = UserID
        self.chat_id = chat_id
        self.OutputQueue = OutputQueue
        self.DB = AATC_DB.DBConnection()
        self.Thread_Name = "[BOT FOR UID "+str(self.ClientID)+"]"
        
        Command, Arguments = packet[0],packet[1]
        self.Main(Command,Arguments)

    def Main(self,Command,Arguments):
        try:
            Sucess,Message,Data = self.ProcessCommand(Command,Arguments)
                
        except Exception as e:
            Sucess,Message,Data = False,"An Error occured"+str(e),[]
            print("Error occured with UserID:",str(self.ClientID),". Error :",str(e),". Sending failure message")
            
        try:
            self.Send((Sucess,Message,Data))
        except Exception as e:
            print("Error sending message back to chat",e)
        self.DB.Exit()
            
        

    def Send(self,data):
        Sucess,Message,Data = data[0],data[1],data[2]
        data = str(Sucess) +"\n" +str(Message)+ "\n" + str(Data)
        self.OutputQueue.put((data,self.chat_id))

    def Login(self,Arguments):
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message,UserID = self.DB.CheckCredentials(Username,Password)
        self.DB.Bot_SetUserID(self.chat_id,UserID)
        return Sucess,Message,[]



class WebConnection(UserConnection):
    def __init__(self,UserID):
        self.ClientID = UserID
        self.DB = AATC_DB.DBConnection()
        self.Thread_Name = "[WEB FOR UID "+str(self.ClientID)+"]"
        
        

    def Main(self,packet):
        Command, Arguments = packet[0],packet[1]
        try:
            Sucess,Message,Data = self.ProcessCommand(Command,Arguments)
                
        except Exception as e:
            Sucess,Message,Data = False,"An Error occured"+str(e),[]
            print("Error occured with UserID:",str(self.ClientID),". Error :",str(e),". Sending failure message")


        self.DB.Exit()
        return Sucess,Message,Data
        
    def Login(self,Arguments):
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message,UserID = self.DB.CheckCredentials(Username,Password)
        return Sucess,Message,UserID










    

class MonitorConnection(ClientConnection):
    def ProcessCommand(self,Command,Arguments):
        if self.ClientID == -1:
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
            if Command == "Login":
                Sucess,Message,Data = self.Login(Arguments)
            elif Command == "MonitorChangePassword":
                Sucess,Message,Data = self.MonitorChangePassword(Arguments)

            elif Command == "GetNoFlyZones":
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
                self.ExitLoop = True

            #Else if command doesnt exist send back Failure
            else:
                Sucess,Message,Data = False,"Command does not exist",[]
                print("Monitor tried to use unregistered command")
        return Sucess,Message,Data

    ################################
    def Login(self,Arguments):
        MonitorName,MonitorPassword = Arguments[0],Arguments[1]
        Sucess,Message,self.ClientID = self.DB.MonitorCheckCredentials(MonitorName,MonitorPassword)
        return Sucess,Message,[]

    def AddMonitor(self,Arguments):
        MonitorName,MonitorPassword = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.AddMonitor(MonitorName,MonitorPassword)
        return Sucess,Message,[]

    def MonitorChangePassword(self,Arguments):
        OldPassword,NewPassword = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.MonitorChangePassword(self.ClientID,OldPassword,NewPassword)
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
        Username = Arguments[0]
        Sucess,Message,Data = self.DB.GetUserID(Username)
        return Sucess,Message,Data
    
    def GetUsername(self,Arguments):
        UserID = Arguments[0]
        Sucess,Message,Data = self.DB.GetUsername(UserID)
        return Sucess,Message,Data


    ###### Monitor  ################

    def GetMonitorDrones(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorDrones(self.ClientID)
        return Sucess,Message,Data

    def GetMonitorFlights(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorFlights(self.ClientID)
        return Sucess,Message,Data

    def GetMonitorFlightWaypoints(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorFlightWaypoints(self.ClientID)
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
        Sucess,Message = self.DB.RemoveMonitorPermission(UserID,self.ClientID)
        return Sucess,Message,[]

    def GetMonitorPermissionMonitor(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetMonitorPermissionMonitor(self.ClientID)
        return Sucess,Message,Data

    ###################################################
    def GetFlightsAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightsAll()
        return Sucess,Message,Data
    
    def GetFlightWaypointsAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetFlightWaypointsAll()
        return Sucess,Message,Data

    #############################################






class DroneConnection(ClientConnection):

    def ProcessCommand(self,Command,Arguments):
        if self.ClientID == -1:
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
                self.ExitLoop = True

            #Else if command doesnt exist send back Failure
            else:
                Sucess,Message,Data = False,"Command does not exist",[]
                print("Drone tried to use unregistered command")
                print(Command)
        return Sucess,Message,Data

    def Login(self,Arguments):
        DroneID,DronePassword = Arguments[0],Arguments[1]
        Sucess,Message,self.ClientID = self.DB.DroneCheckCredentials(DroneID,DronePassword)
        return Sucess,Message,[]

    ########################################################

    def UpdateDroneStatus(self,Arguments):
        LastCoords,LastBattery = Coordinate(*Arguments[0]),Arguments[1]
        Sucess,Message = self.DB.UpdateDroneStatus(self.ClientID,LastCoords,LastBattery)
        return Sucess,Message,[]

    ########################################################

    def DroneGetDroneInfo(self,Arguments = None):
        Sucess,Message,Data = self.DB.DroneGetDroneInfo(self.ClientID)
        return Sucess,Message,Data
    
    ##########################################################

    def CheckForFlight(self,Arguments):
        MaxLookAheadTime = Arguments[0] # How many seconds until flight start should the search allow. Would lead to the drone being locked into that flight most likely.
        Sucess,Message,Data = self.DB.CheckForFlight(self.ClientID,MaxLookAheadTime)
        return Sucess,Message,Data 

    def GetFlight(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message,Data = self.DB.GetFlight(self.ClientID,FlightID)
        return Sucess,Message,Data

    def GetFlightWaypoints(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message,Data = self.DB.GetFlightWaypoints(self.ClientID,FlightID)
        return Sucess,Message,Data

    def MarkFlightComplete(self,Arguments):
        FlightID,Code = Arguments[0],Arguments[1]
        Sucess,Message = self.DB.MarkFlightComplete(self.ClientID,FlightID,Code)
        return Sucess,Message,[]

    ######################################################






def Cleaner(Thread_Name,Thread_Queue,Interval = 36000,EndTimeThreshold = 72000):
    Exit = False
    while not Exit:
        try:
            DB = AATC_DB.DBConnection()
            while not Exit:
                print("Cleaner starting cleaning")
                DB.CleanMonitorPermissions()
                
                Sucess,Message,FlightIDs = DB.GetCompletedFlightIDs(EndTimeThreshold)
                DB.CleanFlights(FlightIDs)
                
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
    


















##if __name__ == "__main__": #For testing purposes
##    HOST = ''
##    PORT = 8000
##
##    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
##    print( 'Socket created')
##
##    try:
##        s.bind((HOST, PORT))
##    except:
##        print("Error binding port")
##        s.close()
##        sys.exit()
##         
##    print( 'Socket bind complete')
##    s.listen(10)
##    print( 'Socket now listening')
##
##
##    while 1:
##        try:
##            conn, addr = s.accept()
##            print( '\nConnected with ' + addr[0] + ':' + str(addr[1]))
##            UConn = MonitorConnection(conn)
##            UConn.Connection_Loop()
##        except Exception as e:
##            print(str(e))






