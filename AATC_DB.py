import MySQLdb as sql
import time,codecs
from Crypto.Protocol.KDF import PBKDF2
def GetTime():
    return int(time.time())

def CoordLessThanOrEqual(Coord1,Coord2):# True if Coord1 <= Coord2
    List1 = list(Coord1)
    List2 = list(Coord2)
    BoolList = []
    for x in range(len(List1)):  #Goes through each item in the lists
        if List1[x] <= List2[x]:   #If The Coord1[x] <= Coord2[x]
            BoolList.append(True)
        else:
            BoolList.append(False)
    return all(BoolList)


def Hash(value,salt):
    return str(PBKDF2(codecs.encode(value),codecs.encode(salt)))  #str(PBKDF2(codecs.encode(value),codecs.encode(salt),dkLen = 32))



class DBConnection:
    """
    This is the Database connection object for AATC. This provides a DB Connection of other objects using a simple API
    The General form is :
         Sucess,Message,*Data* =  DatabaseConnection . Request( *Arguments* )

    General behaviour:
    A Get...() Function which returns values from a table, the Message will contain a string version of the headers in a list eg '["DroneID","DroneName","OtherColumnName"]
    A Delete/Remove/Add/Set (Things which dont return specific data) will return Sucess,Message 

    !!!THE UserID IS VITAL FOR MOST TRANSACTIONS WHICH REQUIRE A PERMISSION!!! This is to prevent users interfereing with others.
    Many functions will require a UserID. This is a unique number for a Username and can be obtained by DBConnection.GetUserID('Username')
    
    Table_Headers("TableName") will get the headers of that table
    Reset() will drop all tables and create them again!  THIS CAN TAKE A LONG TIME AND IS PROBABLY NOT THREADSAFE. WILL CRASH OTHER USERS! 
    """

    
    def __init__(self):
        print("Initializing database connection ")
        self._db_con = sql.connect("localhost","AATC_Server","password","AATC_Database")        #Connects to mysql server
        self._cur = self._db_con.cursor()
        self._cur_header = self._db_con.cursor()

    def Exit(self):
        self._db_con.close()
    def Table_Headers(self,TableName):      #Function get the column names for a table in order to allow the client to identify what each column is for.
        self._cur_header.execute("SHOW COLUMNS FROM "+ TableName)  # Cannot use placeholders when referencing the table name , syntax error
        result = self._cur_header.fetchall()
        Headers = []
        for item in result:
            Headers.append(item[0])  #Gets Column header
        return Headers

########################    DRONE           ################################ 
    def AddDrone(self,UserID,DroneName,DronePassword,DroneType,DroneSpeed,DroneRange,DroneWeight):
        self._cur.execute("SELECT 1 FROM Drone WHERE UserID = %s AND DroneName = %s",(UserID,DroneName))
        if self._cur.fetchall() == ():
            self._cur.execute("INSERT INTO Drone(UserID,DroneName,DroneType,DroneSpeed,DroneRange,DroneWeight,FlightsFlown,LastCoords,LastBattery) VALUES(%s,%s,%s,%s,%s,%s,0,'(0,0,0)',0)",(UserID,DroneName,DroneType,DroneSpeed,DroneRange,DroneWeight))
            _,_,DroneID = self.GetDroneID(UserID,DroneName)
            DroneID = DroneID[0][0]                               #Sets up password in seperate table for maintainance security( if SELECT * were used the password would be disclosed in plaintext
            self._cur.execute("INSERT INTO DroneCredentials(DroneID,DronePassword) VALUES(%s,%s)",(DroneID,DronePassword))
            self._db_con.commit()
            return True,"Added Drone"
        else:
            return False,"This drone already exists for you"
        
    def RemoveDrone(self,UserID,DroneID):   #Delete a drone
        self._cur.execute("SELECT 1 FROM Drone WHERE UserID = %s AND DroneID = %s",(UserID,DroneID))  #If drone belongs to user
        if self._cur.fetchall() != ():
            self._cur.execute("DELETE FROM Drone WHERE DroneID = %s",(DroneID,))
            self._cur.execute("DELETE FROM DroneCredentials WHERE DroneID = %s",(DroneID,))
            self._db_con.commit()
            return True,"Removed Drone"
        else:
            return False,"This drone does not exist or you do not have permission to delete this drone"

    def DroneCheckCredentials(self,DroneID,DronePassword):
        self._cur.execute("SELECT DroneID FROM DroneCredentials WHERE DroneID = %s AND DronePassword = %s",(DroneID,DronePassword))     #Search if login is correct
        DroneIDFetch = self._cur.fetchall()
        if DroneIDFetch != ():
            return True,"Correct Drone Credentials",DroneIDFetch[0][0]
        else:
            return False,"Incorrect Drone Credentials",-1

    def DroneGetDroneInfo(self,DroneID):    #Function to allow drone to get information about itself
        self._cur.execute("SELECT * FROM Drone WHERE DroneID = %s",(DroneID,))
        return True,str(self.Table_Headers("Drone")),self._cur.fetchall()
        
            

        
    def GetDroneID(self,UserID,DroneName):  #Gets the drone ID for a given drone name and userID
        self._cur.execute("SELECT DroneID FROM Drone WHERE UserID = %s AND DroneName = %s",(UserID,DroneName))
        return True,"['DroneID']",self._cur.fetchall()

    def GetDroneCredentials(self,UserID,DroneID):   #Obtains the drone's credentials
        self._cur.execute("SELECT DroneCredentials.* FROM Drone,DroneCredentials WHERE Drone.UserID = %s AND Drone.DroneID = DroneCredentials.DroneID AND DroneCredentials.DroneID = %s",(UserID,DroneID))
        return True,str(self.Table_Headers("DroneCredentials")),self._cur.fetchall()

    def SetDroneCredentials(self,UserID,DroneID,DronePassword):     #Alters the drones credentials
        self._cur.execute("SELECT 1 FROM Drone WHERE Drone.UserID = %s AND Drone.DroneID = %s",(UserID,DroneID))    #Checks the user owns the drone
        if self._cur.fetchall() != ():
            self._cur.execute("UPDATE DroneCredentials SET DronePassword = %s WHERE DroneID = %s",(DronePassword,DroneID))
            self._db_con.commit()
            return True,"Updated Drone Credentials"
        else:
            return False,"This drone does not exist or you do not have permission to change it's credentials"

    def CheckDroneOwnership(self,UserID,DroneID):   #Checks if a user owns the drone
        self._cur.execute("SELECT 1 FROM Drone WHERE UserID = %s AND DroneID = %s",(UserID,DroneID))
        return True,"['DroneOwnership']",self._cur.fetchall()

    def GetDroneInfo(self,UserID,DroneID):  #Get the information about a single drone
        self._cur.execute("SELECT DISTINCT Drone.* FROM Drone,User WHERE Drone.DroneID = %s AND (Drone.UserID = %s OR (Drone.UserID = User.UserID AND User.PublicVisibleFlights = 1))",(DroneID,UserID))
        return True,str(self.Table_Headers("Drone")),self._cur.fetchall()
            
    def GetDronesUser(self,UserID): #Get all user drones
        self._cur.execute("SELECT * FROM Drone WHERE UserID = %s",(UserID,))
        self._db_con.commit()
        return True,str(self.Table_Headers("Drone")),self._cur.fetchall()
    def GetDronesAll(self):     #Get all publicly visible drones
        self._cur.execute("SELECT Drone.* FROM User,Drone WHERE User.UserID = Drone.UserID AND User.PublicVisibleFlights = 1")
        return True,str(self.Table_Headers("Drone")),self._cur.fetchall()

    def UpdateDroneStatus(self,DroneID,LastCoords,LastBattery):     #Update the latest information about the drone
        self._cur.execute("UPDATE Drone SET LastCoords = %s,LastBattery = %s WHERE DroneID = %s",(str(LastCoords),int(LastBattery),DroneID))
        self._db_con.commit()
        return True,"Updated Drone Status"

##########################   USER         #############################
    
    def GetUserID(self,Username):
        self._cur.execute("SELECT UserID FROM User WHERE Username = %s",(Username,))
        return True,"['UserID']",self._cur.fetchall()
    def GetUsername(self,UserID):
        self._cur.execute("SELECT Username FROM User WHERE UserID = %s",(UserID,))
        return True,"['Username']",self._cur.fetchall()
    
    def AddUser(self,Username,Password):    #Add a new user
        self._cur.execute("SELECT 1 FROM User WHERE Username = %s",(Username,))     #Checks the user does not already exist
        if self._cur.fetchall() == ():
            self._cur.execute("INSERT INTO User(Username,Password,PublicVisibleFlights,PermissionAdder,ZoneCreatorPermission,ZoneRemoverPermission,ZoneModifierPermission) VALUES(%s,%s,0,0,0,0,0)",(Username,Hash(Password,Username)))
            self._db_con.commit()
            return True,"Added User"
        else:
            return False,"User already exists"

    def CheckCredentials(self,Username,Password):   #Check as user's login is correct
        self._cur.execute("SELECT UserID FROM User WHERE Username = %s AND Password = %s",(Username,Hash(Password,Username)))   #Checks the password and username are correct
        UserIDFetch = self._cur.fetchall()
        if UserIDFetch != ():
            return True,"Correct Credentials",UserIDFetch[0][0] #Return the UserID
        else:
            return False,"Incorrect Credentials",-1

    def SetFlightVisibility(self,UserID,Value): #Alter the flight visiblilty for a user
        if Value in [0,1]:      #Ensures this can only be 0,1 , could be expanded to other values
            self._cur.execute("UPDATE User SET PublicVisibleFlights = %s WHERE UserID = %s",(Value,UserID))
            self._db_con.commit()
            return True,"Changed PublicVisibleFlights Value"
        else:
            return False,"Invalid PublicVisibleFlights Value"
        
    def SetAccountType(self,UserID,Permission,Value):   #Alter a permission for the user
        options = ["ZoneCreatorPermission","ZoneRemoverPermission","ZoneModifierPermission"]
        if Permission not in options:               #Checks only these options are allowed to prevent SQL injection
            return False,"This setting does not exist. Options are :"+str(options)
        self._cur.execute("UPDATE User SET "+Permission+" =%s WHERE UserID = %s AND PermissionAdder > 2",(Value,UserID))  #The string concatation is safe as only strings which are found exactly in options can be inserted and so are safe strings, cannot contain any other commands
        self._db_con.commit()                                           #Above checks permission adder so only users with PermissionAdder > 2 can change their permissions - prevents all users obtaining these permisssions
        return True,"Set AccountType Value"

    def UserChangePassword(self,UserID,OldPassword,NewPassword):    #Change the user's password
        self._cur.execute("SELECT Username from User WHERE UserID = ?",(UserID,))       # Find the username for the salt
        Username = self._cur.fetchall()[0][0]
        self._cur.execute("SELECT 1 FROM User WHERE UserID = %s and Password = %s",(UserID,Hash(OldPassword,Username)))     #Check old password is correct
        if self._cur.fetchall() != ():
            self._cur.execute("UPDATE User SET Password = %s WHERE UserID = %s",(Hash(NewPassword,Username),UserID))        #update password
            self._db_con.commit()
            return True,"Changed password"
        else:
            return False,"Incorrect old password"

#####################          FLIGHT          ##############################

    def GetFlightsUser(self,UserID):        #Get all flights belonging to the user
        self._cur.execute("SELECT Flight.* FROM Flight,Drone WHERE Flight.DroneID = Drone.DroneID AND Drone.UserID = %s",(UserID,))
        return True,str(self.Table_Headers("Flight")),self._cur.fetchall()

    
    def GetFlightsAll(self):        #Get all publicly visible flights
        self._cur.execute("SELECT Flight.* FROM Flight,Drone,User WHERE Flight.DroneID = Drone.DroneID AND Drone.UserID = User.UserID AND User.PublicVisibleFlights = 1")
        return True,str(self.Table_Headers("Flight")),self._cur.fetchall()

    def AddFlight(self,UserID,DroneID,StartCoords,EndCoords,StartTime,ETA,EndTime,Distance,XOffset,YOffset,ZOffset):
        self._cur.execute("SELECT 1 FROM User,Drone WHERE Drone.DroneID = %s AND Drone.UserID = %s",(DroneID,UserID))   #Check user owns drone
        if self._cur.fetchall() !=():
            self._cur.execute("INSERT INTO Flight(DroneID,StartCoords,EndCoords,StartTime,ETA,EndTime,Distance,XOffset,YOffset,ZOffset,Completed) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)",(DroneID,str(StartCoords),str(EndCoords),int(StartTime),int(ETA),int(EndTime),int(Distance),XOffset,YOffset,ZOffset))
            self._db_con.commit()
            FlightID = self._cur.lastrowid
            return True,"Flight added",FlightID
        else:
            return False,"You do not have permission to launch this drone",-1
        
    def RemoveFlight(self,UserID,FlightID):     #Delete a flight
        self._cur.execute("SELECT 1 FROM Flight,Drone,User WHERE Flight.FlightID = %s AND Flight.DroneID = Drone.DroneID AND Drone.UserID = %s",(FlightID,UserID))  #If User owns this drone/flight
        if self._cur.fetchall() != ():
            self._cur.execute("DELETE FROM Flight WHERE FlightID = %s",(FlightID,))
            self._db_con.commit()
            return True,"Flight Removed"
        else:
            return False,"You do not have permission to remove this flight"

    def CheckForFlight(self,DroneID,MaxLookAheadTime):  #Checks for a nearby (time wise) flight for the drone
        InvalidateDelay = 1800
        self._cur.execute("SELECT FlightID FROM Flight WHERE DroneID = %s AND StartTime < (%s+%s) AND StartTime > (%s-%s) AND Completed = 0 ORDER BY StartTime ASC LIMIT 1",(DroneID,GetTime(),MaxLookAheadTime, GetTime(),InvalidateDelay))        #Checks if a flight is available in the allowed range
        FlightIDFetch = self._cur.fetchall()
        self._db_con.commit()
        if FlightIDFetch != ():
            return True,"Flight is available",FlightIDFetch
        else:
            return False,"Flight is not available",[]

    def GetFlight(self,DroneID,FlightID):       #Get details about a given flight
        self._cur.execute("SELECT * FROM Flight WHERE DroneID = %s AND FlightID = %s",(DroneID,FlightID))   #Checks the drone can access the flight
        FlightFetch = self._cur.fetchall()
        if FlightFetch != ():
            return True,str(self.Table_Headers("Flight")),FlightFetch
        else:
            return False,"Flight not obtained, Flight may not exist or you may not have permission",[]

    def MarkFlightComplete(self,DroneID,FlightID,Code):     #Mark a flight as complete using a given code.
        self._cur.execute("SELECT 1 FROM Flight WHERE DroneID = %s AND FlightID = %s",(DroneID,FlightID))       #Checks drone can access the flight
        if self._cur.fetchall() != ():
            self._cur.execute("UPDATE Flight SET Completed = %s,EndTime = %s WHERE FlightID = %s",(Code,GetTime(),FlightID))
            self._cur.execute("UPDATE Drone SET FlightsFlown = FlightsFlown +1 WHERE DroneID = %s",(DroneID,))
            self._db_con.commit()
            return True,"Marked Flight complete"
        else:
            return False,"You do not have permission to mark this flight complete"
        
    def GetCompletedFlightIDs(self,EndTimeThreshold):       #Obtain the FlightIDs of all flights which have been completed
        self._cur.execute("SELECT FlightID FROM Flight WHERE (Completed > 0 AND (EndTime + %s) < %s) OR (EndTime+ %s) < %s",(EndTimeThreshold,GetTime(),EndTimeThreshold*3,GetTime()))      
        return True,"['FlightID']",self._cur.fetchall()

    def CleanFlights(self,FlightIDList):    #Delete all flights in the FlightID list
        self._cur.executemany("DELETE FROM Flight WHERE FlightID = %s",FlightIDList)
        self._db_con.commit()
        return True,"Deleted completed flights above threshold"    

#----------------------------  FLIGHT WAYPOINT------------------------------------
    def GetFlightWaypoints(self,DroneID,FlightID):      #Get all the flight waypoints for a flight
        self._cur.execute("SELECT FlightWaypoints.* FROM Flight,FlightWaypoints WHERE Flight.DroneID = %s AND Flight.FlightID = FlightWaypoints.FlightID AND FlightWaypoints.FlightID = %s",(DroneID,FlightID))
        return True,str(self.Table_Headers("FlightWaypoints")),self._cur.fetchall()          
    
    def GetFlightWaypointsUser(self,UserID):    #Get all the flightt waypoints for a user
        self._cur.execute("SELECT FlightWaypoints.* FROM FlightWaypoints,Flight,Drone WHERE FlightWaypoints.FlightID = Flight.FlightID AND Flight.DroneID = Drone.DroneID AND Drone.UserID = %s ORDER BY FlightWaypoints.FlightID, FlightWaypoints.WaypointNumber",(UserID,))
        return True,str(self.Table_Headers("FlightWaypoints")),self._cur.fetchall()
    
    def GetFlightWaypointsAll(self):        #Get all publicly visible flight waypoints.
        self._cur.execute("SELECT FlightWaypoints.* FROM FlightWaypoints,Flight,Drone,User WHERE FlightWaypoints.FlightID = Flight.FlightID AND Flight.DroneID = Drone.DroneID AND Drone.UserID = User.UserID AND User.PublicVisibleFlights = 1 ORDER BY FlightWaypoints.FlightID,FlightWaypoints.WaypointNumber")
        return True,str(self.Table_Headers("FlightWaypoints")),self._cur.fetchall()
    
    def AddWaypoint(self,UserID,FlightID,WaypointNumber,Coords,ETA,BlockTime=0):    #Add a single new waypoint
        self._cur.execute("SELECT 1 FROM User,Flight,Drone WHERE User.UserID = %s AND User.UserID = Drone.UserID AND Drone.DroneID = Flight.DroneID AND Flight.FlightID = %s",(UserID,FlightID))    #Check the client can add this waypoint
        if self._cur.fetchall() !=():
            self._cur.execute("INSERT INTO FlightWaypoints(FlightID,WaypointNumber,Coords,ETA,BlockTime) VALUES(%s,%s,%s,%s,%s)",(FlightID,WaypointNumber,str(Coords),int(ETA),BlockTime))
            self._db_con.commit()
            return True,"Added Waypoint"
        else:
            return False,"You do not have permission to add a waypoint for this flight"

    def AddWaypoints(self,UserID,FlightID,Waypoints):   #Add a number of new waypoints in a batch to reduce overhead
        self._cur.execute("SELECT 1 FROM User,Flight,Drone WHERE User.UserID = %s AND User.UserID = Drone.UserID AND Drone.DroneID = Flight.DroneID AND Flight.FlightID = %s",(UserID,FlightID))    #Checks user can add flight
        if self._cur.fetchall() !=():
            self._cur.executemany("INSERT INTO FlightWaypoints(FlightID,WaypointNumber,Coords,ETA,BlockTime) VALUES(%s,%s,%s,%s,%s)",Waypoints)
            self._db_con.commit()
            return True,"Added Waypoints"
        else:
            return False,"You do not have permission to add a waypoint for this flight"
        
    def RemoveFlightWaypoints(self,UserID,FlightID):    #Remove all waypoints for a given flight
        self._cur.execute("SELECT 1 FROM User,Flight,Drone WHERE User.UserID = %s AND User.UserID = Drone.UserID AND Drone.DroneID = Flight.DroneID AND Flight.FlightID = %s",(UserID,FlightID))    #Check user can delete waypoint
        if self._cur.fetchall() !=():
            self._cur.execute("DELETE FROM FlightWaypoints WHERE FlightID = %s",(FlightID,))
            self._db_con.commit()
            return True,"Deleted waypoint"
        else:
            return False,"You do not have permission to delete these waypoints"


    def CleanCompletedFlightWaypoints(self,FlightID):  #Server only command, deletes all flight waypoints for the given flight
        self._cur.execute("DELETE FROM FlightWaypoints WHERE FlightID = %s",(FlightID,))
        self._db_con.commit()
        return True,"Deleted waypoints"

###########################  MONITOR     ##################################
    def AddMonitor(self,MonitorName,MonitorPassword):
        self._cur.execute("SELECT 1 FROM Monitor WHERE MonitorName = %s",(MonitorName,))        #Checks monitordoes not exist
        if self._cur.fetchall() == ():
            self._cur.execute("INSERT INTO Monitor(MonitorName,MonitorPassword) VALUES(%s,%s)",(MonitorName,Hash(MonitorPassword,MonitorName)))
            self._db_con.commit()
            return True,"Added Monitor"
        else:
            return False,"Monitor already exists"

    def MonitorCheckCredentials(self,MonitorName,MonitorPassword):  #Checks if the login for a monitor is correct
        self._cur.execute("SELECT MonitorID FROM Monitor WHERE MonitorName = %s AND MonitorPassword = %s",(MonitorName,Hash(MonitorPassword,MonitorName)))  #Checks monitor credentials
        MonitorIDFetch = self._cur.fetchall()
        if MonitorIDFetch != ():
            return True,"Correct Credentials",MonitorIDFetch[0][0]
        else:
            return False,"Incorrect Credentials",-1

    def MonitorChangePassword(self,MonitorID,OldPassword,NewPassword):  #Change the password for a monitor
        self._cur.execute("SELECT MonitorName FROM Monitor WHERE MonitorID = ?",(MonitorID,))       #Obtains monitor name
        MonitorName = self._cur.fetchall()[0][0]
        self._cur.execute("SELECT 1 FROM Monitor WHERE MonitorID = %s AND MonitorPassword = %s",(MonitorID,Hash(OldPassword,MonitorName)))  #Ensures old password is correct
        if self._cur.fetchall() != ():
            self._cur.execute("UPDATE Monitor SET MonitorPassword = %s WHERE MonitorID = %s",(Hash(NewPassword,MonitorName),MonitorID))
            self._db_con.commit()
            return True,"Password updated"
        else:
            return False, "Incorrect old password"

    def GetMonitorDrones(self,MonitorID):   #Get all the monitors for a drone from monitor permissions
        self._cur.execute("SELECT Drone.* FROM Drone,MonitorPermission WHERE Drone.UserID = MonitorPermission.UserID AND MonitorPermission.MonitorID = %s",(MonitorID,))
        self._db_con.commit()
        return True,str(self.Table_Headers("Drone")),self._cur.fetchall()
    
    def GetMonitorFlights(self,MonitorID):      #Get all flights for a monitor via monitor permissions
        self._cur.execute("SELECT Flight.* FROM Flight,Drone,MonitorPermission WHERE Flight.DroneID = Drone.DroneID AND Drone.UserID = MonitorPermission.UserID and MonitorPermission.MonitorID = %s",(MonitorID,))
        self._db_con.commit()
        return True,str(self.Table_Headers("Flight")),self._cur.fetchall()
    
    def GetMonitorFlightWaypoints(self,MonitorID):  #Get all flight waypoints for a monitor via monitor permissions
        self._cur.execute("SELECT FlightWaypoints.* FROM FlightWaypoints,Flight,Drone,MonitorPermission WHERE FlightWaypoints.FlightID = Flight.FlightID AND Flight.DroneID = Drone.DroneID AND Drone.UserID = MonitorPermission.UserID and MonitorPermission.MonitorID = %s",(MonitorID,))
        self._db_con.commit()
        return True,str(self.Table_Headers("FlightWaypoints")),self._cur.fetchall()

    def GetMonitorID(self,MonitorName):
        self._cur.execute("SELECT MonitorID FROM Monitor WHERE MonitorName = %s",(MonitorName,))
        result = self._cur.fetchall()
        return True,"['MonitorID']",result
    
    def GetMonitorName(self,MonitorID):
        self._cur.execute("SELECT MonitorName FROM Monitor WHERE MonitorID = %s",(MonitorID,))
        return True,"['MonitorName']",self._cur.fetchall()

#--------------------------   MONITOR PERMISSION   ------------------------------------
    def AddMonitorPermission(self,UserID,MonitorID,ExpiryDate):     #Add a monitor permission
        self._cur.execute("SELECT 1 FROM MonitorPermission WHERE UserID = %s AND MonitorID = %s",(UserID,MonitorID))    # Checks permission does not already exist
        if self._cur.fetchall() ==():
            self._cur.execute("INSERT INTO MonitorPermission(MonitorID,UserID,LastAccessed,ExpiryDate) VALUES (%s,%s,%s,%s)",(MonitorID,UserID,0,ExpiryDate))
            self._db_con.commit()
            return True,"Sucessfully added MonitorPermission"
        else:
            return False,"MonitorPermission already exists"

    def RemoveMonitorPermission(self,UserID,MonitorID):     #remove a monitor permission
        self._cur.execute("DELETE FROM MonitorPermission WHERE UserID = %s AND MonitorID = %s",(UserID,MonitorID))
        self._db_con.commit()
        return True,"Deleted MonitorPermission"

    def ModifyMonitorPermissionDate(self,UserID,MonitorID,NewDate):     #Modify a monitor permission
        self._cur.execute("UPDATE MonitorPermission SET ExpiryDate = %s WHERE UserID = %s AND MonitorID = %s",(NewDate,UserID,MonitorID))
        self._db_con.commit()
        return True,"Updated Date for MonitorPermission"
    
    def GetMonitorPermissionUser(self,UserID):      #Get all permissions for a user
        self._cur.execute("SELECT * FROM MonitorPermission WHERE UserID = %s",(UserID,))
        Headers = self.Table_Headers("MonitorPermission")
        return True,str(Headers),self._cur.fetchall()
    
    def GetMonitorPermissionMonitor(self,MonitorID):    #Get all the permissions for a monitor
        self._cur.execute("SELECT * FROM MonitorPermission WHERE MonitorID = %s",(MonitorID,))
        Headers = self.Table_Headers("MonitorPermission")
        return True,str(Headers),self._cur.fetchall()
    
    def UpdateMonitorPermissionLastAccessed(self,UserID,MonitorID,NewDate = None):      #Update when the permission was last accessed. Not used due to performance loss and not being particularly useful
        if NewDate == None:
            NewDate = GetTime()
        self._cur.execute("UPDATE MonitorPermission SET LastAccessed = %s WHERE MonitorID = %s AND UserID = %s",(NewDate,MonitorID,UserID))
        self._db_con.commit()
        return True,"Updated LastAccessed"

    def CleanMonitorPermissions(self):      #Remove old monitor permissions after expiry
        self._cur.execute("DELETE FROM MonitorPermission WHERE ExpiryDate < %s",(GetTime(),))
        self._db_con.commit()
        return True,"Cleaned Monitor Permission"


########################    No Fly Zone ###############################################
    def AddNoFlyZone(self,Coord1,Coord2,Level,UserID):      #Add a no fly zone
        if not CoordLessThanOrEqual(Coord1,Coord2):  #If Coord2 is closer to origin in every point than Coord1 It is an invalid coordinate
            Message = "Invalid Coordinates. Coordinate 2:"+str(Coord2)+" is closer in some dimentions to the origin than Coordinate 1"+str(Coord1)
            return False,Message
        else:
            if type(Level) is not int or Level <= 0:
                return False, "Invalid Level. Must be an integer and > 0"
            self._cur.execute("SELECT 1 FROM User WHERE UserID = %s AND ZoneCreatorPermission =1",(UserID,))        #Checks user has permission to add a NoFlyZone
            if self._cur.fetchall() !=  ():
                self._cur.execute("INSERT INTO NoFlyZone(StartCoord,EndCoord,Level,OwnerUserID) VALUES(%s,%s,%s,%s)",(str(Coord1),str(Coord2),Level,UserID))
                self._db_con.commit()
                return True,"Sucessfully added NoFlyZone"
            else:
                return False,"You do not have ZoneCreator Permission"
    def RemoveNoFlyZone(self,UserID,ZoneID):
        self._cur.execute("SELECT 1 FROM NoFlyZone,User WHERE (NoFlyZone.ZoneID = %s AND NoFlyZone.OwnerUserID = %s ) OR (User.UserID = %s AND User.ZoneRemoverPermission = 1)",(ZoneID,UserID,UserID))   # Gets 1 if (Zone with ZoneID has UserID as owner) OR (User with UserID has ZoneRemoverPermission) 
        if self._cur.fetchall() != ():
            #Runs if user has permission to delete this no fly zone
            self._cur.execute("DELETE FROM NoFlyZone WHERE ZoneID = %s",(ZoneID,))
            self._db_con.commit()
            return True,"Sucessfully deleted NoFlyZone"
        else:
            return False,"You do not own this NoFlyZone or you do not have the ZoneRemoverPermission"   #Replace String permission with max no fly zone level permission
        

    def ModifyNoFlyZoneLevel(self,UserID,ZoneID,Level):     #Modify a no fly zone level.
        if type(Level) is not int or Level <=0:
            return False,"Invalid Level. Must be an integer and > 0"
        self._cur.execute("SELECT 1 FROM NoFlyZone,User WHERE (NoFlyZone.ZoneID = %s AND NoFlyZone.OwnerUserID = %s ) OR (User.UserID = %s AND User.ZoneModifierPermission = 1)",(ZoneID,UserID,UserID))   # Gets 1 if (Zone with ZoneID has UserID as owner) OR (User with UserID has ZoneModifier Permission) 
        if self._cur.fetchall() != ():
            #Runs if user has permission to delete this no fly zone
            self._cur.execute("UPDATE NoFlyZone SET Level = %s WHERE ZoneID = %s",(Level,ZoneID))
            self._db_con.commit()
            return True,"Sucessfully modified NoFlyZone"
        else:
            return False,"You do not own this NoFlyZone or you do not have the ZoneModifier Permission"   #Replace String permission with max no fly zone level permission    

    def GetNoFlyZones(self):    #Get all no fly zones
        self._cur.execute("SELECT * FROM NoFlyZone")
        Headers = self.Table_Headers("NoFlyZone")    #Gets Headers of table to be sent as message
        return True,str(Headers),self._cur.fetchall()
    
###########################################################################
    ##################  InputStack   #################################

    def Bot_addValue(self,value,chat_id):       #Add an input value to the input stack for a chat id
        self._cur.execute("SELECT MAX(stack_pos) FROM InputStack WHERE chat_id = %s",(chat_id,))
        result = self._cur.fetchall()
        if not result[0][0] == None:
            stack_pos = result[0][0] +1
        else:
            stack_pos = 0
        self._cur.execute("INSERT INTO InputStack VALUES(%s,%s,%s)",(chat_id,stack_pos,value))
        self._db_con.commit()
    
    def Bot_getCommand(self,chat_id):   #Get the command on the stack for a given chat id
        self._cur.execute("SELECT value FROM InputStack WHERE chat_id = %s AND stack_pos = 0",(chat_id,))
        result = self._cur.fetchall()
        return result[0][0]
    
    def Bot_getStack(self,chat_id):     #Get the entire stack ordered backwards
        self._cur.execute("SELECT value FROM InputStack WHERE chat_id = %s ORDER BY stack_pos ASC",(chat_id,))
        result = self._cur.fetchall()
        return result

    def Bot_getStackSize(self,chat_id):     #Get the size of the stack
        self._cur.execute("SELECT COUNT(1) FROM InputStack WHERE chat_id = %s",(chat_id,))
        result = self._cur.fetchall()
        return result[0][0]
    
    def Bot_flushStack(self,chat_id):       #Cancel the entire stack
        self._cur.execute("DELETE FROM InputStack WHERE chat_id = %s",(chat_id,))
        self._db_con.commit()

    ##################################################################
    ####################### Sessions ##########################

    def Bot_SetUserID(self,chat_id,UserID):     #Set the userID a chat is logged in as
        self._cur.execute("SELECT 1 FROM Sessions WHERE chat_id = %s",(chat_id,))
        if len(self._cur.fetchall()) == 0:
            self._cur.execute("INSERT INTO Sessions VALUES(%s,%s)",(chat_id,UserID))
        else:
            self._cur.execute("UPDATE Sessions SET UserID = %s WHERE chat_id = %s",(UserID,chat_id))
        self._db_con.commit()

    def Bot_GetUserID(self,chat_id):        #Get the userId the chat is logged in as
        self._cur.execute("SELECT UserID FROM Sessions WHERE chat_id = %s",(chat_id,))
        result = self._cur.fetchall()
        if len(result) == 0:
            return -1
        else:
            return result[0][0]    

##########################################################################    
        
    def ResetDatabase(self):        #Resets the tables 
        self._cur.execute("SET FOREIGN_KEY_CHECKS = 0")  #Otherwise dropping tables will raise errors.
        TABLES = ["User","Drone","Monitor","MonitorPermission","Flight","FlightWaypoints","NoFlyZone","DroneCredentials","InputStack","Sessions"]
        for item in TABLES:  # Drops all tables
            self._cur.execute("DROP TABLE IF EXISTS {0}".format(item))
        
        self._cur.execute("CREATE TABLE User(UserID INTEGER PRIMARY KEY AUTO_INCREMENT, Username TEXT,Password TEXT, PublicVisibleFlights INT, PermissionAdder INT , ZoneCreatorPermission INT, ZoneRemoverPermission INT,ZoneModifierPermission INT)")
        self._cur.execute("CREATE TABLE Drone(DroneID INTEGER PRIMARY KEY AUTO_INCREMENT, UserID INT, DroneName TEXT, DroneType TEXT, DroneSpeed INT, DroneRange INT, DroneWeight REAL, FlightsFlown INT, LastCoords TEXT, LastBattery REAL,FOREIGN KEY(UserID) REFERENCES User(UserID))")
        self._cur.execute("CREATE TABLE Monitor(MonitorID INTEGER PRIMARY KEY AUTO_INCREMENT, MonitorName TEXT, MonitorPassword TEXT)")
        self._cur.execute("CREATE TABLE MonitorPermission(MonitorID INT ,UserID INT, LastAccessed TEXT, ExpiryDate TEXT,PRIMARY KEY(MonitorID,UserID),FOREIGN KEY(MonitorID) REFERENCES Monitor(MonitorID),FOREIGN KEY(UserID) REFERENCES User(UserID))")
        self._cur.execute("CREATE TABLE Flight(FlightID INTEGER PRIMARY KEY AUTO_INCREMENT, DroneID INT, StartCoords TEXT, EndCoords TEXT, StartTime REAL, ETA REAL, EndTime REAL, Distance  REAL,XOffset REAL , YOffset REAL , ZOffset REAL,Completed INT,FOREIGN KEY(DroneID) REFERENCES Drone(DroneID))")
        self._cur.execute("CREATE TABLE FlightWaypoints(FlightID INT, WaypointNumber INT, Coords TEXT, ETA REAL, BlockTime INT ,PRIMARY KEY(FlightID,WaypointNumber),FOREIGN KEY(FlightID) REFERENCES Flight(FlightID))")
        self._cur.execute("CREATE TABLE NoFlyZone(ZoneID INTEGER PRIMARY KEY AUTO_INCREMENT, StartCoord TEXT, EndCoord TEXT, Level INT, OwnerUserID INT,FOREIGN KEY(OwnerUserID) REFERENCES User(UserID))")
        self._cur.execute("CREATE TABLE DroneCredentials(DroneID INTEGER PRIMARY KEY AUTO_INCREMENT ,DronePassword TEXT)")

        self._cur.execute("CREATE TABLE InputStack(chat_id INT , stack_pos INT, value TEXT, PRIMARY KEY(chat_id,stack_pos))")
        self._cur.execute("CREATE TABLE Sessions(chat_id INT PRIMARY KEY, UserID INT)")
        
        self._cur.execute("SET FOREIGN_KEY_CHECKS = 1")  # Reenables checks
        self._db_con.commit()
    

