import multiprocessing,socket,AATC_NoFlyZoneGrapher,sys,time
import AATC_Server_002 as AATC_Server
from AATC_Coordinate import *


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


def ProcessSpawner(Port,Type,Target,KillSwitch):
    ProcessList = []
    while not KillSwitch.is_set():
        try:
            HOST = ''
            PORT = Port

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print( 'Socket created')
            s.bind((HOST, PORT))

                 
            print( 'Socket bind complete')
            s.listen(10)
            print( 'Socket now listening')


            while not KillSwitch.is_set():
                try:
                    conn, addr = s.accept()
                    print( '\nConnected with ' + addr[0] + ':' + str(addr[1])+ "Type:"+Type)
                    Process = multiprocessing.Process(target = Target, args = (conn,))
                    Process.start()
                    ProcessList.append(Process)
                except Exception as e:
                    print("Error creating" ,Type,"connection",str(e))
        except Exception as e:
            print("Error in",Type,"Process Spawner",str(e))
    for Process in ProcessList:
        Process.join()
    

if __name__ == "__main__":
    print("Server is starting")
    KillSwitch = multiprocessing.Event()
    HighProcessList = []
    #Launch UserProcess spawner
    UPS = multiprocessing.Process(target = ProcessSpawner,args = (8000,"User",MakeUserConnection,KillSwitch))
    HighProcessList.append(UPS)
    UPS.start()

    #Launch MonitorPerocess spawner
    MPS = multiprocessing.Process(target = ProcessSpawner,args = (8001,"Monitor",MakeMonitorConnection,KillSwitch))
    HighProcessList.append(MPS)
    MPS.start()
    
    #Launch DroneProcess Spawner
    DPS = multiprocessing.Process(target = ProcessSpawner,args = (8002,"Drone",MakeDroneConnection,KillSwitch))
    HighProcessList.append(DPS)
    DPS.start()

    #Launch NoFlyZoneGrapher
    NFZG = multiprocessing.Process(target = AATC_NoFlyZoneGrapher.NoFlyZoneGrapher, args = (KillSwitch,150))
    HighProcessList.append(NFZG)
    NFZG.start()

    CLN = multiprocessing.Process(target = AATC_Server.Cleaner,args = (KillSwitch,150))
    HighProcessList.append(CLN)
    CLN.start()

    Main_Command = ""
    while Main_Command != "EXIT":
        Main_Command = input("Enter main command >>").upper()
        
        
        
    print("Killing all Server processes....")
    print("This may take time, sleeping processes will be killed when resuming from sleep")
    KillSwitch.set()
    for Process in HighProcessList:
        Process.join()
        print("Process:",Process,"has exited")
    print("Main process is now exiting...")
    sys.exit()
            
            

    























