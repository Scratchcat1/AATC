import multiprocessing,socket,AATC_NoFlyZoneGrapher
import AATC_Server_002 as AATC_Server

class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize
    def __str__(self):
        return str((round(self.x,8),round(self.y,8),round(self.z,8)))


def UserProcessSpawner():
    while True:
        try:
            HOST = ''
            PORT = 8000

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print( 'Socket created')
            s.bind((HOST, PORT))
                 
            print( 'Socket bind complete')
            s.listen(10)
            print( 'Socket now listening')


            while True:
                try:
                    conn, addr = s.accept()
                    print( '\nConnected with ' + addr[0] + ':' + str(addr[1])+ "Type:User")
                    UserProcess = multiprocessing.Process(target = MakeUserConnection,args = (conn,))
                    UserProcess.start()
                except Exception as e:
                    print("Error creating User connection",str(e))
        except Exception as e:
            print("Error in UserProcessSpawner",str(e))

def MakeUserConnection(conn):
    UConn = AATC_Server.UserConnection(conn)
    UConn.Connection_Loop()

#####################################################

def MonitorProcessSpawner():
    while True:
        try:
            HOST = ''
            PORT = 8001

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print( 'Socket created')
     
            s.bind((HOST, PORT))
            print( 'Socket bind complete')
            s.listen(10)
            print( 'Socket now listening')

            while True:
                try:
                    conn, addr = s.accept()
                    print( '\nConnected with ' + addr[0] + ':' + str(addr[1]) + "Type:Monitor")
                    MonitorProcess = multiprocessing.Process(target = MakeMonitorConnection,args = (conn,))
                    MonitorProcess.start()
                except Exception as e:
                    print("Error creating Monitor connection",str(e))
        except Exception as e:
            print("Error in MonitorProcessSpawner",str(e))

def MakeMonitorConnection(conn):
    MConn = AATC_Server.MonitorConnection(conn)
    MConn.Connection_Loop()



############################################################

def DroneProcessSpawner():
    while True:
        try:
            HOST = ''
            PORT = 8002

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print( 'Socket created')
            s.bind((HOST, PORT))

                 
            print( 'Socket bind complete')
            s.listen(10)
            print( 'Socket now listening')


            while True:
                try:
                    conn, addr = s.accept()
                    print( '\nConnected with ' + addr[0] + ':' + str(addr[1])+ "Type:Drone")
                    DroneProcess = multiprocessing.Process(target = MakeDroneConnection, args = (conn,))
                    DroneProcess.start()
                except Exception as e:
                    print("Error creating Drone connection",str(e))
        except Exception as e:
            print("Error in DroneProcessSpawner",str(e))

def MakeDroneConnection(conn):
    DConn = AATC_Server.DroneConnection(conn)
    DConn.Connection_Loop()



##########################################################
##########################################################
    

if __name__ == "__main__":
    print("Server is starting")
    #Launch UserProcess spawner
    UPS = multiprocessing.Process(target = UserProcessSpawner)
    UPS.start()

    #Launch MonitorPerocess spawner
    MPS = multiprocessing.Process(target = MonitorProcessSpawner)
    MPS.start()
    
    #Launch DroneProcess Spawner
    DPS = multiprocessing.Process(target = DroneProcessSpawner)
    DPS.start()

    #Launch NoFlyZoneGrapher
##    NFZG = multiprocessing.Process(target = AATC_NoFlyZoneGrapher.NoFlyZoneGrapher)
##    NFZG.start()

    CLN = multiprocessing.Process(target = AATC_Server.Cleaner)
    CLN.start()

    























