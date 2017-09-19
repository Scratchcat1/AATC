import threading,queue,time,random
import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BOARD)

#GPIO.setup(11, GPIO.OUT) #red
#GPIO.setup(13, GPIO.OUT) #amber
#GPIO.setup(21, GPIO.OUT) #green
#GPIO.setup(26, GPIO.IN) #button

class GPIO_Thread_Controller:
    def __init__(self,Command_Queue):
        self.Command_Queue = Command_Queue
        self.Threads = {}
        self.Thread_Queues = {}

    def Create_Thread(self,Thread_Name):
        Thread_Queue = queue.Queue()
        thread = threading.Thread(target = GPIO_Thread,args = (Thread_Name,Thread_Queue))
        self.Threads[Thread_Name] = thread
        self.Thread_Queues[Thread_Name] = Thread_Queue
        thread.start()

    def PassData(self,Thread_Name,Data):
        self.Thread_Queues[Thread_Name].put(Data)

    def Main(self):
        Exit = False
        while not Exit:
            try:
                Request = self.Command_Queue.get()   #(Thread_Name/Controller command,"Command",Args)
                self.Command_Queue.task_done()
                
                if Request[0] == "Controller":
                    Command,Args = Request[1],Request[2]
                    if Command == "Create_Thread":
                        self.Create_Thread(*Args)
                    elif Command == "Close_Thread":
                        self.Close_Thread(*Args)
                    elif Command == "Exit":
                        self.Exit = True
                    elif Command == "Reset":
                        self.Reset()
                else:
                    self.PassData(Request[0],(Request[1],Request[2]))
                        
                        

                

            except Exception as e:
                print("Error in GPIO_Thread_Controller",e)

    def Close_Thread(self,Thread_Name):
        Thread = self.Threads.pop(Thread_Name)
        Queue = self.Thread_Queues.pop(Thread_Name)
        Queue.put(("Exit",()))
        print("GPIO Controller closed Thread",Thread_Name)
        


    def Reset(self):
        print("Reseting GPIO Threading Controller...")
        Thread_Names = list(self.Threads.keys())
        for Thread_Name in Thread_Names:
            self.Close_Thread(Thread_Name)
        print("Reset GPIO Threading Controller")
                
        
        
        
        
        

def GPIO_Thread(Thread_Name,GPIO_Queue):
    Exit = False
    Function = BlankFunction
    FuncArgs = ()
    while not Exit:
        try:
            FuncReset = Function(Thread_Name,*FuncArgs) #calls the function passed to the thread
            
            if FuncReset:
                Function,FuncArgs = BlankFunction,()  #Resets commands. Allows function to exit itself.
                
            if not GPIO_Queue.empty():
                Data = GPIO_Queue.get()
                GPIO_Queue.task_done()
                Command,Arguments = Data[0],Data[1]
                
                if Command == "Function":
                    Function, FuncArgs = Arguments[0],Arguments[1]
                elif Command == "Exit":
                    Exit = True
                
        except Exception as e:
            print("Error occured in GPIO_Thread",Thread_Name,".",str(e))
            Function,FuncArgs = BlankFunction,()  #Resets commands to prevent large prints
            
                
            
        
        
def Create_Controller():
    q = queue.Queue()
    g = GPIO_Thread_Controller(q)
    t = threading.Thread(target = g.Main)
    t.start()
    return q
    





"""
Thread_Name is common to all processes accessing the Thread_Controller.
EG 'RED' will always reference the thread 'RED'.
Pin Number is not fixed per thread. Threads can control multiple pins or none at all. A new function can change the pins a Thread is controlling.


def Command(Thread_Name,arg1,arg2...):
    run function code
    ...
    ...
    ...
    end of function code
    return True/False  # return FuncReset value. If True, function will not be repeated. If False, will continue until new command arrives

"""


# Example functions

def BlankFunction(Thread_Name):
    time.sleep(0.2)
    return False

def DisplayName(Thread_Name,Sleep_Time):
    print("Message from Thread",Thread_Name,". Sleeping for time",Sleep_Time)
    time.sleep(Sleep_Time)
    return False
    

def BlinkTest(Thread_Name,pin,frequency,cycles):  #prints demonstration of blinking pin in text, Frequency in Hz, cycles = repeats till check for new instruction
    pauseTime = 1/(frequency*2)
    for x in range(cycles):
        print("Activating blink pin",pin, "Cycle:",x)
        time.sleep(pauseTime)
        print("Deactivating blink pin",pin, "Cycle:",x)
        time.sleep(pauseTime)
    return False

def PatternTest(Thread_Name, Pattern ,ReferenceTime=1):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.OUT) #red
        GPIO.setup(13, GPIO.OUT) #amber
        GPIO.setup(21, GPIO.OUT) #green
        #Pattern consists of a list with tuples of (Pin,State,WaitTime)
        for Step in Pattern:
            Pin = Step[0]
            State = Step[1]
            WaitTime = Step[2]

            GPIO.output(Pin,State)
            print("Thread {} | Pin {:>3} | State {:>2} | WaitTime {:>4}".format(Thread_Name,str(Pin),str(State),str(WaitTime)))
            time.sleep(WaitTime*ReferenceTime)
    except Exception as e:
        print("Exception in PatternTest",e)
    finally:
        GPIO.cleanup()
    return False

def PatternGenerator(PinSet=[11,13,21],StateSet = [0,1] ,Length = 50 ,MinTime = 0.1 ,MaxTime = 1 , RoundingTime = 2):
    Pattern = []
    for x in range(Length):
        Pattern.append((
            random.choice(PinSet),
            random.choice(StateSet),
            round(random.random()*(MaxTime-MinTime)+MinTime,RoundingTime)
                ))
    return Pattern
    


