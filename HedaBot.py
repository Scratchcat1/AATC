import telepot,time,random,multiprocessing,AATC_DB,AATC_GPIO,SkyrimQuote #Skyrim quote just gets a random quote from skyrim
import AATC_Server_002 as AATC_Server


def printUpdates(Bot):
    for item in Bot.getUpdates():
        print(item)

def TelebotLaunch(Thread_Name,Input_Queue):
    Heda = Telebot(Thread_Name,Input_Queue)
    print("Starting Telebot",Thread_Name)
    Heda.mainLoop()


def StringBlock(string, block_size):
    blocks = []
    for n in range(0,len(string),block_size):
        blocks.append(string[n:n+block_size])
    return blocks

class Ticker:
    def __init__(self,frequency):
        self._last_call = time.time()
        self._time_period = 1/frequency

    def wait_ok(self):
        dtime = (self._last_call+self._time_period)-time.time()
        if dtime > 0:
            time.sleep(dtime)
        self._last_call = time.time()

    def reset(self):
        self._last_call  = 0

        

class Telebot:
    def __init__(self,Thread_Name,Input_Queue,signature = "\nHeda ∞",start_update_id= 0,inputSorterNumber = 2):
        self._Thread_Name = Thread_Name
        self._Input_Queue = Input_Queue
        self._bot = telepot.Bot(BOT_TOKEN)
        self._signature = signature
        self._update_id = start_update_id
        self._chat_id = 0
    
        self._ticker = Ticker(3)    # Used to limit the frequency at which messages are sent
        self._Restart_Ticker = Ticker(1/60)
        self._Update_Queue = []
        self._DB = AATC_DB.DBConnection()
        self._OutputQueue = multiprocessing.Queue()
        
        self._inputSorterNumber = inputSorterNumber
        self._TC_Queue = AATC_GPIO.Create_Controller()
        for ProcessID in range(self._inputSorterNumber):
            self._TC_Queue.put(("Controller","Create_Process",(ProcessID,inputSorter,(self._OutputQueue,))))
        
        

    def setChatID(self,chat_id):
        self._chat_id = chat_id

    def sendMessage(self,message,chat_id = None):
        if chat_id != None:
            self._chat_id = chat_id
        blocks = StringBlock(message+self._signature,4000)
        for string in blocks:
            self._ticker.wait_ok()
            self._bot.sendMessage(self._chat_id,string)

    def getUpdate(self):
        if len(self._Update_Queue) ==0:
            updates = []
            while len(updates) == 0:
                updates = self._bot.getUpdates(self._update_id +1)
                if len(updates) != 0:
                    pass
                else:
                    time.sleep(1)
            for item in updates:
                self._update_id = max([self._update_id, item["update_id"]])
                self._Update_Queue.append(item)

        return self._Update_Queue.pop(0)

    
    def textInput(self,Message=""):  #relays message between user and machine
        self.sendMessage(Message,self._chat_id)
        return self.getUpdate()["message"]["text"]

    def mainLoop(self):
        Exit = False
        while not Exit:
            try:
                while not self._OutputQueue.empty():  #Sends the messages which have been created.
                    packet = self._OutputQueue.get()
                    self.sendMessage(*packet)
                    
                update = self._bot.getUpdates(self._update_id + 1)
                for packet in update:
                    self._update_id = max([self._update_id,packet["update_id"]])

                    messageText = packet["message"]["text"]
                    chatID = packet["message"]["chat"]["id"]
                    if ord(messageText[0]) >200:  #Deal with emojis -_-
                        continue

                    Thread_Name = chatID % self._inputSorterNumber
                    self._TC_Queue.put((Thread_Name,"ProcessMessage",(messageText,chatID)))
                    
                time.sleep(0.5)
            except Exception as e:
                print("Error in Telebot",self._Thread_Name,"Error:",e)
                self._Restart_Ticker.wait_ok()
                try:
                    self._bot = telepot.Bot(BOT_TOKEN)
                except Exception as e:
                    print("Error in Telebot",self._Thread_Name,"Error connecting to telegram servers. Check your internet connection and API Token. Connection may be blocked by administrator.")
                

            if not self._Input_Queue.empty():
                data = self._Input_Queue.get()
                command,arguments = data[0],data[1]
                if command == "Exit":
                    Exit = True
        self._TC_Queue.put(("Controller","Exit",(True,)))
        print("Telebot", self._Thread_Name," is exiting")
            

    def processMessage(self,messageText,chat_id = 0):
        lowerText = messageText.lower()
        response = messageText
        if "time" in lowerText:
            response = str(time.time())

        elif "date" in lowerText:
            response = str(time.strftime("%Y:%m:%d %H:%M:%S"))

        elif "random float" in lowerText:
            response = str(random.random())

        else:   
            with open("SkyrimDialogue.txt","r") as f:
                for i,line in enumerate(f):
                    pass

            lineNum = random.randint(0,i+1)
            with open("SkyrimDialogue.txt","r") as f:
                for x in range(lineNum):
                    line = f.readline()
            response = line.rstrip().split("\t")[-1:][0]

        return response

    

class inputSorter:
    def __init__(self,Thread_Name,Input_Queue,OutputQueue,Exec_Processes = 1):
        self._Thread_Name = Thread_Name
        self._Input_Queue = Input_Queue
        self._OutputQueue = OutputQueue
        self._Exec_Processes = Exec_Processes
        
        self._DB = AATC_DB.DBConnection()
        self._ShowCommandsList = ShowCommands()
        self._CommandDictionary = CreateCommandDictionary()

        self._EC_Queue = AATC_GPIO.Create_Controller()
        for ProcessID in range(self._Exec_Processes):
            self._EC_Queue.put(("Controller","Create_Process",(ProcessID,CommandExecutor,(self._OutputQueue,))))

        self.mainLoop()

    def mainLoop(self):
        Exit = False
        while not Exit:
            try:
                data = self._Input_Queue.get()
                command,arguments = data[0],data[1]
                if command == "Exit":
                    Exit = True
                    continue
            
                messageText,chat_id = arguments[0],arguments[1]

                response = self.processInput(messageText,chat_id)
                if response != None:
##                    print()
##                    print("Message:",messageText)
##                    print("Response:",response)
                    self._OutputQueue.put((response,chat_id))
            except Exception as e:
                print("Error in inputSorter",self._Thread_Name,"Error:",e)
        self._EC_Queue.put(("Controller","Exit",(True,)))
        print("Closing inputSorter",self._Thread_Name)


    def processInput(self,messageText,chat_id):
        lowerText = messageText.lower()
        try:
            if "/" in messageText:
                if "/cancel" == messageText:
                    self._DB.Bot_flushStack(chat_id)
                    return "Command cancelled"
                elif "/quote" == messageText:
                    return SkyrimQuote.SkyrimQuote()
                else:
                    self._DB.Bot_flushStack(chat_id)
                    messageText = messageText.replace("/","")
            elif lowerText in ["help","?"]:
                return self._ShowCommandsList
                
                    
            self._DB.Bot_addValue(messageText,chat_id)
            
            stack_size = self._DB.Bot_getStackSize(chat_id)
            command = self._DB.Bot_getCommand(chat_id)
            command_size = len(self._CommandDictionary[command])
            
            if stack_size == command_size+1:
                UserID = self._DB.Bot_GetUserID(chat_id)
                stack = self._DB.Bot_getStack(chat_id)
                self._DB.Bot_flushStack(chat_id)
                
                packet = convertDBStack(stack,self._CommandDictionary)

##                p = multiprocessing.Process(target = AATC_Server.BotConnection, args = (UserID,chat_id,packet,self._OutputQueue))
##                p.start()
                Thread_Name = random.randint(0,self._Exec_Processes-1)
                self._EC_Queue.put((Thread_Name,"RunCommand",(UserID,chat_id,packet)))
                
            else:
                return self._CommandDictionary[command][stack_size]["Query"]
            
        except Exception as e:
            return "Error processing message "+str(e) + "\n" + self._ShowCommandsList





class CommandExecutor:
    def __init__(self,Thread_Name,Input_Queue,OutputQueue):
        self._Thread_Name = Thread_Name
        self._Input_Queue = Input_Queue
        self._OutputQueue = OutputQueue

        self.mainLoop()

    def mainLoop(self):
        Exit = False
        while not Exit:
            try:
                data = self._Input_Queue.get()
                command,arguments = data[0],data[1]
                if command == "Exit":
                    Exit = True
                    continue

                
                elif command == "RunCommand":
                    UserID,chat_id,packet = arguments[0],arguments[1],arguments[2]
                    AATC_Server.BotConnection(UserID,chat_id,packet,self._OutputQueue)

                else:
                    print("CommandExecutor",self._Thread_Name," obtained incorrect command",command)

            except Exception as e:
                print("Exception in CommandExecutor",self._Thread_Name,"Error:",e)
        


















def convertDBStack(result,CommandDictionary):
    result = list(result)
    command = result.pop(0)[0]
    arguments = []
    for i,item in enumerate(result):
        #print(item[0])
        arguments.append(CommandDictionary[command][i+1]["Type"](item[0]))
    packet = (command,arguments)
    return packet

def SplitWaypoints(string,MARKER = "\n"):
    waypoints = string.split(MARKER)
    return waypoints

def ShowCommands():
    result = "Here is a list of commands you can use"
    commands = CreateCommandDictionary()
    for command in commands:
        result += "\n/"+command
    return result
    


def CreateCommandDictionary():
    Commands = {}
    # Format Commands["Commnad String"] = {ArgumentNumber:{"Quergy":"Query text","Type":type of response eg int. Must be callable }}
    Commands["Login"] = {1:{"Query":"Enter Username","Type":str},
                          2:{"Query":"Enter Password","Type":str}}

    #####################################################

    Commands["GetNoFlyZones"] = {}
    Commands["RemoveNoFlyZone"] = {1: {'Type': int, 'Query': 'Enter ZoneID'}}
    Commands["AddNoFlyZone"] = {1: {'Type': str, 'Query': 'Enter first coordinate'},
                                2: {'Type': str, 'Query': 'Enter second coordinate'},
                                3: {'Type': int, 'Query': 'Enter level of NoFlyZone'}}

    
    Commands["ModifyNoFlyZoneLevel"] = {1: {'Type': int, 'Query': 'Enter ZoneID'},
                                        2: {'Type': int, 'Query': 'Enter new level of Zone'}}

    #####################################################


    Commands["AddDrone"] = {1: {'Type': str, 'Query': 'Enter Drone Name'},
                            2: {'Type': str, 'Query': 'Enter Drone Password'},
                            3: {'Type': str, 'Query': 'Enter Drone Type'},
                            4: {'Type': int, 'Query': 'Enter Drone Speed'},
                            5: {'Type': int, 'Query': 'Enter Drone Range'},
                            6: {'Type': float, 'Query': 'Enter Drone Weight'}}


    Commands["RemoveDrone"] ={1: {'Type': int, 'Query': 'Enter Drone ID to be deleted'}}

    Commands["GetDroneID"] = {1: {'Type': str, 'Query': 'Enter Drone Name'}}

    Commands["GetDroneCredentials"] = {1: {'Type': int, 'Query': 'Enter DroneID'}}

    Commands["SetDroneCredentials"] = {1: {'Type': int, 'Query': 'Enter DroneID'},
                                     2: {'Type': str, 'Query': 'Enter Drone Password'}}

    Commands["CheckDroneOwnership"]= {1: {'Type': int, 'Query': 'Enter UserID'},
                                      2: {'Type': int, 'Query': 'Enter DroneID'}}

    Commands["GetDroneInfo"]= {1: {'Query': 'Enter DroneID', 'Type': int}}

    Commands["GetDronesUser"]= {}
    Commands["GetDronesAll"]= {}

    ######################################

    Commands["GetUserID"]= {1: {'Query': 'Enter Username', 'Type': str}}
    Commands["GetUsername"]= {1: {'Query': 'Enter UserID', 'Type': int}}

    Commands["AddUser"]= {1: {'Query': 'Enter Username', 'Type': str},
                          2: {'Query': 'Enter Password', 'Type': str}}

    Commands["SetFlightVisibility"]= {1: {'Query': 'Enter Visibility', 'Type': int}}

    Commands["SetAccountType"]= {1: {'Query': 'Enter Permission', 'Type': str},
                                 2: {'Query': 'Enter Account Type', 'Type': int}}

    Commands["UserChangePassword"] = {1:{"Query": "Enter Old Password", "Type":str},
                                      2:{"Query": "Enter New Password", "Type":str}}


    #######################################

    Commands["GetFlightsUser"]= {}
    Commands["GetFlightsAll"]= {}

    Commands["AddFlight"]= {1: {'Query': 'Enter DroneID', 'Type': int},
                            2: {'Query': 'Enter waypoints in single message in brackets split by returns', 'Type': SplitWaypoints},
                            3: {'Query': 'Enter StartTime', 'Type': int}}


    Commands["RemoveFlight"]= {1: {'Query': 'Enter FlightID', 'Type': int}}

    Commands["GetFlightWaypointsUser"]= {}
    Commands["GetFlightWaypointsAll"]= {}

    ################################################

    Commands["GetMonitorID"]= {1: {'Query': 'Enter MonitorName', 'Type': str}}
    Commands["GetMonitorName"]= {1: {'Query': 'Enter MonitorID', 'Type': int}}

    Commands["AddMonitorPermission"]= {1: {'Query': 'Enter MonitorID', 'Type': int},
                                       2: {'Query': 'Enter Expiry Date', 'Type': int}}

    Commands["RemoveMonitorPermission"]= {1: {'Query': 'Enter MonitorID', 'Type': int}}

    Commands["ModifyMonitorPermissionDate"]= {1: {'Query': 'Enter MonitorID', 'Type': int},
                                              2: {'Query': 'Enter New Expiry Date', 'Type': int}}

    Commands["GetMonitorPermissionUser"]= {}

    return Commands

    
##import sqlite3 as sql    
##class DB_Connection:
##    def __init__(self):
##        self._DB_con = sql.connect("db.name")
##        self.cur = self._DB_con.cursor()
##            
##    def addValue(self,value,chat_id):
##        self.cur.execute("SELECT MAX(stack_pos) FROM InputStack WHERE chat_id = ?",(chat_id,))
##        result = self.cur.fetchall()
##        if not result[0][0] == None:
##            stack_pos = result[0][0] +1
##        else:
##            stack_pos = 0
##        self.cur.execute("INSERT INTO InputStack VALUES(?,?,?)",(chat_id,stack_pos,value))
##        self._DB_con.commit()
##    
##    def getCommand(self,chat_id):
##        self.cur.execute("SELECT value FROM InputStack WHERE chat_id = ? AND stack_pos = 0",(chat_id,))
##        result = self.cur.fetchall()
##        return result[0][0]
##    
##    def getStack(self,chat_id):
##        self.cur.execute("SELECT value FROM InputStack WHERE chat_id = ? ORDER BY stack_pos ASC",(chat_id,))
##        result = self.cur.fetchall()
##        return result
##
##    def getStackSize(self,chat_id):
##        self.cur.execute("SELECT COUNT(1) FROM InputStack WHERE chat_id = ?",(chat_id,))
##        result = self.cur.fetchall()
##        return result[0][0]
##    
##    def flushStack(self,chat_id):
##        self.cur.execute("DELETE FROM InputStack WHERE chat_id = ?",(chat_id,))
##        self._DB_con.commit()
##
##
##    ##############################################################
##
##    def SetUserID(self,chat_id,UserID):
##        self.cur.execute("SELECT 1 FROM Sessions WHERE chat_id = ?",(chat_id,))
##        if len(self.cur.fetchall()) == 0:
##            self.cur.execute("INSERT INTO Sessions VALUES(?,?)",(chat_id,UserID))
##        else:
##            self.cur.execute("UPDATE Sessions SET UserID = ? WHERE chat_id = ?",(UserID,chat_id))
##        self._DB_con.commit()
##
##    def GetUserID(self,chat_id):
##        self.cur.execute("SELECT UserID FROM Sessions WHERE chat_id = ?",(chat_id,))
##        result = self.cur.fetchall()
##        if len(result) == 0:
##            return -1
##        else:
##            return result[0][0]
##            
##        
##
##    ##############################################################
##
##
##    def reset(self,drop_tables = True):
##        if drop_tables:
##            self.cur.execute("DROP TABLE IF EXISTS InputStack")
##            self.cur.execute("DROP TABLE IF EXISTS Sessions")
##        self.cur.execute("CREATE TABLE IF NOT EXISTS InputStack(chat_id INT , stack_pos INT, value TEXT)")
##        self.cur.execute("CREATE TABLE IF NOT EXISTS Sessions(chat_id INT PRIMARY KEY, UserID INT)")
##        self._DB_con.commit()
##        
    
        
        
            
            
                
        

BOT_TOKEN = "YOUR TOKEN HERE"
if __name__ == "__main__":
    bot = telepot.Bot(BOT_TOKEN)
    heda = Telebot()
    heda.mainLoop()
    print(bot.getMe())
