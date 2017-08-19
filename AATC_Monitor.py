#AATC Monitor system
# Used to display the flights of drones


import socket,codecs,ast,recvall,sys


class MonitorInterface:
    """Interface with which to allow a monitor to communicate with the server.
       In essence, a cut down User with access to some other User's drone,flight,waypoint data
       This will be used to display an approximatly real time view of the drones flying
       A Monitor can access all public visible drones as well as those which it has been given access to.
       These two sets are accessed seperatly. 
"""
    def __init__(self,Connection):
        self.con = Connection
        self.MonitorName = ""
        print("Welcome to the AATC Connection interface")
        
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



    ##############################

    def Login(self,MonitorName,MonitorPassword):
        self.MonitorName = MonitorName
        self.Send("Login",(MonitorName,MonitorPassword))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def GetNoFlyZones(self):
        self.Send("GetNoFlyZones",())
        Sucess,Message,NoFlyZones = self.Recv()
        return Sucess,Message,NoFlyZones

    def GetDronesAll(self):
        self.Send("GetDronesAll",())
        Sucess,Message,DronesAll = self.Recv()
        return Sucess,Message,DronesAll

    def GetUserID(self,Username):
        self.Send("GetUserID",(Username,))
        Sucess,Message,UserID = self.Recv()
        return Sucess,Message,UserID

    def GetUsername(self,UserID):
        self.Send("GetUsername",(UserID,))
        Sucess,Message,Username = self.Recv()
        return Sucess,Message,Username

    def AddMonitor(self,MonitorName,MonitorPassword):
        self.Send("AddMonitor",(MonitorName,MonitorPassword))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def GetMonitorDrones(self):
        self.Send("GetMonitorDrones",())
        Sucess,Message,DronesMonitor = self.Recv()
        return Sucess,Message,DronesMonitor

    def GetMonitorFlights(self):
        self.Send("GetMonitorFlights",())
        Sucess,Message,FlightsMonitor = self.Recv()
        return Sucess,Message,FlightsMonitor

    def GetMonitorFlightWaypoints(self):
        self.Send("GetMonitorFlightWaypoints",())
        Sucess,Message,WaypointsMonitor = self.Recv()
        return Sucess,Message,WaypointsMonitor

    def GetMonitorID(self,MonitorName):
        self.Send("GetMonitorID",(MonitorName,))
        Sucess,Message,MonitorID = self.Recv()
        return Sucess,Message,MonitorID

    def GetMonitorName(self,MonitorID):
        self.Send("GetMonitorName",(MonitorID,))
        Sucess,Message,MonitorName = self.Recv()
        return Sucess,Message,MonitorName

    def RemoveMonitorPermission(self,UserID):
        self.Send("RemoveMonitorPermission",(UserID,))
        Sucess,Message,_ = self.Recv()
        return Sucess,Message

    def GetMonitorPermissionMonitor(self):
        self.Send("GetMonitorPermissionMonitor",())
        Sucess,Message,MonitorPermissionMonitor = self.Recv()
        return Sucess,Message,MonitorPermissionMonitor

    def GetFlightsAll(self):
        self.Send("GetFlightsAll",())
        Sucess,Message,FlightsAll = self.Recv()
        return Sucess,Message,FlightsAll

    def GetFlightWaypointsAll(self):
        self.Send("GetFlightWaypointsAll",())
        Sucess,Message,WaypointsAll = self.Recv()
        return Sucess,Message,WaypointsAll






    
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



def CreateMonitorInterface(IP = "192.168.0.19",Port = 8001):
    soc = Connect(IP,Port)
    M = MonitorInterface(soc)
    return M
        
