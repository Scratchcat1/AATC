import telepot,time,random,multiprocessing,AATC_DB,AATC_GPIO
import AATC_Server_002 as AATC_Server


def printUpdates(Bot):
    for item in Bot.getUpdates():
        print(item)

class Telebot:
    def __init__(self,bot,signature = "\nHeda ∞",start_update_id= 0,inputSorterNumber = 4):
        self.bot = bot
        self.signature = signature
        self.update_id = start_update_id
        self.chat_id = 464193112
        self.Update_Queue = []
        self.DB = AATC_DB.DBConnection()
        self.OutputQueue = multiprocessing.Queue()
        
        self.inputSorterNumber = inputSorterNumber
        self.TC_Queue = AATC_GPIO.Create_Controller()
        for ProcessID in range(self.inputSorterNumber):
            self.TC_Queue.put(("Controller","Create_Process",(ProcessID,inputSorter,(self.OutputQueue,))))
        
        

    def setChatID(self,chat_id):
        self.chat_id = chat_id

    def sendMessage(self,message,chat_id = None):
        if chat_id != None:
            self.chat_id = chat_id
        self.bot.sendMessage(self.chat_id,message+self.signature)

    def getUpdate(self):
        if len(self.Update_Queue) ==0:
            updates = []
            while len(updates) == 0:
                updates = self.bot.getUpdates(self.update_id +1)
                if len(updates) != 0:
                    pass
                else:
                    time.sleep(1)
            for item in updates:
                self.update_id = max([self.update_id, item["update_id"]])
                self.Update_Queue.append(item)

        return self.Update_Queue.pop(0)

    
    def textInput(self,Message=""):  #relays message between user and machine
        self.sendMessage(Message,self.chat_id)
        return self.getUpdate()["message"]["text"]

    def mainLoop(self):
        while True:
            try:
                while not self.OutputQueue.empty():  #Sends the messages which have been created.
                    packet = self.OutputQueue.get()
                    self.sendMessage(*packet)
                    
                update = self.bot.getUpdates(self.update_id + 1)
                for packet in update:
                    self.update_id = max([self.update_id,packet["update_id"]])

                    messageText = packet["message"]["text"]
                    chatID = packet["message"]["chat"]["id"]
                    if ord(messageText[0]) >200:  #Deal with emojis -_-
                        continue

                    Thread_Name = chatID % self.inputSorterNumber
                    self.TC_Queue.put((Thread_Name,"ProcessMessage",(messageText,chatID)))
                    
                time.sleep(0.5)
            except:
                pass
        self.TC_Queue.put(("Controller","Exit",(True,)))
            

    def processMessage(self,messageText,chat_id = 0):
        lowerText = messageText.lower()
        response = messageText
        if "time" in lowerText:
            response = str(time.time())

        elif "date" in lowerText:
            response = str(time.strftime("%Y:%m:%d %H:%M:%S"))

        elif "random float" in lowerText:
            response = str(random.random())

        #elif "quote" in lowerText:
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
    def __init__(self,Thread_Name,Input_Queue,OutputQueue,Exec_Processes = 2):
        self.Thread_Name = Thread_Name
        self.Input_Queue = Input_Queue
        self.OutputQueue = OutputQueue
        self.Exec_Processes = Exec_Processes
        
        self.DB = AATC_DB.DBConnection()
        self.ShowCommandsList = ShowCommands()
        self.CommandDictionary = CreateCommandDictionary()

        self.EC_Queue = AATC_GPIO.Create_Controller()
        for ProcessID in range(self.Exec_Processes):
            self.EC_Queue.put(("Controller","Create_Process",(ProcessID,CommandExecutor,(self.OutputQueue,))))

        self.mainLoop()

    def mainLoop(self):
        Exit = False
        while not Exit:
            try:
                data = self.Input_Queue.get()
                command,arguments = data[0],data[1]
                if command == "Exit":
                    Exit = True
                    continue
            
                messageText,chat_id = arguments[0],arguments[1]

                response = self.processInput(messageText,chat_id)
                if response != None:
                    print()
                    print("Message:",messageText)
                    print("Response:",response)
                    self.OutputQueue.put((response,chat_id))
            except Exception as e:
                print("Error in inputSorter",self.Thread_Name,"Error:",e)
        self.EC_Queue.put(("Controller","Exit",(True,)))


    def processInput(self,messageText,chat_id):
        lowerText = messageText.lower()
        try:
            if "/" in messageText:
                if "/cancel" == messageText:
                    self.DB.flushStack(chat_id)
                    return "Command cancelled"
                else:
                    self.DB.flushStack(chat_id)
                    messageText = messageText.replace("/","")
            elif lowerText in ["help","?"]:
                return self.ShowCommandsList
                
                    
            self.DB.addValue(messageText,chat_id)
            
            stack_size = self.DB.getStackSize(chat_id)
            command = self.DB.getCommand(chat_id)
            command_size = len(self.CommandDictionary[command])
            
            if stack_size == command_size+1:
                UserID = self.DB.GetUserID(chat_id)
                stack = self.DB.getStack(chat_id)
                self.DB.flushStack(chat_id)
                
                packet = convertDBStack(stack,self.CommandDictionary)

##                p = multiprocessing.Process(target = AATC_Server.BotConnection, args = (UserID,chat_id,packet,self.OutputQueue))
##                p.start()
                Thread_Name = random.randint(0,self.Exec_Processes-1)
                self.EC_Queue.put((Thread_Name,"RunCommand",(UserID,chat_id,packet)))
                
            else:
                return self.CommandDictionary[command][stack_size]["Query"]
            
        except Exception as e:
            return "Error processing message "+str(e) + "\n" + self.ShowCommandsList





class CommandExecutor:
    def __init__(self,Thread_Name,Input_Queue,OutputQueue):
        self.Thread_Name = Thread_Name
        self.Input_Queue = Input_Queue
        self.OutputQueue = OutputQueue

        self.mainLoop()

    def mainLoop(self):
        Exit = False
        while not Exit:
            try:
                data = self.Input_Queue.get()
                command,arguments = data[0],data[1]
                if command == "Exit":
                    Exit = True
                    continue

                
                elif command == "RunCommand":
                    UserID,chat_id,packet = arguments[0],arguments[1],arguments[2]
                    AATC_Server.BotConnection(UserID,chat_id,packet,self.OutputQueue)

                else:
                    print("CommandExecutor",self.Thread_Name," obtained incorrect command",command)

            except Exception as e:
                print("Exception in CommandExecutor",self.Thread_Name,"Error:",e)
        


















def convertDBStack(result,CommandDictionary):
    result = list(result)
    command = result.pop(0)[0]
    arguments = []
    for i,item in enumerate(result):
        print(item[0])
        arguments.append(CommandDictionary[command][i+1]["Type"](item[0]))
    packet = (command,arguments)
    return packet

def SplitWaypoints(string):
    waypoints = string.split("\n")
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
##        self.db_con = sql.connect("db.name")
##        self.cur = self.db_con.cursor()
##            
##    def addValue(self,value,chat_id):
##        self.cur.execute("SELECT MAX(stack_pos) FROM InputStack WHERE chat_id = ?",(chat_id,))
##        result = self.cur.fetchall()
##        if not result[0][0] == None:
##            stack_pos = result[0][0] +1
##        else:
##            stack_pos = 0
##        self.cur.execute("INSERT INTO InputStack VALUES(?,?,?)",(chat_id,stack_pos,value))
##        self.db_con.commit()
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
##        self.db_con.commit()
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
##        self.db_con.commit()
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
##        self.db_con.commit()
##        
    
        
        
            
            
                
        

BOT_TOKEN = "YOUR TOKEN HERE"
if __name__ == "__main__":
    bot = telepot.Bot(BOT_TOKEN)
    heda = Telebot(bot)
    heda.mainLoop()
    print(bot.getMe())
