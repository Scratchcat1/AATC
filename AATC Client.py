#############################################################
#                Communication Lookup Table
#
#   ("Login",("Type","Username","Password",NewUser(Boolean))) -> (True/False,"Message")
#    Type -> Type of client logging in eg Monitor,Drone,User.
#    Returned Data
#       True,WelcomeMessage -> Sucess logging in, print welcome message 
#       False,Reason        -> Failure logging in , print reason why
#
#   ("GetNoFlyZones",(Limit1,Limit2)) -> (True/False, Message ,(List of ID and  Coordinate pairs eg (ID,(x,y,z),(x,y,z)) in a list  ))
#   
#    ("AddNoFlyZone",(StartCoords,EndCoords))  -> (True/False,Message)   Add a NoFlyZone between the coords. Will be rounded down to nearest nodes
#
#    ("RemoveNoFlyZone",(ZoneID,)) -> (True/Falce,Message)  Removes the no fly zone with that ID, Id can be found from GetNoFlyZones
#
#
#
#
#   ("GetDroneInfo",(AllDrones?,InFlight)    ->  (True/False, Message, (List of DronesData eg (Username,DroneName,DroneID,InFlight,ETA?,LastLocation,Speed,Range,Weight)))
#    If All is True the program will send all DronesInfo of drones who are made visible by owners. Otherwise only users drones
#    InFlight Selects only those which are flying
#
#    ("AddNewDrone",(DroneName,Speed,Range,Weight))  -> (True/False,Message)  Register a drone to central database
#
#    ("RemoveDrone",(DroneID,)) -> (True/False,Message)   Remove a drone from the central database
#
#    ("SetFlightVisibility",(Visibility,))  -> (True/False,Message)            Set Visibility of flights to public
#
#    ("GetFlightInfo",(All,))  -> (True/False,Message,FlightInfo)  Flight Info is List of Flights eg (FlightID,DroneID,StartCoords,TargetCoords,CurrentPosition,ETA,Path) where path is list of path Coords
#
#############################################################

def Connect(remote_ip,PORT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((remote_ip, PORT))
        print("Connected to > "+ remote_ip+":"+str(PORT))
        return s
    except:
        print("Error binding port")
        print("Check address and port is up")
        print("Otherwise check server is functional")
        print("Exiting...")
        sys.exit()


         
import socket,codecs,ast,recvall
#Create Socket
#Create Connection


##def split(tup,num = 3):  # Used to remove the data section for non data
##    Sucess,Message,Data = tup[0],tup[1],tup[2]
##    if num == 3:
##        return Sucess,Message,Data
##    elif num == 2:
##        return Sucess,Message


class UserInterface:
    def __init__(self,Connection):
        self.con = Connection
        self.Username  = ""
        print("Welcome to the AATC connection interface")

    def Login(self,Username,Password):
        self.Username = Username
        self.Send("Login",(Username,Password))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message
        
    ################################    
    ################################
    def GetNoFlyZones(self):
        self.Send("GetNoFlyZones",())
        Sucess,Message,NoFlyZones = self.Recv()
        return Sucess,Message,NoFlyZones

    def AddNoFlyZone(self,StartCoords,EndCoords,Level):
        self.Send("AddNoFlyZone",(StartCoords,EndCoords,Level))
        Sucess,Message,_ =  self.Recv()
        return Sucess,Message

    def RemoveNoFlyZone(self,ZoneID):
        self.Send("RemoveNoFlyZone",(ZoneID,))
        Sucess,Message,_ =  self.Recv()
        return Sucess,Message
    
    def ModifyNoFlyZoneLevel(self,ZoneID,Level):
        self.Send("ModifyNoFlyZoneLevel",(ZoneID,Level))
        Sucess,Message,_ =  self.Recv()
        return Sucess,Message     
    ##################################

    def AddDrone(self,DroneName,DronePassword,Type,Speed,Range,Weight):
        self.Send("AddDrone",(DroneName,DronePassword,Type,Speed,Range,Weight))
        Sucess, Message,_ =  self.Recv()
        return Sucess,Message
    
    def RemoveDrone(self,DroneID):
        self.Send("RemoveDrone",(DroneID,))
        Sucess,Message,_ =  self.Recv()
        return Sucess,Message

    def GetDroneID(self,DroneName):
        self.Send("GetDroneID",(DroneName,))
        Sucess,Message,DroneID = self.Recv()
        return Sucess,Message,DroneID

    def GetDroneCredentials(self,DroneID):
        self.Send("GetDroneCredentials",(DroneID,))
        Sucess,Message,Credentials = self.Recv()
        return Sucess,Message,Credentials

    def SetDroneCredentials(self,DroneID,DronePassword):
        self.Send("SetDroneCredentials",(DroneID,DronePassword))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def CheckDroneOwnership(self,UserID,DroneID):
        self.Send("CheckDroneOwnership")
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def GetDroneInfo(self,DroneID):
        self.Send("GetDroneInfo",(DroneID,))
        Sucess,Message,DroneInfo = self.Recv()
        return Sucess,Message,DroneInfo
    def GetDronesUser(self):
        self.Send("GetDronesUser",())
        Sucess,Message,DroneInfo  =  self.Recv()
        return Sucess,Message,DroneInfo
    def GetDronesAll(self):
        self.Send("GetDronesAll",())
        Sucess,Message,DroneInfo  =  self.Recv()
        return Sucess,Message,DroneInfo
    ###########################################

    def GetUserID(self,Username):
        self.Send("GetUserID",(Username,))
        Sucess,Message,UserID = self.Recv()
        return Sucess,Message,UserID

    def GetUsername(self,UserID):
        self.Send("GetUsername",(UserID,))
        Sucess,Message,Username = self.Recv()
        return Sucess,Message,Username   #Username will be ["asfgg"] as it is how database returns it

    def AddUser(self,Username,Password):
        self.Send("AddUser",(Username,Password))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message
    
    def SetFlightVisibility(self,Visibility):
        self.Send("SetUserPublicVisibleFlights",(Visibility,))
        Sucess,Message,_ =  self.Recv()
        return Sucess,Message

    def SetAccountType(self,Value):
        self.Send("SetAccountType",(Value,))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    ##########################################

    def GetFlightsUser(self):
        self.Send("GetFlightsUser",())
        Sucess,Message,UserFlights = self.Recv()
        return Sucess,Message,UserFlights

    def GetFlightsAll(self):
        self.Send("GetFlightsAll",())
        Sucess,Message,AllFlights = self.Recv()
        return Sucess,Message,AllFlights

    def AddFlight(self,DroneID,StartCoords,EndCoords,StartTime):
        self.Send("AddFlight",(DroneID,StartCoords,EndCoords,StartTime))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def RemoveFlight(self,FlightID):
        self.Send("RemoveFlight",(FlightID,))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message
    ##########################################

    def GetFlightWaypointsUser(self):
        self.Send("GetFlightWaypointsUser",())
        Sucess,Message,UserWaypoints = self.Recv()
        return Sucess,Message,UserWaypoints

    def GetFlightWaypointsAll(self):
        self.Send("GetFlightWaypointsAll",())
        Sucess,Message,AllWaypoints = self.Recv()
        return Sucess,Message,AllWaypoints
    ##########################################

    def GetMonitorID(self,MonitorName):
        self.Send("GetMonitorID",(MonitorName,))
        Sucess,Message,MonitorID = self.Recv()  #MonitorID = [NumberID] as how db returns
        return Sucess,Message,MonitorID

    def GetMonitorName(self,MonitorID):
        self.Send("GetMonitorName",(MonitorID,))
        Sucess,Message,MonitorName = self.Recv() #  [MonitorName]
        return Sucess,Message,MonitorName
    ##########################################

    def AddMonitorPermission(self,MonitorID,ExpiryDate):
        self.Send("AddMonitorPermission",(MonitorID,ExpiryDate))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message
    
    def RemoveMonitorPermission(self,MonitorID):
        self.Send("RemoveMonitorPermission",(MonitorID,))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def ModifyMonitorPermissionDate(self,MonitorID,NewDate):
        self.Send("ModifyMonitorPermissionDate",(MonitorID,NewDate))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def GetMonitorPermissionUser(self):
        self.Send("GetMonitorPermissionUser",())
        Sucess,Message,MonitorPermissionsUser = self.Recv()
        return Sucess,Message,MonitorPermissionsUser

    ##############################################
    ##############################################
    def Send(self,Code,data):
        Info = codecs.encode(str((Code,data)))
        self.con.sendall(Info)

    def Recv(self):   #Returns tuple of Sucess,Message,Data   of which data may just be useless for that function
        try:
            data = recvall.recvall(self.con)
            data = ast.literal_eval(codecs.decode(data))
            #      Sucess, Message , Data
            return data[0],data[1],data[2]
        except Exception as e:
            print("Socket data recive error")
            print(str(e))
            return (False,"Conversion/Transfer Error"+str(e),[])


def CreateUserInterface(IP = "192.168.0.19",Port = 8000):
    soc = Connect(IP,Port)
    U = UserInterface(soc)
    return U
