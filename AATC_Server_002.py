import codecs,ast,socket,recvall,random,time
import AATC_AStar,AATC_DB, AATC_Crypto,AATC_Config,AATC_Weather,AATC_Coordinate
##from AATC_Coordinate import *

def GetTime():
    return int(time.time())

##def CoordLessThanOrEqual(Coord1,Coord2):# True if Coord1 <= Coord2
##    List1 = list(Coord1)
##    List2 = list(Coord2)
##    BoolList = []
##    for x in range(len(List1)):  #Goes through each item in the lists
##        if List1[x] <= List2[x]:   #If The Coord1[x] <= Coord2[x]
##            BoolList.append(True)
##        else:
##            BoolList.append(False)
##    return all(BoolList)

           

class ClientConnection:
    """This is the base class for Connections, all other connection objects will inherit from this object.
       Will contain all similar components i.e. send, receive

    """
    def __init__(self,Thread_Name,Thread_Queue,Connection):
        self._DB = AATC_DB.DBConnection()
        self.Create_Commands()
        self._Thread_Name = Thread_Name
        self._Thread_Queue = Thread_Queue
        self._con = Connection
        self._Crypto = AATC_Crypto.Crypter(self._con, mode = "SERVER" )
        self._ClientID = -1  #Used to identify if has logged in yet

    def Connection_Loop(self):      #Loop until exit. Checks and executes commands each loop.
        """
            Keeps looping in request for Client,
            Recived data in format (CommandString,(Arg1,Arg2...))
            Calls function in format FunctionX(ArgumentTuple)
            This is to move argument processing to the specific Section
            Drone is passed as argument on server side only for security

            Arguments may be converted from Tuple to Dict in future for clarity
        """
        self._ExitLoop = False
        while not self._ExitLoop:
            try:
                data = self.Recv()
                Command,Arguments = data[0],data[1]
                Sucess,Message,Data = self.ProcessCommand(Command,Arguments)

            except Exception as e:
                Sucess,Message,Data = False,"An Error occured"+str(e),[]
                print("Error occured with",self._Thread_Name,":",str(self._ClientID),"Error :",str(e)," Sending failure message")
            try:
                self.Send((Sucess,Message,Data))
            except Exception as e:
                print(self._Thread_Name,self._ClientID," disconnected")
                self._ExitLoop = True

            if not self._Thread_Queue.empty():
                data = Thread_Queue.get()
                Command,Arguments = data[0],data[1]
                if Command == "Exit":
                    self._ExitLoop = True
                

        self._DB.Exit()
        self._con.close()
        print("Process is exiting")

    def Send(self,data):    #Encrypt and send
        self._con.sendall(self._Crypto.Encrypt(codecs.encode(str(data))))
    def Recv(self):     #Receive and decrypt
        try:
            data = self._Crypto.Decrypt(recvall.recvall(self._con))
            data = ast.literal_eval(codecs.decode(data))
            return data
        except Exception as e:
            return ("",())#Never references a command

    def Exit(self,Arguments = None):    #Exit the program
        #self._DB.db_con.close()
        self._ExitLoop = True
        print("Process for ",self._Thread_Name,":",self._ClientID," is exiting..")
        return True,"Server process is exiting. Ok to disconnect",[]
        
    
    
class UserConnection(ClientConnection):     #Used to interface with the user clients.
    def Create_Commands(self):
        self._Non_Authenticated_Commands = {
            "Login":self.Login,
            "AddUser":self.AddUser,
            "Exit":self.Exit  }
        self._Authenticated_Commands = {
            "GetNoFlyZones":self.GetNoFlyZones,
            "AddNoFlyZone":self.AddNoFlyZone,
            "RemoveNoFlyZone":self.RemoveNoFlyZone,
            "ModifyNoFlyZoneLevel":self.ModifyNoFlyZoneLevel,

            "AddDrone":self.AddDrone,
            "RemoveDrone":self.RemoveDrone,
            "GetDroneID":self.GetDroneID,
            "GetDroneCredentials":self.GetDroneCredentials,
            "SetDroneCredentials":self.SetDroneCredentials,
            "CheckDroneOwnership":self.CheckDroneOwnership,
            "GetDroneInfo":self.GetDroneInfo,
            "GetDronesUser":self.GetDronesUser,
            "GetDronesAll":self.GetDronesAll,

            "Login":self.Login,
            "GetUserID":self.GetUserID,
            "GetUsername":self.GetUsername,
            "SetFlightVisibility":self.SetFlightVisibility,
            "SetAccountType":self.SetAccountType,
            "UserChangePassword":self.UserChangePassword,


            "GetFlightsUser":self.GetFlightsUser,
            "GetFlightsAll":self.GetFlightsAll,
            "AddFlight":self.AddFlight,
            "RemoveFlight":self.RemoveFlight,
            
            "GetFlightWaypointsUser":self.GetFlightWaypointsUser,
            "GetFlightWaypointsAll":self.GetFlightWaypointsAll,
            
            "GetMonitorID":self.GetMonitorID,
            "GetMonitorName":self.GetMonitorName,
            
            "AddMonitorPermission":self.AddMonitorPermission,
            "RemoveMonitorPermission":self.RemoveMonitorPermission,
            "ModifyMonitorPermissionData":self.ModifyMonitorPermissionDate,
            "GetMonitorPermissionUser":self.GetMonitorPermissionUser,

            "Exit":self.Exit }
    
    def ProcessCommand(self,Command,Arguments):      #Executes a command with arguments depending on login state
        if self._ClientID == -1:
            Function = self._Non_Authenticated_Commands.get(Command)
        else:
            Function = self._Authenticated_Commands.get(Command)
        if Function != None:
            Sucess,Message,Data = Function(Arguments)
        else:
            Sucess,Message,Data = False,"Command does not exist",[]
            print(self._Thread_Name,self._ClientID," tried to use unregistered command")
        return Sucess,Message,Data

            
    def Login(self,Arguments):
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message,self._ClientID = self._DB.CheckCredentials(Username,Password)
        return Sucess,Message,[]

    ########################################################
    def GetNoFlyZones(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetNoFlyZones()
        return Sucess,Message,Data

    def AddNoFlyZone(self,Arguments):
        if len(Arguments) == 3:
            Coord1,Coord2,Level = Arguments[0],Arguments[1],Arguments[2]
            Coord1,Coord2 = ast.literal_eval(Coord1),ast.literal_eval(Coord2)
            Sucess,Message = self._DB.AddNoFlyZone(Coord1,Coord2,Level,self._ClientID)
        else:
            Sucess,Message = False,"Incorrect Argument format"
        return Sucess,Message,[]

    def RemoveNoFlyZone(self,Arguments):
        ZoneID = Arguments[0]
        Sucess,Message = self._DB.RemoveNoFlyZone(self._ClientID,ZoneID)
        return Sucess,Message,[]
    
    def ModifyNoFlyZoneLevel(self,Arguments):
        ZoneID,Level = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.ModifyNoFlyZoneLevel(self._ClientID,ZoneID,Level)
        return Sucess,Message,[]


    ########################################################
    def AddDrone(self,Arguments):
        DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight = Arguments[0],Arguments[1],Arguments[2],Arguments[3],Arguments[4],Arguments[5]
        Sucess,Message = self._DB.AddDrone(self._ClientID,DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight)
        return Sucess,Message,[]
    
    def RemoveDrone(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message = self._DB.RemoveDrone(self._ClientID,DroneID)
        return Sucess,Message,[]

    def GetDroneID(self,Arguments):
        DroneName = Arguments[0]
        Sucess,Message,Data = self._DB.GetDroneID(self._ClientID,DroneName)
        return Sucess,Message,Data

    def GetDroneCredentials(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message,Data = self._DB.GetDroneCredentials(self._ClientID,DroneID)
        return Sucess,Message,Data
    
    def SetDroneCredentials(self,Arguments):
        DroneID,DronePassword = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.SetDroneCredentials(self._ClientID,DroneID,DronePassword)
        return Sucess,Message,[]

    def CheckDroneOwnership(self,Arguments):
        UserID,DroneID = Arguments[0],Arguments[1]
        Sucess,Message,Data = self._DB.CheckDroneOwnership(UserID,DroneID)
        return Sucess,Message,Data
    
    def GetDroneInfo(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message,Data = self._DB.GetDroneInfo(self._ClientID,DroneID)
        return Sucess,Message,Data
    
    def GetDronesUser(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetDronesUser(self._ClientID)
        return Sucess,Message,Data

    def GetDronesAll(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetDronesAll()
        return Sucess,Message,Data

    ########################################################
        
##    def GetUserID(self,Argument):
##    def CheckCredentials(self,Arguments):

    def GetUserID(self,Arguments):
        Username = Arguments[0]
        Sucess,Message,Data = self._DB.GetUserID(Username)
        return Sucess,Message,Data
    
    def GetUsername(self,Arguments):
        UserID = Arguments[0]
        Sucess,Message,Data = self._DB.GetUsername(UserID)
        return Sucess,Message,Data

        
    def AddUser(self,Arguments):
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.AddUser(Username,Password)
        return Sucess,Message,[]


    def SetFlightVisibility(self,Arguments):
        Value = Arguments[0]
        Sucess,Message = self._DB.SetFlightVisibility(self._ClientID,Value)
        return Sucess,Message,[]

        
    def SetAccountType(self,Arguments):
        Permission,Value = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.SetAccountType(self._ClientID,Permission,Value)
        return Sucess,Message,[]

    def UserChangePassword(self,Arguments):
        OldPassword,NewPassword = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.UserChangePassword(self._ClientID,OldPassword,NewPassword)
        return Sucess,Message,[]

    #######################################################
    
    
    def GetFlightsUser(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetFlightsUser(self._ClientID)
        return Sucess,Message,Data

    def GetFlightsAll(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetFlightsAll()
        return Sucess,Message,Data
    
    def AddFlight(self,Arguments):      #Finds the path for a flight and adds it to the database
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
            print(self._Thread_Name,":",self._ClientID,"Error in AddFlight HighPointOK assesment",e)
            return False,"A point in this set is in a restricted area or not in service area. Flight denied.",[]
            
              
        
        S_,M_,Result = self._DB.CheckDroneOwnership(self._ClientID,DroneID)
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
                xSize,ySize,zSize = graph.Get_Size()
                XOffset,YOffset,ZOffset = round(random.random()*0.5*xSize,8),round(random.random()*0.5*ySize,8),round(random.random()*0.5*zSize,8)
                CoordList = []
                for NodeID in Path:
                    Node = graph.GetNode(NodeID)
                    Coords = Node.Get_Coords()
                    Coords.Set_X( Coords.Get_X()+XOffset),  Coords.Set_Y(Coords.Get_Y()+YOffset), Coords.Set_Z(Coords.Get_Z()+ZOffset)
                    CoordList.append({"Coords":Coords})
                    
                Time = StartTime
                _,Columns,DroneData = self._DB.GetDroneInfo(self._ClientID,DroneID)
                Columns = ast.literal_eval(Columns)
                DroneData = DroneData[0]
                SpeedIndex,RangeIndex = Columns.index("DroneSpeed"),Columns.index("DroneRange")
                DroneSpeed,DroneRange = DroneData[SpeedIndex],DroneData[RangeIndex]                

                Weather_Estimator = AATC_Weather.OWM_Control()
                Estimated_Drone_Speed = Weather_Estimator.Get_Adjusted_Speed(CoordList[0]["Coords"],CoordList[-1]["Coords"],DroneSpeed,Time)
                TotalDistance = 0
                for x in range(len(CoordList)):
                    if x != 0: #If not first Coord add the difference in distance to time etc
                        Distance = AATC_Coordinate.DeltaCoordToMetres(CoordList[x]["Coords"],CoordList[x-1]["Coords"]) #Gets distance in metres
                        TotalDistance += Distance

                        if AATC_Config.ENABLE_FINE_SPEED_ESTIMATION:
                            Estimated_Drone_Speed = Weather_Estimator.Get_Adjusted_Speed(CoordList[x]["Coords"],CoordList[x-1]["Coords"],DroneSpeed,Time)
                            time.sleep(AATC_Config.OWM_SLEEP_TIME)
                        DeltaTime = Distance/Estimated_Drone_Speed
                        Time = Time + DeltaTime
                    CoordList[x]["Time"] = Time

                EndTime = Time # Time at which it would probably complete it



                #Adding Flight to Database
                _,_,FlightID = self._DB.AddFlight(self._ClientID,DroneID,HighPoints[0],HighPoints[len(HighPoints)-1],StartTime,EndTime,EndTime,TotalDistance,XOffset,YOffset,ZOffset)

                ######################
                ###################### TEMP WORKAROUND ##########
##                self._DB.cur.execute("SELECT FlightID FROM Flight WHERE DroneID = %s AND StartTime = %s",(DroneID,StartTime))
##                FlightID = self._DB.cur.fetchall()[0][0]
                ######################
                ######################
                

                Waypoints = []
                
                for WaypointNumber in range(len(CoordList)):
                    Waypoints.append((FlightID,WaypointNumber+1,str(CoordList[WaypointNumber]["Coords"]),int(CoordList[WaypointNumber]["Time"]),0))

                self._DB.AddWaypoints(self._ClientID,FlightID,Waypoints)

                return True,"['FlightID','NumberOfWaypoints','StartTime','EndTime','Distance']",[(FlightID,len(CoordList),StartTime,EndTime,TotalDistance)] #Returns data about the flight

        else:
            return False,"You do not own this drone. Flight denied",[]



                
##        #Stuff I still need to do
##        #Eg add to tempoary PrebookFlight Table
##        #User pathfinding to translate to Waypoints,Flight and remove from table
##        return Sucess,Message,[]

    def RemoveFlight(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message = self._DB.RemoveFlightWaypoints(self._ClientID,FlightID)
        Sucess,Message = self._DB.RemoveFlight(self._ClientID,FlightID)
        return Sucess,Message,[]

    #######################################################

    def GetFlightWaypointsUser(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetFlightWaypointsUser(self._ClientID)
        return Sucess,Message,Data


    def GetFlightWaypointsAll(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetFlightWaypointsAll()
        return Sucess,Message,Data

    #######################################################

    def GetMonitorID(self,Arguments):
        MonitorName = Arguments[0]
        Sucess,Message,Data = self._DB.GetMonitorID(MonitorName)
        return Sucess,Message,Data


    def GetMonitorName(self,Arguments):
        MonitorID = Arguments[0]
        Sucess,Message,Data = self._DB.GetMonitorName(MonitorID)
        return Sucess,Message,Data


    #######################################################

    def AddMonitorPermission(self,Arguments):
        MonitorID,ExpiryDate = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.AddMonitorPermission(self._ClientID,MonitorID,ExpiryDate)
        return Sucess,Message,[]

        
    def RemoveMonitorPermission(self,Arguments):
        MonitorID = Arguments[0]
        Sucess,Message = self._DB.RemoveMonitorPermission(self._ClientID,MonitorID)
        return Sucess,Message,[]

        
    def ModifyMonitorPermissionDate(self,Arguments):
        MonitorID,NewDate = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.ModifyMonitorPermissionDate(self._ClientID,MonitorID,NewDate)
        return Sucess,Message,[]

        
    def GetMonitorPermissionUser(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetMonitorPermissionUser(self._ClientID)
        return Sucess,Message,Data


    #################################################








class BotConnection(UserConnection):        #Interfaces with the bot
    def __init__(self,UserID,chat_id,packet,OutputQueue):
        self._ClientID = UserID
        self._chat_id = chat_id
        self._OutputQueue = OutputQueue
        self.Create_Commands()
        self._DB = AATC_DB.DBConnection()
        self._Thread_Name = "[BOT FOR UID "+str(self._ClientID)+"]"
        
        Command, Arguments = packet[0],packet[1]
        self.Main(Command,Arguments)

    def Main(self,Command,Arguments):   #Executes the single command passed to the routine
        try:
            Sucess,Message,Data = self.ProcessCommand(Command,Arguments)
                
        except Exception as e:
            Sucess,Message,Data = False,"An Error occured"+str(e),[]
            print("Error occured with ",self._Thread_Name,". Error :",str(e),". Sending failure message")
            
        try:
            self.Send((Sucess,Message,Data))
        except Exception as e:
            print(self._Thread_Name,"Error sending message back to chat",e)
        self._DB.Exit()
            
        

    def Send(self,data):    #Sends data back to the main bot thread
        Sucess,Message,Data = data[0],data[1],data[2]
        data = str(Sucess) +"\n" +str(Message)+ "\n" + str(Data)
        self._OutputQueue.put((data,self._chat_id))

    def Login(self,Arguments):      #Sets the new UserID for the given chat_id in the session table
        Username,Password = Arguments[0],Arguments[1]
        Sucess,Message,UserID = self._DB.CheckCredentials(Username,Password)
        self._DB.Bot_SetUserID(self.chat_id,UserID)
        return Sucess,Message,[]


##
##class WebConnection(UserConnection):  # Not part of project as such
##    def __init__(self,UserID):
##        self._ClientID = UserID
##        self._DB = AATC_DB.DBConnection()
##        self._Thread_Name = "[WEB FOR UID "+str(self._ClientID)+"]"
##        
##        
##
##    def Main(self,packet):
##        Command, Arguments = packet[0],packet[1]
##        try:
##            Sucess,Message,Data = self.ProcessCommand(Command,Arguments)
##                
##        except Exception as e:
##            Sucess,Message,Data = False,"An Error occured"+str(e),[]
##            print("Error occured with UserID:",str(self._ClientID),". Error :",str(e),". Sending failure message")
##
##
##        self._DB.Exit()
##        return Sucess,Message,Data
##        
##    def Login(self,Arguments):
##        Username,Password = Arguments[0],Arguments[1]
##        Sucess,Message,UserID = self._DB.CheckCredentials(Username,Password)
##        return Sucess,Message,UserID
##
##
##







    

class MonitorConnection(ClientConnection):      #Interfaces with a monitor
    def Create_Commands(self):
        self._Non_Authenticated_Commands = {
            "Login":self.Login,
            "AddMonitor":self.AddMonitor,
            "Exit":self.Exit }
        self._Authenticated_Commands = {
            "Login":self.Login,
            "MonitorChangePassword":self.MonitorChangePassword,
            
            "GetNoFlyZones":self.GetNoFlyZones,
            "GetDronesAll":self.GetDronesAll,

            "GetUserID":self.GetUserID,
            "GetUsername":self.GetUsername,

            "GetMonitorDrones":self.GetMonitorDrones,
            "GetMonitorFlights":self.GetMonitorFlights,
            "GetMonitorFlightWaypoints":self.GetMonitorFlightWaypoints,

            "GetMonitorID":self.GetMonitorID,
            "GetMonitorName":self.GetMonitorName,

            "RemoveMonitorPermission":self.RemoveMonitorPermission,
            "GetMonitorPermissionMonitor":self.GetMonitorPermissionMonitor,

            "GetFlightsAll":self.GetFlightsAll,
            "GetFlightWaypointsAll":self.GetFlightWaypointsAll,

            "Exit":self.Exit}
            
            
    def ProcessCommand(self,Command,Arguments): 
        if self._ClientID == -1:
            Function = self._Non_Authenticated_Commands.get(Command)
        else:
            Function = self._Authenticated_Commands.get(Command)
        if Function != None:
            Sucess,Message,Data = Function(Arguments)
        else:
            Sucess,Message,Data = False,"Command does not exist",[]
            print(self._Thread_Name,self._ClientID," tried to use unregistered command")
        return Sucess,Message,Data

    ################################
    def Login(self,Arguments):
        MonitorName,MonitorPassword = Arguments[0],Arguments[1]
        Sucess,Message,self._ClientID = self._DB.MonitorCheckCredentials(MonitorName,MonitorPassword)
        return Sucess,Message,[]

    def AddMonitor(self,Arguments):
        MonitorName,MonitorPassword = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.AddMonitor(MonitorName,MonitorPassword)
        return Sucess,Message,[]

    def MonitorChangePassword(self,Arguments):
        OldPassword,NewPassword = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.MonitorChangePassword(self._ClientID,OldPassword,NewPassword)
        return Sucess,Message,[]

    ######### No Fly Zone  ##################
    def GetNoFlyZones(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetNoFlyZones()
        return Sucess,Message,Data
    
    ####### Drones   ################

    def GetDronesAll(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetDronesAll()
        return Sucess,Message,Data

    ####### User    #################

    def GetUserID(self,Arguments):
        Username = Arguments[0]
        Sucess,Message,Data = self._DB.GetUserID(Username)
        return Sucess,Message,Data
    
    def GetUsername(self,Arguments):
        UserID = Arguments[0]
        Sucess,Message,Data = self._DB.GetUsername(UserID)
        return Sucess,Message,Data


    ###### Monitor  ################

    def GetMonitorDrones(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetMonitorDrones(self._ClientID)
        return Sucess,Message,Data

    def GetMonitorFlights(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetMonitorFlights(self._ClientID)
        return Sucess,Message,Data

    def GetMonitorFlightWaypoints(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetMonitorFlightWaypoints(self._ClientID)
        return Sucess,Message,Data
        
    def GetMonitorID(self,Arguments):
        MonitorName = Arguments[0]
        Sucess,Message,Data = self._DB.GetMonitorID(MonitorName)
        return Sucess,Message,Data

    def GetMonitorName(self,Arguments):
        MonitorID = Arguments[0]
        Sucess,Message,Data = self._DB.GetMonitorName(MonitorID)
        return Sucess,Message,Data

    ######## Monitor Permisssion ############

    def RemoveMonitorPermission(self,Arguments):
        UserID = Arguments[0]
        Sucess,Message = self._DB.RemoveMonitorPermission(UserID,self._ClientID)
        return Sucess,Message,[]

    def GetMonitorPermissionMonitor(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetMonitorPermissionMonitor(self._ClientID)
        return Sucess,Message,Data

    ###################################################
    def GetFlightsAll(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetFlightsAll()
        return Sucess,Message,Data
    
    def GetFlightWaypointsAll(self,Arguments = None):
        Sucess,Message,Data = self._DB.GetFlightWaypointsAll()
        return Sucess,Message,Data

    #############################################






class DroneConnection(ClientConnection):        #Interfaces with drones
    def Create_Commands(self):
        self._Non_Authenticated_Commands = {
            "Login":self.Login,
            "Exit":self.Exit  }
        self._Authenticated_Commands = {
            "UpdateDroneStatus":self.UpdateDroneStatus,
            "DroneGetDroneInfo":self.DroneGetDroneInfo,
            "CheckForFlight":self.CheckForFlight,
            "GetFlight":self.GetFlight,
            "GetFlightWaypoints":self.GetFlightWaypoints,
            "MarkFlightComplete":self.MarkFlightComplete,
            "Exit":self.Exit }

    def ProcessCommand(self,Command,Arguments):      #Executes a command with arguments depending on login state
        if self._ClientID == -1:
            Function = self._Non_Authenticated_Commands.get(Command)
        else:
            Function = self._Authenticated_Commands.get(Command)
        if Function != None:
            Sucess,Message,Data = Function(Arguments)
        else:
            Sucess,Message,Data = False,"Command does not exist",[]
            print(self._Thread_Name,self._ClientID," tried to use unregistered command")
        return Sucess,Message,Data

 

    def Login(self,Arguments):
        DroneID,DronePassword = Arguments[0],Arguments[1]
        Sucess,Message,self._ClientID = self._DB.DroneCheckCredentials(DroneID,DronePassword)
        return Sucess,Message,[]

    ########################################################

    def UpdateDroneStatus(self,Arguments):
        LastCoords,LastBattery = AATC_Coordinate.Coordinate(*Arguments[0]),Arguments[1]
        Sucess,Message = self._DB.UpdateDroneStatus(self._ClientID,LastCoords,LastBattery)
        return Sucess,Message,[]

    ########################################################

    def DroneGetDroneInfo(self,Arguments = None):
        Sucess,Message,Data = self._DB.DroneGetDroneInfo(self._ClientID)
        return Sucess,Message,Data
    
    ##########################################################

    def CheckForFlight(self,Arguments):
        MaxLookAheadTime = Arguments[0] # How many seconds until flight start should the search allow. Would lead to the drone being locked into that flight most likely.
        Sucess,Message,Data = self._DB.CheckForFlight(self._ClientID,MaxLookAheadTime)
        return Sucess,Message,Data 

    def GetFlight(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message,Data = self._DB.GetFlight(self._ClientID,FlightID)
        return Sucess,Message,Data

    def GetFlightWaypoints(self,Arguments):
        FlightID = Arguments[0]
        Sucess,Message,Data = self._DB.GetFlightWaypoints(self._ClientID,FlightID)
        return Sucess,Message,Data

    def MarkFlightComplete(self,Arguments):
        FlightID,Code = Arguments[0],Arguments[1]
        Sucess,Message = self._DB.MarkFlightComplete(self._ClientID,FlightID,Code)
        return Sucess,Message,[]

    ######################################################






def Cleaner(Thread_Name,Thread_Queue,Interval = 36000,EndTimeThreshold = 72000):    #Ensures the database does not contain old or unneeded data by removing old items.
    Exit = False
    while not Exit:
        try:
            DB = AATC_DB.DBConnection()
            while not Exit:
                print("Cleaner starting cleaning")
                DB.CleanMonitorPermissions()    #Remove expired permissions
                
                Sucess,Message,FlightIDs = DB.GetCompletedFlightIDs(EndTimeThreshold)
                for WrappedID in FlightIDs: #Wrapped as will be in for FlightIDs = [[a,],[b,],[c,]] where letters mean flightIDs
                    DB.CleanCompletedFlightWaypoints(WrappedID[0])

                DB.CleanFlights(FlightIDs)          #Remove old flights   
                print("Cleaner completed cleaning. Sleeping..")
                time.sleep(Interval)

                if not Thread_Queue.empty():
                    data = Thread_Queue.get()
                    Command,Arguments = data[0],data[1]
                    if Command == "Exit":
                        Exit = True
            
        except Exception as e:
            print("Error in Cleaner",e)
            time.sleep(60)
    DB.Exit()
    


















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






