import multiprocessing,socket,AATC_NoFlyZoneGrapher,sys,time,AATC_GPIO,HedaBot
import AATC_Server_002 as AATC_Server
#from AATC_Coordinate import *
from flask_app import Flask_Test_App



##########################################################
#####################This section is part of the flask webserver component of the AATC program, not part of the main project.

def StartFlaskServer(Thread_Name,Thread_Queue):
    Flask_Test_App.main_app(Flask_Test_App.app) # Starts the flask webserver
    

##########################################################


def ProcessSpawner(Name,Communications_Queue,Port,Type,Target): #Spawn processes for each connection
    Exit = False
    Spawner_Control_Queue = AATC_GPIO.Create_Controller()       #Create a controller for the sub processes
    ID_Counter = 1
    DisplayName = "["+str(Name)+":"+str(Type)+"]"
    while not Exit:
        try:
            HOST = ''
            PORT = Port

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(DisplayName,'Socket created')
            s.bind((HOST, PORT))            #Bind to the port

                 
            print(DisplayName, 'Socket bind complete')
            s.listen(10)
            print(DisplayName, 'Socket now listening')


            while not Exit:
                try:
                    conn, addr = s.accept()     #Accept connections
                    print(DisplayName, ' Connected with' , addr[0] , ':' , str(addr[1]), "Type:",Type)
                    Thread_Name = Type+str(ID_Counter)
                    Spawner_Control_Queue.put(("Controller","Create_Process",(Thread_Name,Target,(conn,))))     #Create the sub process for the connection
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

def StartProcesses(Control_Queue):      #Start each of the main sub processes.
    Control_Queue.put(("Controller","Create_Process",("USpawner",ProcessSpawner,(8000,"User",MakeUserConnection))))
    Control_Queue.put(("Controller","Create_Process",("MSpawner",ProcessSpawner,(8001,"Monitor",MakeMonitorConnection))))
    Control_Queue.put(("Controller","Create_Process",("DSpawner",ProcessSpawner,(8002,"Drone",MakeDroneConnection))))


    Control_Queue.put(("Controller","Create_Process",("Grapher",AATC_NoFlyZoneGrapher.NoFlyZoneGrapher_Launch)))
    Control_Queue.put(("Controller","Create_Process",("Cleaner",AATC_Server.Cleaner)))

    Control_Queue.put(("Controller","Create_Process",("Hedabot",HedaBot.TelebotLaunch,())))
    ###Control_Queue.put(("Controller","Create_Process",("Flask_Server",StartFlaskServer,())))
    print("[StartProcesses] All processes started")
    

if __name__ == "__main__":      #Starts the server
    print("Server is starting")
    

    Control_Queue = AATC_GPIO.Create_Controller()
    StartProcesses(Control_Queue)
    
    Main_Command = ""
    while Main_Command != "EXIT":
        Main_Command = input("Enter main command >>").upper()
        AATC_GPIO.multiprocessing.active_children()
        
        
        
    print("Killing all Server processes....")
    print("This may take time, sleeping processes will be killed when resuming from sleep")

    Control_Queue.put(("Controller","Exit",(True,)))    #Tells the sub processes to quit
    
    print("Main process is now exiting...")
    sys.exit()
            
            

    























