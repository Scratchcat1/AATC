import telepot,time,random,multiprocessing
import AATC_Server_002 as AATC_Server



def printUpdates(Bot):
    for item in Bot.getUpdates():
        print(item)

class Telebot:
    def __init__(self,bot,signature = "\nHeda ∞",start_update_id= 0):
        self.bot = bot
        self.signature = signature
        self.update_id = start_update_id
        self.chat_id = 464193112
        self.Update_Queue = []
        self.DB = DB_Connection()

    def setChatID(self,chat_id):
        self.chat_id = chat_id

    def sendMessage(self,message):
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
        self.bot.sendMessage(self.chat_id, Message + self.signature)
        return self.getUpdate()["message"]["text"]

    def sendMessage(self,Message):
        self.bot.sendMessage(self.chat_id,Message+self.signature)

    def mainLoop(self):
        self.update_id = 0
        while True:
            update = self.bot.getUpdates(self.update_id + 1)
            for packet in update:
                self.update_id = max([self.update_id,packet["update_id"]])

                messageText = packet["message"]["text"]
                chatID = packet["message"]["chat"]["id"]
                if ord(messageText[0]) >200:  #Deal with emojis -_-
                    continue

                response = self.inputSorter(messageText,chatID)
                if response != None:
                    print()
                    print("Message:",messageText)
                    print("Response:",response)

                    self.bot.sendMessage(chatID,response+self.signature)
                
            time.sleep(1)
            

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

    def inputSorter(self,text,chat_id):
        try:
            if "/" in text:
                if "/cancel" == text:
                    self.DB.flushStack(chat_id)
                    return "Command cancelled"
                else:
                    self.DB.flushStack(chat_id)
                    text = text.replace("/","")
                    
            self.DB.addValue(text,chat_id)
            
            stack_size = self.DB.getStackSize(chat_id)
            
            command = self.DB.getCommand(chat_id)
            CommandDictionary = CreateCommandDictionary()
            
            command_size = len(CommandDictionary[command])
            
            if stack_size == command_size+1:
                stack = self.DB.getStack(chat_id)
                packet = convertDBStack(stack,CommandDictionary)
                
                UserID = self.DB.GetUserID(chat_id)
                result = packet


                p = multiprocessing.Process(target = AATC_Server.BotConnection, args = (UserID,chat_id,packet))
                p.start()
                #return "I did something"+str(result)+ " for the userID "+str(UserID)
            else:
                return CommandDictionary[command][stack_size]["Query"]
            
        except Exception as e:
            return "Error processing message "+str(e)
    
class StringStack:
    def __init__(self):
        self.stack = []
    def load_stack(self,string):
        self.stack = ast.literal_eval(string)
    def push(self,item):
        self.stack.append(item)
    def pop(self):
        return self.stack.pop()
    def __str__(self):
        return str(self.stack)
    def __len__(self):
        return len(self.stack)


def convertStack(stack):
    arguments = []
    while len(stack) > 1:
        arguments.append(stack.pop())
    command = stack.pop()
    packet = (command,arguments)
    return packet

def convertDBStack(result,CommandDictionary):
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


def CreateCommandDictionary():
    Commands = {}
    # Format Commands["Commnad String"] = {ArgumentNumber:{"Quergy":"Query text","Type":type of response eg int. Must be callable }}
    Commands["Login"] = {1:{"Query":"Enter Username","Type":str},
                          2:{"Query":"Enter Password","Type":str}}

    Commands["GetNoFlyZones"] = {}
    Commands["AddNoFlyZone"] = {1: {'Type': str, 'Query': 'Enter first coordinate'},
                                2: {'Type': str, 'Query': 'Enter second coordinate'},
                                3: {'Type': int, 'Query': 'Enter level of NoFlyZone'}}

    
    Commands["ModifyNoFlyZoneLevel"] = {1: {'Type': int, 'Query': 'Enter ZoneID'},
                                        2: {'Type': int, 'Query': 'Enter new level of Zone'}}




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

    Commands["GetUserID"]= {1: {'Query': 'Enter Username', 'Type': str}}
    Commands["GetUsername"]= {1: {'Query': 'Enter UserID', 'Type': int}}

    Commands["AddUser"]= {1: {'Query': 'Enter Username', 'Type': str},
                          2: {'Query': 'Enter Password', 'Type': str}}

    Commands["SetFlightVisibility"]= {1: {'Query': 'Enter Visibility', 'Type': int}}

    Commands["SetAccountType"]= {1: {'Query': 'Enter Permission', 'Type': str},
                                 2: {'Query': 'Enter Account Type', 'Type': int}}


    Commands["GetFlightsUser"]= {}
    Commands["GetFlightsAll"]= {}

    Commands["AddFlight"]= {1: {'Query': 'Enter DroneID', 'Type': int},
                            2: {'Query': 'Enter waypoints in single message in brackets split by returns', 'Type': SplitWaypoints},
                            3: {'Query': 'Enter StartTime', 'Type': int}}


    Commands["RemoveFlight"]= {1: {'Query': 'Enter FlightID', 'Type': int}}

    Commands["GetFlightWaypointsUser"]= {}
    Commands["GetFlightWaypointsAll"]= {}

    Commands["GetMonitorID"]= {1: {'Query': 'Enter MonitorName', 'Type': str}}
    Commands["GetMonitorName"]= {1: {'Query': 'Enter MonitorID', 'Type': int}}

    Commands["AddMonitorPermission"]= {1: {'Query': 'Enter MonitorID', 'Type': int},
                                       2: {'Query': 'Enter Expiry Date', 'Type': int}}

    Commands["RemoveMonitorPermission"]= {1: {'Query': 'Enter MonitorID', 'Type': int}}

    Commands["ModifyMonitorPermissionDate"]= {1: {'Query': 'Enter MonitorID', 'Type': int},
                                              2: {'Query': 'Enter New Expiry Date', 'Type': int}}

    Commands["GetMonitorPermissionUser"]= {}

    return Commands

        
import sqlite3 as sql    
class DB_Connection:
    def __init__(self):
        self.db_con = sql.connect("db.name")
        self.cur = self.db_con.cursor()
            
    def addValue(self,value,chat_id):
        self.cur.execute("SELECT MAX(stack_pos) FROM InputStack WHERE chat_id = ?",(chat_id,))
        result = self.cur.fetchall()
        if not result[0][0] == None:
            stack_pos = result[0][0] +1
        else:
            stack_pos = 0
        self.cur.execute("INSERT INTO InputStack VALUES(?,?,?)",(chat_id,stack_pos,value))
        self.db_con.commit()
    
    def getCommand(self,chat_id):
        self.cur.execute("SELECT value FROM InputStack WHERE chat_id = ? AND stack_pos = 0",(chat_id,))
        result = self.cur.fetchall()
        return result[0][0]
    
    def getStack(self,chat_id):
        self.cur.execute("SELECT value FROM InputStack WHERE chat_id = ? ORDER BY stack_pos ASC",(chat_id,))
        result = self.cur.fetchall()
        return result

    def getStackSize(self,chat_id):
        self.cur.execute("SELECT COUNT(1) FROM InputStack WHERE chat_id = ?",(chat_id,))
        result = self.cur.fetchall()
        return result[0][0]
    
    def flushStack(self,chat_id):
        self.cur.execute("DELETE FROM InputStack WHERE chat_id = ?",(chat_id,))
        self.db_con.commit()


    ##############################################################

    def SetUserID(self,chat_id,UserID):
        self.cur.execute("SELECT 1 FROM Sessions WHERE chat_id = ?",(chat_id,))
        if len(self.cur.fetchall()) == 0:
            self.cur.execute("INSERT INTO Sessions VALUES(?,?)",(chat_id,UserID))
        else:
            self.cur.execute("UPDATE Sessions SET UserID = ? WHERE chat_id = ?",(UserID,chat_id))
        self.db_con.commit()

    def GetUserID(self,chat_id):
        self.cur.execute("SELECT UserID FROM Sessions WHERE chat_id = ?",(chat_id,))
        result = self.cur.fetchall()
        if len(result) == 0:
            return -1
        else:
            return result[0][0]
            
        

    ##############################################################


    def reset(self,drop_tables = True):
        if drop_tables:
            self.cur.execute("DROP TABLE IF EXISTS InputStack")
            self.cur.execute("DROP TABLE IF EXISTS Sessions")
        self.cur.execute("CREATE TABLE IF NOT EXISTS InputStack(chat_id INT , stack_pos INT, value TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS Sessions(chat_id INT PRIMARY KEY, UserID INT)")
        self.db_con.commit()
        
    
        
        
            
            
                
        

BOT_TOKEN = "YOU TOKEN HERE"
if __name__ == "__main__":
    bot = telepot.Bot(BOT_TOKEN)
    print(bot.getMe())
