import threading,multiprocessing,queue,time,random, sys
try:
    import RPi.GPIO as GPIO
    ENABLE_GPIO = True
except:
    print("No RPi.GPIO module available. Features depending on this will not work/crash")
    ENABLE_GPIO = False
#GPIO.setmode(GPIO.BOARD)

##GPIO.setup(11, GPIO.OUT) #red
##GPIO.setup(13, GPIO.OUT) #amber
##GPIO.setup(21, GPIO.OUT) #green
##GPIO.setup(26, GPIO.IN) #button

def GPIO_Wait_Switch(pin,wait_time = 1, SWITCH_MODE= 1, Indicator_Pin = False):  # Will wait for pin to switch to the SWITCH_MODE setting. If not will sleep for wait_time seconds.
    #if "GPIO" in sys.modules:   # If does not have GPIO will automatically pass through.
    if ENABLE_GPIO:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin,GPIO.IN)
        
        if Indicator_Pin:
            GPIO_Queue = Create_Controller(Name = "AMBER_LED")
            GPIO_Queue.put(("Controller","Create_Thread",("INDICATOR",)))
        
        while GPIO.input(pin) != SWITCH_MODE:
            if Indicator_Pin:
                GPIO_Queue.put(("INDICATOR","Function",(Blink,(Indicator_Pin,1/wait_time,1,False))))   # will automatically blink at a rate of 1 blink per wait_time
            time.sleep(wait_time)
    
    else:
        pass  


def GPIO_Thread(Thread_Name,GPIO_Queue):
    Exit = False
    Function = BlankFunction
    FuncArgs = ()
    while not Exit:
        try:
            Repeat = Function(Thread_Name,*FuncArgs) #calls the function passed to the thread
            
            if not Repeat:
                Function,FuncArgs = BlankFunction,()  #Resets commands. Allows function to exit itself.
                
            if not GPIO_Queue.empty():
                Data = GPIO_Queue.get()
                #GPIO_Queue.task_done()
                Command,Arguments = Data[0],Data[1]
                
                if Command == "Function":
                    Function, FuncArgs = Arguments[0],Arguments[1]
                elif Command == "Exit":
                    Exit = True
                
        except Exception as e:
            print("Error occured in GPIO_Thread",Thread_Name,".",str(e))
            Function,FuncArgs = BlankFunction,()  #Resets commands to prevent large prints



            

class Thread_Handle:
    def __init__(self,Thread_Name,ThreadPointer,Queue):
        self._Thread_Name = Thread_Name
        self._ThreadPointer = ThreadPointer
        self._Queue = Queue

    def Get_Thread_Name(self):
        return self._Thread_Name

    def Get_ThreadPointer(self):
        return self._ThreadPointer

    def Get_Queue(self):
        return self._Queue





class Thread_Controller:
    def __init__(self,Command_Queue,Name = ""):
        print("Creating Thread Controller",Name)
        self._Name ="TC"+ Name + " >"
        self._Command_Queue = Command_Queue
        self._Threads = {}

    def Create_Thread(self,Thread_Name,TargetCommand = GPIO_Thread,TargetArgs = (),Process = False):     #If Process is True, will use a Process rather than a thread.
        if Thread_Name in self._Threads: #Close thread if already exists
            self.Close_Thread(Thread_Name)
            
        if Process:
            Thread_Queue = multiprocessing.Queue()
            threadPointer = multiprocessing.Process(target = TargetCommand,args = (Thread_Name,Thread_Queue)+TargetArgs)
        else:
            Thread_Queue = queue.Queue()
            threadPointer = threading.Thread(target = TargetCommand,args = (Thread_Name,Thread_Queue)+TargetArgs)
        self._Threads[Thread_Name] = Thread_Handle(Thread_Name,threadPointer,Thread_Queue)
        threadPointer.start()
        
    def Close_Thread(self,Thread_Name):
        ClosingThreadHandle = self._Threads.pop(Thread_Name)
        Queue = ClosingThreadHandle.Get_Queue()
        Queue.put(("Exit",()))
        print(self._Name,"GPIO Controller closed Thread",Thread_Name)
        return ClosingThreadHandle  #Returns Thread_Handle of thread
   

    def PassData(self,Thread_Name,Data):
        Queue = self._Threads[Thread_Name].Get_Queue()
        Queue.put(Data)

    def Main(self):
        Exit = False
        while not Exit:
            try:
                Request = self._Command_Queue.get()   #(Thread_Name/Controller command,"Command",Args)
                self._Command_Queue.task_done()
                
                if Request[0] == "Controller":
                    Command,Args = Request[1],Request[2]
                    if Command == "Create_Thread":               #In total form ("Controller","Create_Thread",(ThreadName,[TargetFunction,TargetArguments]))
                        self.Create_Thread(*Args)
                    elif Command == "Create_Process":
                        self.Create_Thread(*Args, Process = True)
                    elif Command == "Close_Thread":
                        self.Close_Thread(*Args)
                    elif Command == "Exit":  #Shutdown  everything
                        self.Reset(*Args)
                        self._Exit = True
                    elif Command == "Reset":  #Shutdown all threads, not controller
                        self.Reset(*Args)
                        
                else:
                    self.PassData(Request[0],(Request[1],Request[2]))
                        

            except Exception as e:
                print(self._Name,"Error in GPIO_Thread_Controller",e)
        print(self._Name,"Shutting down")


    def Reset(self,Wait_Join = False):
        print(self._Name,"Reseting GPIO Threading Controller...")
        Thread_Names = list(self._Threads.keys())
        ThreadHandles = []
        for Thread_Name in Thread_Names:
            ClosingThreadHandle = self.Close_Thread(Thread_Name)
            ThreadHandles.append(ClosingThreadHandle)
            
        if Wait_Join:   #In seperate loop to asyncrously call 'Exit'      
            for ThreadHandle in ThreadHandles:
                ThreadPointer = ThreadHandle.Get_ThreadPointer()
                ThreadPointer.join()
                
        print(self._Name,"Reset GPIO Threading Controller")
                
        
        
    
            
                
            
        
        
def Create_Controller(process = False, Name = ""):
    if process:
        q = multiprocessing.Queue()
    else:
        q = queue.Queue()
        
    TC = Thread_Controller(q,Name)

    if process:
        t = multiprocessing.Process(target = TC.Main)
    else:   
        t = threading.Thread(target = TC.Main)
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
    return True/False  # return Repeat value. If True, function will  be repeated. If False will exit.

"""


# Example functions

def BlankFunction(Thread_Name):
    time.sleep(0.2)
    return True

def DisplayName(Thread_Name,Sleep_Time):
    print("Message from Thread",Thread_Name,". Sleeping for time",Sleep_Time)
    time.sleep(Sleep_Time)
    return True
    

def BlinkTest(Thread_Name,pin,frequency,cycles=1,repeat = False):  #prints demonstration of blinking pin in text, Frequency in Hz, cycles = repeats till check for new instruction
    pauseTime = 1/(frequency*2)
    for x in range(cycles):
        print("Activating blink pin",pin, "Cycle:",x)
        time.sleep(pauseTime)
        print("Deactivating blink pin",pin, "Cycle:",x)
        time.sleep(pauseTime)
        
    return repeat




##################General GPIO functions

def Blink(Thread_Name,pin,frequency,cycles = 1,repeat= False):
    pauseTime = 1/(frequency*2)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin,GPIO.OUT)
    try:
        for x in range(cycles):
            #On
            GPIO.output(pin,1)
            time.sleep(pauseTime)

            #Off
            GPIO.output(pin,0)
            time.sleep(pauseTime)
    finally:
        GPIO.cleanup(pin)
        
    return repeat
        
        
    




def Pattern(Thread_Name, Pattern ,ReferenceTime=1,repeat = True):
    pins = set()
    for item in Pattern:
        pins.add(item[0])
    try:
        GPIO.setmode(GPIO.BOARD)
##        GPIO.setup(11, GPIO.OUT) #red
##        GPIO.setup(13, GPIO.OUT) #amber
##        GPIO.setup(21, GPIO.OUT) #green
        for pin in pins:
            GPIO.setup(pin,GPIO.OUT)
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
        GPIO.cleanup(*pins)
    return repeat

def PatternGenerator(PinSet=[11,13,21],StateSet = [0,1] ,Length = 50 ,MinTime = 0.1 ,MaxTime = 1 , RoundingTime = 2):
    Pattern = []
    for x in range(Length):
        Pattern.append((
            random.choice(PinSet),
            random.choice(StateSet),
            round(random.random()*(MaxTime-MinTime)+MinTime,RoundingTime)
                ))
    return Pattern
    


