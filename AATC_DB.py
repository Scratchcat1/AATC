import sqlite3 as sql
import time
def GetTime():
    return int(time.time())

def CoordLessThanOrEqual(Coord1,Coord2):# True if Coord1 <= Coord2
    List1 = list(Coord1)
    List2 = list(Coord2)
    BoolList = []
    for x in range(len(List1)):  #Goes through each item in the lists
        if List1[x] <= List2[x]:   #If The Coord1[x] <= Coord2[x]
            BoolList.append(True)
    return all(BoolList)


class DBConnection:
    """
    This is the Database connection object for AATC. This provides a DB Connection of other objects using a simple API
    The General form is :
         Sucess,Message,*Data* =  DatabaseConnection . Request( *Arguments* )
         
    A Get...() Function which returns values from a table, the Message will contain a string version of the headers in a list eg '["DroneID","DroneName","OtherColumnName"]
    A Delete/Remove/Add/Set (Things which dont return specific data) will return Sucess,Message 

    !!!THE UserID IS VITAL FOR MOST TRANSACTIONS WHICH REQUIRE A PERMISSION!!! This is to prevent users interfereing with others.
    Many functions will require a UserID. This is a unique number for a Username and can be obtained by DBConnection.GetUserID('Username')
    In the future it may be possible to store the UserID in this object
    
    Table_Headers("TableName") will get the headers of that table
    Reset() will drop all tables and create them again!  THIS CAN TAKE A LONG TIME AND IS PROBABLY NOT THREADSAFE. WILL CRASH OTHER USERS! NOT ACCESSABLE AT ALL RIGHT NOW

    This object is designed more towards security and reliability than performance, therefore more checks occur which can impeed performance
    """

    
    def __init__(self,DatabaseName = "Main.db"):
        print("Initializing database connection '",DatabaseName,"'")
        self.db_con = sql.connect(DatabaseName)
        self.cur = self.db_con.cursor()
        self.cur_header = self.db_con.cursor()

    def Exit(self):
        self.db_con.close()
    def Table_Headers(self,TableName):
        self.cur_header.execute("PRAGMA table_info("+TableName+")")
        result = self.cur_header.fetchall()
        Headers = []
        for item in result:
            Headers.append(item[1])  #Gets Column header
        return Headers

########################    DRONE           ################################ 
    def AddDrone(self,UserID,DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight):
        self.cur.execute("SELECT 1 FROM Drone WHERE UserID = ? AND DroneName = ?",(UserID,DroneName))
        if self.cur.fetchall() == []:
            self.cur.execute("INSERT INTO Drone(UserID,DroneName,DroneType,DroneSpeed,DroneRange,DroneWeight,FlightsFlown,LastCoords,LastBattery) VALUES(?,?,?,?,?,?,0,'(0,0,0)',0)",(UserID,DroneName,DroneType,DroneSpeed,DroneRange,DroneWeight))
            _,_,DroneID = self.GetDroneID(UserID,DroneName)
            DroneID = DroneID[0][0]                               #Sets up password in seperate table for maintainance security
            self.cur.execute("INSERT INTO DroneCredentials(DroneID,DronePassword) VALUES(?,?)",(DroneID,DronePassword))
            return True,"Added Drone"
        else:
            return False,"This drone already exists for you"
        
    def RemoveDrone(self,UserID,DroneID):
        self.cur.execute("SELECT 1 FROM Drone WHERE UserID = ? AND DroneID = ?",(UserID,DroneID))  #If drone belongs to user
        if self.cur.fetchall() != []:
            self.cur.execute("DELETE FROM Drone WHERE DroneID = ?",(DroneID,))
            self.cur.execute("DELETE FROM DroneCredentials WHERE DroneID = ?",(DroneID,))
            return True,"Removed Drone"
        else:
            return False,"This drone does not exist or you do not have permission to delete this drone"

    def DroneCheckCredentials(self,DroneID,DronePassword):
        self.cur.execute("SELECT 1 FROM DroneCredentials WHERE DroneID = ? AND DronePassword = ?",(DroneID,DronePassword))
        DroneIDFetch = self.cur.fetchall()
        if DroneIDFetch != []:
            return True,"Correct Drone Credentials",DroneIDFetch[0][0]
        else:
            return False,"Incorrect Drone Credentials",-1
            

        
    def GetDroneID(self,UserID,DroneName):
        self.cur.execute("SELECT DroneID FROM Drone WHERE UserID = ? AND DroneName = ?",(UserID,DroneName))
        return True,"['DroneID']",self.cur.fetchall()

    def GetDroneCredentials(self,UserID,DroneID):
        self.cur.execute("SELECT DroneCredentials.* FROM Drone,DroneCredentials WHERE Drone.UserID = ? AND Drone.DroneID = DroneCredentials.DroneID AND DroneCredentials.DroneID = ?",(UserID,DroneID))
        return True,str(self.Table_Headers("DroneCredentials")),self.cur.fetchall()

    def SetDroneCredentials(self,UserID,DroneID,DronePassword):
        self.cur.execute("SELECT 1 FROM Drone WHERE Drone.UserID = ? AND Drone.DroneID = ?",(UserID,DroneID))
        if self.cur.fetchall() != []:
            self.cur.execute("UPDATE DroneCredentials SET DronePassword = ? WHERE DroneID = ?",(DronePassword,DroneID))
            return True,"Updated Drone Credentials"
        else:
            return False,"This drone does not exist or you do not have permission to change it's credentials"

    def CheckDroneOwnership(self,UserID,DroneID):
        self.cur.execute("SELECT 1 FROM Drone WHERE UserID = ? AND DroneID = ?",(UserID,DroneID))
        return True,"['DroneOwnership']",self.cur.fetchall()

    def GetDroneInfo(self,UserID,DroneID):
        self.cur.execute("SELECT Drones.* FROM Drones,User WHERE Drone.DroneID = ? AND (Drone.UserID = ? OR (Drone.UserID = User.UserID AND User.PublicVisibleFlights = 1))",(DroneID,UserID))
        return True,str(self.Table_Headers("Drone")),self.cur.fetchall()
            
    def GetDronesUser(self,UserID):
        self.cur.execute("SELECT * FROM Drone WHERE UserID = ?",(UserID,))
        return True,str(self.Table_Headers("Drone")),self.cur.fetchall()
    def GetDronesAll(self):
        self.cur.execute("SELECT Drone.* FROM User,Drone WHERE User.UserID = Drone.UserID AND User.PublicVisibleFlights = 1")
        return True,str(self.Table_Headers("Drone")),self.cur.fetchall()

    def UpdateDroneStatus(self,DroneID,LastCoords,LastBattery):
        self.cur.execute("UPDATE Drone SET LastCoords = ?,LastBattery = ? WHERE DroneID = ?",(LastCoords,LastBattery,DroneID))
        return True,"Updated Drone Status"

##########################   USER         #############################
    
    def GetUserID(self,Username):
        self.cur.execute("SELECT UserID FROM User WHERE Username = ?",(Username,))
        return True,"['UserID']",self.cur.fetchall()
    def GetUsername(self,UserID):
        self.cur.execute("SELECT Username FROM User WHERE UserID = ?",(UserID,))
        return True,"['Username']",self.cur.fetchall()
    
    def AddUser(self,Username,Password):
        self.cur.execute("SELECT 1 FROM User WHERE Username = ?",(Username,))
        if self.cur.fetchall() == []:
            self.cur.execute("INSERT INTO User(Username,Password,PublicVisibleFlights,AccountType) VALUES(?,?,0,'Default')",(Username,Password))
            return True,"Added User"
        else:
            return False,"User already exists"

    def CheckCredentials(self,Username,Password):
        self.cur.execute("SELECT UserID FROM User WHERE Username = ? AND Password = ?",(Username,Password))
        UserIDFetch = self.cur.fetchall()
        if UserIDFetch != []:
            return True,"Correct Credentials",UserIDFetch[0][0]
        else:
            return False,"Incorrect Credentials",-1

    def SetUserPublicVisibleFlights(self,UserID,Value):
        if Value in [0,1]:
            self.cur.execute("UPDATE User SET PublicVisibleFlights = ? WHERE UserID = ?",(Value,UserID))
            return True,"Changed PublicVisibleFlights Value"
        else:
            return False,"Invalid PublicVisibleFlights Value"
    def SetAccountType(self,UserID,Value):
        self.cur.execute("UPDATE User SET AccountType =? WHERE UserID = ? ",(Value,UserID))
        return True,"Set AccountType Value"

#####################          FLIGHT          ##############################

    def GetFlightsUser(self,UserID):
        self.cur.execute("SELECT Flight.* FROM Flight,Drone WHERE Flight.DroneID = Drone.DroneID AND Drone.UserID = ?",(UserID,))
        return True,str(self.Table_Headers("Flight")),self.cur.fetchall()

    
    def GetFlightsAll(self):
        self.cur.execute("SELECT Flight.* FROM Flight,Drone,User WHERE Flight.DroneID = Drone.DroneID AND Drone.UserID = User.UserID AND User.PublicVisibleFlights = 1")
        return True,str(self.Table_Headers("Flight")),self.cur.fetchall()

    def AddFlight(self,UserID,DroneID,StartCoords,EndCoords,StartTime,ETA,EndTime,Distance,XOffset,YOffset,ZOffset):
        self.cur.execute("SELECT 1 FROM User,Drone WHERE Drone.DroneID = ? AND Drone.UserID = ?",(DroneID,UserID))
        if self.cur.fetchall() !=[]:
            self.cur.execute("INSERT INTO Flight(DroneID,StartCoords,EndCoords,StartTime,ETA,EndTime,Distance,XOffset,YOffset,ZOffset,Completed) VALUES(?,?,?,?,?,?,?,?,?,?,0)",(DroneID,str(StartCoords),str(EndCoords),StartTime,ETA,EndTime,Distance,XOffset,YOffset,ZOffset))
            return True,"Flight added"
        else:
            return False,"You do not have permission to launch this drone"
        
    def RemoveFlight(self,UserID,FlightID):
        self.cur.execute("SELECT 1 FROM Flight,Drone,User WHERE Flight.FlightID = ? AND Flight.DroneID = Drone.DroneID AND Drone.UserID = ?",(FlightID,UserID))  #If User owns this drone
        if self.cur.fetchall() != []:
            self.cur.execute("DELETE FROM Flight WHERE FlightID = ?",(FlightID,))
            return True,"Flight Removed"
        else:
            return False,"You do not have permission to remove this flight"

    def CheckForFlight(self,DroneID,MaxLookAheadTime):
        self.cur.execute("SELECT FlightID FROM Flight WHERE DroneID = ? AND (StartTime - ?) < ? ORDER BY StartTime ASC LIMIT 1",(DroneID,MaxLookAheadTime,GetTime()))
        FlightIDFetch = self.cur.fetchall()
        if FlightIDFetch != []:
            return True,"Flight is available",FlightIDFetch
        else:
            return False,"Flight is not available",[]

    def GetFlight(self,DroneID,FlightID):
        self.cur.execute("SELECT * FROM Flight WHERE DroneID = ? AND FlightID = ?",(DroneID,FlightID))
        FlightFetch = self.cur.fetchall()
        if FlightFetch != []:
            return True,str(self.Table_Headers("Flight")),FlightFetch
        else:
            return False,"Flight not obtained, Flight may not exist or you may not have permission",[]

    def MarkFlightComplete(self,DroneID,FlightID):
        self.cur.execute("SELECT 1 FROM Flight WHERE DroneID = ? AND FlightID = ?",(DroneID,FlightID))
        if self.cur.fetchall != []:
            self.cur.execute("UPDATE Flight SET Completed = 1,EndTime = ? WHERE FlightID = ?",(FlightID,GetTime()))
            return True,"Marked Flight complete"
        else:
            return False,"You do not have permission to mark this flight complete"
        
#----------------------------  FLIGHT WAYPOINT------------------------------------
    def GetFlightWaypoints(self,DroneID,FlightID):
        self.cur.execute("SELECT FlightWaypoints.* FROM Flight,FlightWaypoints WHERE Flight.DroneID = ? AND Flight.FlightID = FlightWaypoints.FlightID AND FlightWaypoints.FlightID = ?",(DroneID,FlightID))
        return True,str(self.Table_Headers("FlightWaypoints")),self.cur.fetchall()          
    
    def GetFlightWaypointsUser(self,UserID):
        self.cur.execute("SELECT * FROM FlightWaypoints,Flight,Drone WHERE FlightWaypoints.FlightID = Flight.FlightID AND Flight.DroneID = Drone.DroneID AND Drone.UserID = ? ORDER BY FlightWaypoints.FlightID, FlightWaypoints.WaypointNumber",(UserID,))
        return True,str(self.Table_Headers("FlightWaypoints")),self.cur.fetchall()
    
    def GetFlightWaypointsAll(self):
        self.cur.execute("SELECT FlightWaypoints.* FROM FlightWaypoints,Flight,Drone,User WHERE FlightWaypoints.FlightID = Flight.FlightID AND Flight.DroneID = Drone.DroneID AND Drone.UserID = User.UserID AND User.PublicVisibleFlights = 1 ORDER BY FlightWaypoints.FlightID,FlightWaypoints.WaypointNumber")
        return True,str(self.Table_Headers("FlightWaypoints")),self.cur.fetchall()
    
    def AddWaypoint(self,UserID,FlightID,WaypointNumber,Coords,ETA,BlockTime=0):
        self.cur.execute("SELECT 1 FROM User,Flight,Drone WHERE User.UserID = ? AND User.UserID = Drone.UserID AND Drone.DroneID = Flight.DroneID AND Flight.FlightID = ?",(UserID,FlightID))
        if self.cur.fetchall() !=[]:
            self.cur.execute("INSERT INTO FlightWaypoints(FlightID,WaypointNumber,Coords,ETA,BlockTime) VALUES(?,?,?,?,?)",(FlightID,WaypointNumber,Coords,ETA,BlockTime))
            return True,"Added Waypoint"
        else:
            return False,"You do not have permission to add a waypoint for this flight"
        
    def RemoveFlightWaypoints(self,UserID,FlightID):
        self.cur.execute("SELECT 1 FROM User,Flight,Drone WHERE User.UserID = ? AND User.UserID = Drone.UserID AND Drone.DroneID = Flight.DroneID AND Flight.FlightID = ?",(UserID,FlightID))
        if self.cur.fetchall() !=[]:
            self.cur.execute("DELETE FROM FlightWaypoints WHERE FlightID = ?",(FlightID,))
            return True,"Deleted waypoint"
        else:
            return False,"You do not have permission to delete these waypoints"




###########################  MONITOR     ##################################
    def AddMonitor(self,MonitorName,MonitorPassword):
        self.cur.execute("SELECT 1 FROM Monitor WHERE MonitorName = ?",(MonitorName,))
        if self.cur.fetchall() == []:
            self.cur.execute("INSERT INTO Monitor(MonitorName,MonitorPassword,AccountType) VALUES(?,?,'Default')",(MonitorName,MonitorPassword))
            return True,"Added Monitor"
        else:
            return False,"Monitor already exists"

    def MonitorCheckCredentials(self,MonitorName,MonitorPassword):
        self.cur.execute("SELECT MonitorID FROM Monitor WHERE MonitorName = ? AND MonitorPassword = ?",(MonitorName,MonitorPassword))
        MonitorIDFetch = self.cur.fetchall()
        if MonitorIDFetch != []:
            return True,"Correct Credentials",MonitorIDFetch[0][0]
        else:
            return False,"Incorrect Credntials",-1

    def GetMonitorDrones(self,MonitorID):
        self.cur.execute("SELECT Drone.* FROM Drone,MonitorPermission WHERE Drone.UserID = MonitorPermission.UserID and MonitorPermission.MonitorID = ?",(MonitorID,))
        return True,str(self.Table_Headers("Drone")),self.cur.fetchall()
    
    def GetMonitorFlights(self,MonitorID):
        self.cur.execute("SELECT Flight.* FROM Flight,Drone,MonitorPermission WHERE Flight.DroneID = Drone.DroneID AND Drone.UserID = MonitorPermission.UserID and MonitorPermission.MonitorID = ?",(MonitorID,))
        return True,str(self.Table_Headers("Flight")),self.cur.fetchall()
    
    def GetMonitorFlightWaypoints(self,MonitorID):
        self.cur.execute("SELECT FlightWaypoints.* FROM FlightWaypoints,Flight,Drone,MonitorPermission WHERE FlightWaypoints.FlightID = Flight.FlightID AND Flight.DroneID = Drone.DroneID AND Drone.UserID = MonitorPermission.UserID and MonitorPermission.MonitorID = ?",(MonitorID,))
        return True,str(self.Table_Headers("FlightWaypoints")),self.cur.fetchall()

    def GetMonitorID(self,MonitorName):
        self.cur.execute("SELECT MonitorID FROM Monitor WHERE MonitorName = ?",(MonitorName,))
        if len(self.cur.fetchall()) != 0:
            Sucess = True
        else:
            Sucess = False
        return Sucess,"[MonitorID]",self.cur.fetchall()
    def GetMonitorName(self,MonitorID):
        self.cur.execute("SELECT MonitorName FROM Monitor WHERE MonitorID = ?",(MonitorID,))
        return True,"[MonitorName]",self.cur.fetchall()


#--------------------------   MONITOR PERMISSION   ------------------------------------
    def AddMonitorPermission(self,UserID,MonitorID,ExpiryDate):
        self.cur.execute("SELECT 1 FROM MonitorPermission WHERE UserID = ? AND MonitorID = ?",(UserID,MonitorID))
        if self.cur.fetchall() ==[]:
            self.cur.execute("INSERT INTO MonitorPermission(MonitorID,UserID,LastAccessed,ExpiryDate) VALUES (?,?,?,?)",(MonitorID,UserID,0,ExpiryDate))
            return True,"Sucessfully added MonitorPermission"
        else:
            return False,"MonitorPermission already exists"

    def RemoveMonitorPermission(self,UserID,MonitorID):
        self.cur.execute("DELETE FROM MonitorPermission WHERE UserID = ? AND MonitorID = ?",(UserID,MonitorID))
        return True,"Deleted MonitorPermission"

    def ModifyMonitorPermissionDate(self,UserID,MonitorID,NewDate):
        self.cur.execute("UPDATE MonitorPermission SET ExpiryDate = ? WHERE UserID = ? AND MonitorID = ?",(NewDate,UserID,MonitorID))
        return True,"Updated Date for MonitorPermission"
    def GetMonitorPermissionUser(self,UserID):
        self.cur.execute("SELECT * FROM MonitorPermission WHERE UserID = ?",(UserID,))
        Headers = self.Table_Headers("MonitorPermission")
        return True,str(Headers),self.cur.fetchall()
    def GetMonitorPermissionMonitor(self,MonitorID):
        self.cur.execute("SELECT * FROM MonitorPermission WHERE MonitorID = ?",(MonitorID,))
        Headers = self.Table_Headers("MonitorPermission")
        return True,str(Headers),self.cur.fetchall()
    def UpdateMonitorPermissionLastAccessed(self,UserID,MonitorID,NewDate = None):
        if NewDate == None:
            NewDate = GetTime()
        self.cur.execute("UPDATE MonitorPermission SET LastAccessed = ? WHERE MonitorID = ? AND UserID = ?",(NewDate,MonitorID,UserID))
        return True,"Updated LastAccessed"


########################    No Fly Zone ###############################################
    def AddNoFlyZone(self,Coord1,Coord2,Level,UserID):
        if not CoordLessThanOrEqual(Coord1,Coord2):  #If Coord2 is closer to origin in every point than Coord1 It is an invalid coordinate
            Message = "Invalid Coordinates. Coordinate 2:"+str(Coord2)+" is closer in all dimentions to the origin than Coordinate 1"+str(Coord1)
            return False,Message
        else:
            if type(Level) is not int or Level <= 0:
                return False, "Invalid Level. Must be an integer and > 0"
            self.cur.execute("SELECT 1 FROM User WHERE UserID = ? AND AccountType = 'ZoneCreator'",(UserID,))
            if self.cur.fetchall() !=  []:
                self.cur.execute("INSERT INTO NoFlyZone(StartCoord,EndCoord,Level,OwnerUserID) VALUES(?,?,?,?)",(str(Coord1),str(Coord2),Level,UserID))
                return True,"Sucessfully added NoFlyZone"
            else:
                return False,"You do not have ZoneCreator Permission"
    def RemoveNoFlyZone(self,UserID,ZoneID):
        self.cur.execute("SELECT 1 FROM NoFlyZone,User WHERE (NoFlyZone.ZoneID = ? AND NoFlyZone.OwnerUserID = ? ) OR (User.UserID = ? AND 'ZoneRemover' IN User.AccountType)",(ZoneID,UserID,UserID))   # Gets 1 if (Zone with ZoneID has UserID as owner) OR (User with UserID has ZoneRemoverPermission) 
        if self.cur.fetchall() != []:
            #Runs if user has permission to delete this no fly zone
            self.cur.execute("DELETE FROM NoFlyZone WHERE ZoneID = ?",(ZoneID,))
            return True,"Sucessfully deleted NoFlyZone"
        else:
            return False,"You do not own this NoFlyZone or you do not have the ZoneRemoverPermission"   #Replace String permission with max no fly zone level permission
        

    def ModifyNoFlyZoneLevel(self,UserID,ZoneID,Level):
        if type(Level) is not int or Level <=0:
            return False,"Invalid Level. Must be an integer and > 0"
        self.cur.execute("SELECT 1 FROM NoFlyZone,User WHERE (NoFlyZone.ZoneID = ? AND NoFlyZone.OwnerUserID = ? ) OR (User.UserID = ? AND 'ZoneModifier' IN User.AccountType)",(ZoneID,UserID,UserID))   # Gets 1 if (Zone with ZoneID has UserID as owner) OR (User with UserID has ZoneModifier Permission) 
        if self.cur.fetchall() != []:
            #Runs if user has permission to delete this no fly zone
            self.cur.execute("UPDATE NoFlyZone SET Level = ? WHERE ZoneID = ?",(Level,ZoneID))
            return True,"Sucessfully modified NoFlyZone"
        else:
            return False,"You do not own this NoFlyZone or you do not have the ZoneModifier Permission"   #Replace String permission with max no fly zone level permission    

    def GetNoFlyZones(self):
        self.cur.execute("SELECT * FROM NoFlyZone")
        Headers = self.Table_Headers("NoFlyZone")    #Gets Headers of table to be sent as message
        return True,str(Headers),self.cur.fetchall()


##########################################################################    
        
    def ResetDatabase(self):
        TABLES = ["User","Drone","Monitor","MonitorPermission","Flight","FlightWaypoints","NoFlyZone","DroneCredentials"]
        for item in TABLES:
            self.cur.execute("DROP TABLE IF EXISTS {0}".format(item))
        
        self.cur.execute("CREATE TABLE User(UserID INTEGER PRIMARY KEY, Username TEXT,Password TEXT, PublicVisibleFlights INT, AccountType TEXT)")
        self.cur.execute("CREATE TABLE Drone(DroneID INTEGER PRIMARY KEY, UserID INT, DroneName TEXT, DroneType TEXT, DroneSpeed INT, DroneRange INT, DroneWeight REAL, FlightsFlown INT, LastCoords TEXT, LastBattery REAL,FOREIGN KEY(UserID) REFERENCES User(UserID))")
        self.cur.execute("CREATE TABLE Monitor(MonitorID INTEGER PRIMARY KEY, MonitorName TEXT, MonitorPassword TEXT,AccountType TEXT)")
        self.cur.execute("CREATE TABLE MonitorPermission(MonitorID INT ,UserID INT, LastAccessed TEXT, ExpiryDate TEXT,PRIMARY KEY(MonitorID,UserID),FOREIGN KEY(MonitorID) REFERENCES Monitor(MonitorID),FOREIGN KEY(UserID) REFERENCES User(UserID))")
        self.cur.execute("CREATE TABLE Flight(FlightID INTEGER PRIMARY KEY, DroneID INT, StartCoords TEXT, EndCoords TEXT, StartTime TEXT, ETA TEXT, EndTime TEXT, Distance  REAL,XOffset REAL , YOffset REAL , ZOffset REAL,Completed INT,FOREIGN KEY(DroneID) REFERENCES Drone(DroneID))")
        self.cur.execute("CREATE TABLE FlightWaypoints(FlightID INT, WaypointNumber INT, Coords TEXT, ETA TEXT, BlockTime INT ,FOREIGN KEY(FlightID) REFERENCES Flight(FlightID))")
        self.cur.execute("CREATE TABLE NoFlyZone(ZoneID INTEGER PRIMARY KEY, StartCoord TEXT, EndCoord TEXT, Level INT, OwnerUserID INT,FOREIGN KEY(OwnerUserID) REFERENCES User(UserID))")
        self.cur.execute("CREATE TABLE DroneCredentials(DroneID INTEGER PRIMARY KEY ,DronePassword TEXT,FOREIGN KEY(DroneID) REFERENCES Drone(DroneID))")
        
    

