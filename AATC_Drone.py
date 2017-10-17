import socket,codecs,ast,recvall,sys,heapq,AATC_Crypto
from AATC_Coordinate import *
        
        
class DroneInterface:
    """Interface with which to allow a Drone to communicate with the server.
       Login using DroneCredentials. These can be stored on Drone eg sd card

       !!! Will probably not allow flight abortion in air as drone may not have connection !!! 

       Updating drone status could be run on a different thread if nessesary.
       Updating Drone status sends the coordinates and last battery to the server for reference.
       
       Check for flight will get the next flight in the next MaxLookAheadTime seconds eg 1800 for 30min.
       This will return a flightId which can be used to obtain the full flight details.
       GetFlight and GetFlightWaypoints will get the data for the flight from the respective table.
       Coordinates are stored in the form '(x,y,z)' as so must be converted to tuples first.



       Mark Flight Complete will tell the server that the drone has sucessfully completed the flight.
       
       Maybe Drone can calculate battery needed and can wait charge if low on battery
       Eg calculate trip distance and get range*battery, if not enough, wait and charge.
"""
    def __init__(self,Connection):
        self.con = Connection
        self.Crypto = AATC_Crypto.Crypter(self.con)
        self.DroneName = ""
        print("Welcome to the AATC Connection interface")
        
    def Send(self,Code,data):
        Info = self.Crypto.Encrypt(codecs.encode(str((Code,data))))
        self.con.sendall(Info)
    def Recv(self):   #Returns tuple of Sucess,Message,Data   of which data may just be useless for that function
        try:
            data = self.Crypto.Decrypt(recvall.recvall(self.con))
            data = ast.literal_eval(codecs.decode(data))
            #      Sucess, Message , Data
            return data[0],data[1],data[2]
        except Exception as e:
            print("Socket data recive error")
            print(str(e))
            return (False,"Conversion/Transfer Error"+str(e),[])



    #############################


    def Login(self,DroneID,DronePassword):
        self.Send("Login",(DroneID,DronePassword))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    #############################

    def UpdateDroneStatus(self,LastCoords,LastBattery):
        self.Send("UpdateDroneStatus",(LastCoords,LastBattery))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    ############################

    def DroneGetDroneInfo(self,DroneID):
        self.Send("DroneGetDroneInfo",(DroneID,))
        Sucess,Message,DroneInfo = self.Recv()
        return Sucess,Message,DroneInfo

    ############################

    def CheckForFlight(self,MaxLookAheadTime = 1800):
        self.Send("CheckForFlight",(MaxLookAheadTime,))
        Sucess,Message,FlightID = self.Recv()   #FlightID in form [(FlightID,)]
        return Sucess,Message,FlightID

    def GetFlight(self,FlightID):
        self.Send("GetFlight",(FlightID,))
        Sucess,Message,Flight = self.Recv()
        return Sucess,Message,Flight

    def GetFlightWaypoints(self,FlightID):
        self.Send("GetFlightWaypoints",(FlightID,))
        Sucess,Message,FlightWaypoints = self.Recv()
        return Sucess,Message,FlightWaypoints

    def MarkFlightComplete(self,FlightID,Code):
        self.Send("MarkFlightComplete",(FlightID,Code))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message



class Flight:
    def __init__(self,FlightID,DroneID,StartCoord,EndCoord,StartTime,ETA,Distance):
        self.FlightID = FlightID
        self.DroneID = DroneID
        self.StartCoord = StartCoord
        self.EndCoord = EndCoord
        self.StartTime = StartTime
        self.ETA = ETA
        self.Distance = Distance

class Waypoint:
    def __init__(self,FlightID,WaypointNumber,Coord,ETA):
        self.FlightID = FlightID
        self.WaypointNumber = WaypointNumber
        self.Coord = Coord
        self.ETA = ETA




def ConvertCoordString(CoordString):
    CoordTuple = ast.literal_eval(CoordString)
    Coord = Coordinate(CoordTuple[0],CoordTuple[1],CoordTuple[2],0,0,0)
    return Coord

def GetFlightObject(Message,Data):
    Data = Data[0]  # as Data = [(Stuff,stuff,even more stuff)]
    Columns = ast.literal_eval(Message)
    FlightIDIndex = Columns.index("FlightID")
    DroneIDIndex = Columns.index("DroneID")
    StartCoordsIndex = Columns.index("StartCoords")
    EndCoordsIndex = Columns.index("EndCoords")
    StartTimeIndex = Columns.index("StartTime")
    ETAIndex = Columns.index("ETA")
    DistanceIndex = Columns.index("Distance")

    FlightID = Data[FlightIDIndex]
    DroneID = Data[DroneIDIndex]
##    StartCoord = ConvertCoordString(Data[StartCoordsIndex])
##    EndCoord = ConvertCoordString(Data[EndCoordsIndex])
    StartCoord = Waypoint(FlightID,-1,ConvertCoordString(Data[StartCoordsIndex]),-1)
    EndCoord = Waypoint(FlightID,-2,ConvertCoordString(Data[EndCoordsIndex]),-1)

    
    StartTime = Data[FlightIDIndex]
    ETA = Data[FlightIDIndex]
    Distance = Data[DistanceIndex]

    FlightObj = Flight(FlightID,DroneID,StartCoord,EndCoord,StartTime,ETA,Distance)
    return FlightObj

def GetWaypointObjects(Message,Data):
    WaypointList = []
    Columns = ast.literal_eval(Message)
    
    FlightIDIndex = Columns.index("FlightID")
    WaypointNumberIndex = Columns.index("WaypointNumber")
    CoordIndex = Columns.index("Coords")
    ETAIndex = Columns.index("ETA")

    for point in Data:
        FlightID = point[FlightIDIndex]
        WaypointNumber = point[WaypointNumberIndex]
        Coord = ConvertCoordString(point[CoordIndex])
        ETA = point[ETAIndex]
        
        waypoint = Waypoint(FlightID,WaypointNumber,Coord,ETA)
        WaypointList.append(waypoint)


    z = []
    for item in WaypointList:   #Sorts into waypoint order
        z.append((item.WaypointNumber,item))
    heapq.heapify(z)
    WaypointList = []
    for item in z:
        WaypointList.append(item[1])
    return WaypointList
    
def MakeDroneInfo(DroneMessage,DroneData):
    return DroneInformation(DroneMessage,DroneData)

class DroneInformation:
    def __init__(self,Message,DroneInfo):
        DroneInfo = DroneInfo[0]
        Message = ast.literal_eval(Message)
        ColumnValue = {}
        Titles = ["DroneID","UserID","DroneName","DroneType","DroneSpeed","DroneRange","DroneWeight"]
        for title in Titles:
            ColumnValue[title] = DroneInfo[Message.index(title)]

        self.DroneID = ColumnValue["DroneID"]
        self.UserID = ColumnValue["UserID"]
        self.DroneName = ColumnValue["DroneName"]
        self.DroneType = ColumnValue["DroneType"]
        self.DroneSpeed = ColumnValue["DroneSpeed"]
        self.DroneRange = ColumnValue["DroneRange"]
        self.DroneWeight = ColumnValue["DroneWeight"]




def Connect(remote_ip,PORT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((remote_ip, PORT))
        print("Connected to > "+ remote_ip+":"+str(PORT))
        return s
    except Exception as e:
        print("Error binding port")
        print(e)
        print("Check address and port is up")
        print("Otherwise check server is functional")
        print("Exiting...")
        sys.exit()


def CreateDroneInterface(IP = "192.168.0.19",Port = 8002):
    soc = Connect(IP,Port)
    D = DroneInterface(soc)
    return D
