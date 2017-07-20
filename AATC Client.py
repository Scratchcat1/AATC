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


def Send(Connection,Code,Data):
    Connection.send((Code,Data))

def Login(Connection):
    Continue = "Y"
    ConInterface= None
    while Continue == "Y":
        username = input("Enter username:")
        password = input("Enter password:")
        #Send(Connection,"Login",("User",username,password))
        #LoggedIn,Message =  Get Response
        print(Message)
        if not LoggedIn:
            Continue = input("Error Logging on, Continue? (Y/N)").upper()
        else:
            Continue = "N"
            ConInteface = ConnectionInterface(Connection,username)
    return LoggedIn
         
import socket
#Create Socket
#Create Connection

LoggedIn,ConInterface = Login(Connection)

if LoggedIn:
    UserInstance = UserControl(Connection,Username)
else:
    print("Exiting program..")




class ConnectionInterface:
    def __init__(self,Connection,Username):
        self.Connection = Connection
        self.Username = Username       #Used to address user
        print("Welcome to the AATC connection interface",self.Username)
    def FetchNoFlyZones(self):
        self.Send("GetNoFlyZones",())
        #Sucess,Message,NoFlyZones = Get Data
        return Sucess,Message,NoFlyZones

    def AddNoFlyZone(self,StartCoords,EndCoords):
        self.Send("AddNoFlyZone",(StartCoords,EndCoords))
        #Sucess,Message = GetData
        return Sucess,Message

    def RemoveNoFlyZone(self,ZoneID):
        self.Send("RemoveNoFlyZone",(ZoneID,))
        # Sucess,Message = GetData
        return Sucess,Message 
    

    def GetDroneInfo(self,All = False,InFlight = False):
        self.Send("GetDroneInfo",(All,InFlight))
        #Sucess,Message,DroneInfo  = GetData
        return Sucess,Message,DroneInfo

    def AddNewDrone(self,DroneName,Speed,Range,Weight):
        self.Send("AddNewDrone",(DroneName,Speed,Range,Weight))
        #Sucess, Message = GetData
        return Sucess,Message

    def RemoveDrone(self,DroneID):
        self.Send("RemoveDrone",(DroneID,))
        #Sucess,Message = GetData
        return Sucess,Message

    def SetFlightVisibility(self,Visibility):
        self.Send("SetFlightVisibility",(Visibility,))
        # Sucess,Message = GetData
        return Sucess,Message

    def GetFlightInfo(self,All= False):
        self.Send("GetFlightInfo",(All,))
        #Sucess,Message,FlightInfo = GetData
        return Sucess,Message,FlightInfo
        
    def Send(self,Code,data):
        Send(self.Connection,Code,data)





"""SERVER SECTION TEMP"""



