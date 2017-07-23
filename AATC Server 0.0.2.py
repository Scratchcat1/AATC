import codecs,ast,AATC_DB,socket
def GetTime():
    return int(time.time())

def CoordLessThanOrEqual(Coord1,Coord2):# True if Coord1 <= Coord2
    List1 = list(Coord1)
    List2 = list(Coord2)
    BoolList = []
    for x in range(len(List1)):  #Goes through each item in the lists
        if List1[x] <= List2[x]:   #If The Coord1[x] <= Coord2[x]
            BoolList.append(True)
    return all(BoolList)
            
        
        


class UserConnection:
    def __init__(self,Connection):
        self.DB = AATC_DB.DBConnection()
        self.con = Connection
        self.UserID = -1  #Used to identify if has logged in yet
    def Send(self,data):
        self.con.sendall(codecs.encode(str(data)))
    def Recv(self):
        try:
            data = sel.con.recv(1024)
            data = ast.literal_eval(codecs.decode(data))
            #      (Command,Arguments)
            return data
            #return data[0],data[1],data[2]
        except Exception as e:
            print("Socket data recive error")
            print(str(e))

    def Connection_Loop(self):
        """
            Keeps looping in request for user,
            Recived data in format (CommandString,(Arg1,Arg2...))
            Calls function in format FunctionX(ArgumentTuple)
            This is to move argument processing to the specific Section
            UserID is passed as argument on server side only for security

            Arguments may be converted from Tuple to Dict in future for clarity
        """
        while self.UserID == -1:#Repeats until logs in
            data = self.Recv()
            try:
                Command,Arguments = data[0],data[1]
                if Command == "Login":
                    Sucess,Message,Data = self.Login(Arguments)
                elif Command == "AddUser":  # If adding a new user, one must create it first, then log in seperatly
                    Sucess,Message,Data = self.AddUser(Arguments)
                else:
                    Sucess,Message,Data = False,"Command does not exist",[]
            except Exception as e:
                Sucess,Message,Data = False,"An Error occured"+str(e),[]
                print("Error occured with UserID:",str(self.UserID),"Error :",str(e)," Sending failure message")
            self.Send((Sucess,Message,Data))
                
        Exit = False
        while not Exit:
            data = self.Recv()
            try:
                Command,Arguments = data[0],data[1]
                if Command == "GetNoFlyZones":
                    Sucess,Message,Data = self.GetNoFlyZones(Arguments)
                elif Command == "AddNoFlyZone":
                    Sucess,Message,Data = self.GetNoFlyZones(Arguments)
                elif Command == "RemoveNoFlyZone":
                    Sucess,Message,Data = self.RemoveNoFlyZone(Arguments)
                elif Command == "ModifyNoFlyZone":
                    Sucess,Message,Data = self.ModifyNoFlyZone(Arguments)
                    
                elif Command == "AddDrone":
                    Sucess,Message,Data = self.AddDrone(Arguments)
                elif Command == "GetDronesUser":
                    Sucess,Message,Data = self.GetDronesUser(Arguments)
                elif Command == "GetDronesAll":
                    Sucess,Message,Data = self.GetDronesAll(Arguments)
                
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
                #Else if command doesnt exist send back Failure
                else:
                    Sucess,Message,Data = False,"Command does not exist",[]
                    print("User tried to use unregistered command")
            except Exception as e:
                Sucess,Message,Data = False,"An Error occured"+str(e),[]
                print("Error occured with UserID:",str(self.UserID),"Error :",str(e)," Sending failure message")
            self.Send((Sucess,Message,Data))
        
            
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
            Coord1,Coord2,Level = Argument[0],Argument[1],Argument[2]
            Sucess,Message = self.DB.AddNoFlyZone(Coord1,Coord2,Level,self.UserID)
        else:
            Sucess,Message = False,"Incorrect Argument format"
        return Sucess,Message,[]

    def RemoveNoFlyZone(self,Arguments):
        ZoneID = Arguments[0]
        Sucess,Message = self.DB.RemoveNoFlyZone(self.UserID,ZoneID)
        return Sucess,Message,[]
    
    def ModifyNoFlyZoneLevel(self,Arguments):
        ZoneID,Level = Arguments[0]
        Sucess,Message = self.DB.ModifyNoFlyZoneLevel(self.UserID,ZoneID,Level)
        return Sucess,Message,[]


    ########################################################
    def AddDrone(self,Arguments):
        DroneName,DroneType,DroneSpeed,DroneRange,DroneWeight = Arguments[0],Arguments[1],Arguments[2],Arguments[3],Arguments[4]
        Sucess,Message = self.DB.AddDrone(self.UserID,DroneName,DroneType,DroneSpeed,DroneRange,DroneWeight)
        return Sucess,Message,[]
    
    def RemoveDrone(self,Arguments):
        DroneID = Arguments[0]
        Sucess,Message = self.DB.RemoveDrone(self.UserID,DroneID)
        return Sucess,Message,[]
        
    def GetDronesUser(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetDronesUser(self.UserID)
        return Sucess,Message,Data

    def GetDronesAll(self,Arguments = None):
        Sucess,Message,Data = self.DB.GetDronesAll()
        return Sucess,Message,Data

    ########################################################
        
##    def GetUserID(self,Argument):
##    def CheckCredentials(self,Arguments):      
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
        DroneID,StartCoords,EndCoords,StartTime = Arguments[0],Arguments[1],Arguments[2],Arguments[3]
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






















