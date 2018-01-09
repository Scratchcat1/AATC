import multiprocessing,socket,AATC_NoFlyZoneGrapher,sys,time,AATC_GPIO,HedaBot
import AATC_Server_002 as AATC_Server
#from AATC_Coordinate import *
from flask_app import Flask_Test_App


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

def MakeUserConnection(Thread_Name,Thread_Queue,conn):
    try:
        UConn = AATC_Server.UserConnection(Thread_Name,Thread_Queue,conn)
        UConn.Connection_Loop()
    except Exception as e:
        print("Serious error in UserConnection",e)

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

def MakeMonitorConnection(Thread_Name,Thread_Queue,conn):
    try:
        MConn = AATC_Server.MonitorConnection(Thread_Name,Thread_Queue,conn)
        MConn.Connection_Loop()
    except Exception as e:
        print("Serious error in MonitorConnection",e)



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

def MakeDroneConnection(Thread_Name,Thread_Queue,conn):
    try:
        DConn = AATC_Server.DroneConnection(Thread_Name,Thread_Queue,conn)
        DConn.Connection_Loop()
    except Exception as e:
        print("Serious error in DroneConnection",e)



##########################################################
#####################This section is part of the flask webserver component of the AATC program, not part of the main project.

def StartFlaskServer(Thread_Name,Thread_Queue):
    Flask_Test_App.main_app(Flask_Test_App.app) # Starts the flask webserver
    

##########################################################


def ProcessSpawner(Name,Communications_Queue,Port,Type,Target):
    Exit = False
    Spawner_Control_Queue = AATC_GPIO.Create_Controller()
    ID_Counter = 1
    DisplayName = "["+str(Name)+":"+str(Type)+"]"
    while not Exit:
        try:
            HOST = ''
            PORT = Port

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(DisplayName,'Socket created')
            s.bind((HOST, PORT))

                 
            print(DisplayName, 'Socket bind complete')
            s.listen(10)
            print(DisplayName, 'Socket now listening')


            while not Exit:
                try:
                    conn, addr = s.accept()
                    print(DisplayName, ' Connected with' , addr[0] , ':' , str(addr[1]), "Type:",Type)
                    Thread_Name = Type+str(ID_Counter)
                    Spawner_Control_Queue.put(("Controller","Create_Process",(Thread_Name,Target,(conn,))))
                    ID_Counter +=1
                except Exception as e:
                    print("Error creating" ,Type,"connection",str(e))

                #Check for commands from Communications_Queue
                if not Communications_Queue.empty():
                    data = Communications_Queue.get()
                    Command,Arguments = data[0],data[1]
                    if Command == "Exit":
                        Exit = True

                        
        except Exception as e:
            time.sleep(10) # If a serious error occurs then this will prevent large amounts of errors making it easier to find a solution.
            print("Error in",Type,"Process Spawner",str(e))
            
    Spawner_Control_Queue.put(("Controller","Exit",(True,)))

def StartProcesses(Control_Queue):
    Control_Queue.put(("Controller","Create_Process",("USpawner",ProcessSpawner,(8000,"User",MakeUserConnection))))
    Control_Queue.put(("Controller","Create_Process",("MSpawner",ProcessSpawner,(8001,"Monitor",MakeMonitorConnection))))
    Control_Queue.put(("Controller","Create_Process",("DSpawner",ProcessSpawner,(8002,"Drone",MakeDroneConnection))))


    Control_Queue.put(("Controller","Create_Process",("Grapher",AATC_NoFlyZoneGrapher.NoFlyZoneGrapher)))
    Control_Queue.put(("Controller","Create_Process",("Cleaner",AATC_Server.Cleaner)))

    Control_Queue.put(("Controller","Create_Process",("Hedabot",HedaBot.TelebotLaunch,())))
    ###Control_Queue.put(("Controller","Create_Process",("Flask_Server",StartFlaskServer,())))
    print("[StartProcesses] All processes started")
    

if __name__ == "__main__":
    print("Server is starting")
    

    Control_Queue = AATC_GPIO.Create_Controller()
    StartProcesses(Control_Queue)
    
    Main_Command = ""
    while Main_Command != "EXIT":
        Main_Command = input("Enter main command >>").upper()
        AATC_GPIO.multiprocessing.active_children()
        
        
        
    print("Killing all Server processes....")
    print("This may take time, sleeping processes will be killed when resuming from sleep")

    Control_Queue.put(("Controller","Exit",(True,)))
    
    print("Main process is now exiting...")
    sys.exit()
            
            

    























