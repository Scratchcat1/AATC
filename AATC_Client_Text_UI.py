import prettytable,AATC_Client,ast
MenuOptions = {
            1:"Login",
            
            2:"GetNoFlyZones",
            3:"AddNoFlyZone",
            4:"RemoveNoFlyZone",
            5:"ModifyNoFlyZoneLevel",
            
            6:"AddDrone",
            7:"RemoveDrone",
            8:"GetDroneID",
            9:"GetDroneCredentials",
            10:"SetDroneCredentials",
            11:"CheckDroneOwnership",
            12:"GetDroneInfo",
            13:"GetDronesUser",
            14:"GetDronesAll",
            
            15:"GetUserID",
            16:"GetUsername",
            17:"AddUser",
            18:"SetFlightVisibility",
            19:"SetAccountType",
            20:"UserChangePassword",
            
            21:"GetFlightsUser",
            22:"GetFlightsAll",
            23:"AddFlight",
            24:"RemoveFlight",
            
            25:"GetFlightWaypointsUser",
            26:"GetFlightWaypointsAll",
            
            27:"GetMonitorID",
            28:"GetMonitorName",
            
            29:"AddMonitorPermission",
            30:"RemoveMonitorPermission",
            31:"ModifyMonitorPermissionDate",
            32:"GetMonitorPermissionUser",


            -1:"Exit"
            }           #Maps command numbers onto the strings of permissions


class UserTextUI:   #Interface with server via text interface
    def __init__(self,UserInterface,MenuOptions):
        self._UserInterface = UserInterface
        self._MenuOptions = MenuOptions
        self._Commands = {
            "Login" : self.Login,
            "GetNoFlyZones" : self.GetNoFlyZones,
            "AddNoFlyZone" : self.AddNoFlyZone,
            "RemoveNoFlyZone" : self.RemoveNoFlyZone,
            "ModifyNoFlyZoneLevel" : self.ModifyNoFlyZoneLevel,
            "AddDrone" : self.AddDrone,
            "RemoveDrone" : self.RemoveDrone,
            "GetDroneID" : self.GetDroneID,
            "GetDroneCredentials" : self.GetDroneCredentials,
            "SetDroneCredentials" : self.SetDroneCredentials,
            "CheckDroneOwnership" : self.CheckDroneOwnership,
            "GetDroneInfo" : self.GetDroneInfo,
            "GetDronesUser" : self.GetDronesUser,
            "GetDronesAll" : self.GetDronesAll,
            "GetUserID" : self.GetUserID,
            "GetUsername" : self.GetUsername,
            "AddUser" : self.AddUser,
            "SetFlightVisibility" : self.SetFlightVisibility,
            "SetAccountType" : self.SetAccountType,
            "UserChangePassword" : self.UserChangePassword,
            "GetFlightsUser" : self.GetFlightsUser,
            "GetFlightsAll" : self.GetFlightsAll,
            "AddFlight" : self.AddFlight,
            "RemoveFlight" : self.RemoveFlight,
            "GetFlightWaypointsUser" : self.GetFlightWaypointsUser,
            "GetFlightWaypointsAll" : self.GetFlightWaypointsAll,
            "GetMonitorID" : self.GetMonitorID,
            "GetMonitorName" : self.GetMonitorName,
            "AddMonitorPermission" : self.AddMonitorPermission,
            "RemoveMonitorPermission" : self.RemoveMonitorPermission,
            "ModifyMonitorPermissionDate" : self.ModifyMonitorPermissionDate,
            "GetMonitorPermissionUser" : self.GetMonitorPermissionUser,
            "Exit" : self.Call_Exit}

    def Main_Loop(self):    #Loop until exit
        self._Exit = False
        while not self._Exit:
            try:
                self.PrintMainMenu()
                MenuChoice = self.GetMenuChoice()
                self.EvaluateChoice(MenuChoice)
                _ = input()
            except Exception as e:
                print("Error occured in Client Text UI",e)
                
    def PrintMainMenu(self):        #Display the menu neatly
        print("\n"*2)
        print("AATC Client Main Menu")
        for x in self._MenuOptions.items():
            print("{0:>3} : {1}".format(str(x[0]),x[1]))
            
    def GetMenuChoice(self):    
        MenuChoice = -99
        while MenuChoice not in self._MenuOptions:  #will exit once valid menu option is chosen
            try:
                 MenuChoice = int(input("Choice >>"))
            except:
                print("Integers only")
        return MenuChoice

    def EvaluateChoice(self,MenuChoice):        #Execute the correct command.
        Command = self._Commands.get(self._MenuOptions[MenuChoice],None)  #Gets full, easier to work with string

        if Command != None:
            Command()
        else:
            print("Please correctly register method to EvaluateChoice method")
            

    def DisplayResults(self,Sucess,Message,Data = None):        #Neatly display the results
        print("Sucess >>",Sucess)
        print("Message >>",Message)
        if Data not in [None,[]]:
            try:
                Columns = ast.literal_eval(Message)
                Table = prettytable.PrettyTable(Columns)
                for row in Data:
                    Table.add_row(row)
                print(Table)
            except Exception as e:
                print("Error creating asthetic table",e)
                for row in Data:
                    print(row)
        

    def Login(self):
        Username = input("Username >>")
        Password = input("Password >>")
        Sucess,Message = self._UserInterface.Login(Username,Password)
        self.DisplayResults(Sucess,Message)

    #######################################

    def GetNoFlyZones(self):
        Sucess,Message,NoFlyZones =self._UserInterface.GetNoFlyZones()
        self.DisplayResults(Sucess,Message,NoFlyZones)

    def AddNoFlyZone(self):
        StartCoords = input("Enter Start Coordinates in form (x,y,z) >>")
        EndCoords = input("Enter End Coordinates in form (x,y,z) >>")
        Level = int(input("Enter Level of No Fly Zone >>"))
        Sucess,Message = self._UserInterface.AddNoFlyZone(StartCoords,EndCoords,Level)
        self.DisplayResults(Sucess,Message)
        
    def RemoveNoFlyZone(self):
        ZoneID = int(input("Enter ZoneID >>"))
        Sucess,Message = self._UserInterface.RemoveNoFlyZone(ZoneID)
        self.DisplayResults(Sucess,Message)

    def ModifyNoFlyZoneLevel(self):
        ZoneID = int(input("Enter ZoneID >>"))
        Level = int(input("Enter Level >>"))
        Sucess,Message = self._UserInterface.ModifyNoFlyZoneLevel(ZoneID,Level)
        self.DisplayResults(Sucess,Message)


    #####################################
    
    def AddDrone(self):
        DroneName = input("Drone Name >>")
        DronePassword = input("Drone Password >>")
        Type = input("Drone Type >>")
        Speed = int(input("Speed (m/s) >>"))
        Range = int(input("Range (m) >>"))
        Weight = float(input("Weight (kg) >>"))
        Sucess,Message = self._UserInterface.AddDrone(DroneName,DronePassword,Type,Speed,Range,Weight)
        self.DisplayResults(Sucess,Message)

    def RemoveDrone(self):
        DroneID = int(input("DroneID >>"))
        Sucess,Message = self._UserInterface.RemoveDrone(DroneID)
        self.DisplayResults(Sucess,Message)

    def GetDroneID(self):
        DroneName = input("Drone Name >>")
        Sucess,Message,DroneID = self._UserInterface.GetDroneID(DroneName)
        self.DisplayResults(Sucess,Message,DroneID)
        
    def GetDroneCredentials(self):
        DroneID = int(input("DroneID >>"))
        Sucess,Message,Credentials = self._UserInterface.GetDroneCredentials(DroneID)
        self.DisplayResults(Sucess,Message,Credentials)

    def SetDroneCredentials(self):
        DroneID = int(input("DroneID >>"))
        DronePassword = input("Drone Password >>")
        Sucess,Message = self._UserInterface.SetDroneCredentials(DroneID,DronePassword)
        self.DisplayResults(Sucess,Message)

    def CheckDroneOwnership(self):
        UserID = int(input("UserID >>"))
        DroneID = int(input("DroneID >>"))
        Sucess,Message,Ownership = self._UserInterface.CheckDroneOwnership(UserID,DroneID)
        self.DisplayResults(Sucess,Message,Ownership)

    def GetDroneInfo(self):
        DroneID = int(input("DroneID >>"))
        Sucess,Message,DroneInfo = self._UserInterface.GetDroneInfo(DroneID)
        self.DisplayResults(Sucess,Message,DroneInfo)

    def GetDronesUser(self):
        Sucess,Message,DroneInfo = self._UserInterface.GetDronesUser()
        self.DisplayResults(Sucess,Message,DroneInfo)

    def GetDronesAll(self):
        Sucess,Message,DroneInfo = self._UserInterface.GetDronesAll()
        self.DisplayResults(Sucess,Message,DroneInfo)

    ###############################################

    def GetUserID(self):
        Username = input("Username >>")
        Sucess,Message,UserID = self._UserInterface.GetUserID(Username)
        self.DisplayResults(Sucess,Message,UserID)

    def GetUsername(self):
        UserID = int(input("UserID >>"))
        Sucess,Message,Username = self._UserInterface.GetUsername(UserID)
        self.DisplayResults(Sucess,Message,Username)

    def AddUser(self):
        Username = input("Username >>")
        Password = input("Password >>")
        Sucess,Message = self._UserInterface.AddUser(Username,Password)
        self.DisplayResults(Sucess,Message)

    def SetFlightVisibility(self):
        Visibility = int(input("Visibility >>"))
        Sucess,Message = self._UserInterface.SetFlightVisibility(Visibility)
        self.DisplayResults(Sucess,Message)

    def SetAccountType(self):
        Permission = input("Account Type >>")
        Type = int(input("Account Type VAlue >>"))
        Sucess,Message = self._UserInterface.SetAccountType(Permission,Type)
        self.DisplayResults(Sucess,Message)

    def UserChangePassword(self):
        OldPassword = input("Old Password >>")
        NewPassword = input("New Password >>")
        Sucess,Message = self._UserInterface.UserChangePassword(OldPassword,NewPassword)
        self.DisplayResults(Sucess,Message)

    ################################################
    
    def GetFlightsUser(self):
        Sucess,Message,UserFlights = self._UserInterface.GetFlightsUser()
        self.DisplayResults(Sucess,Message,UserFlights)

    def GetFlightsAll(self):
        Sucess,Message,AllFlights = self._UserInterface.GetFlightsAll()
        self.DisplayResults(Sucess,Message,AllFlights)

    def AddFlight(self):
        DroneID = int(input("DroneID >>"))

        HighPoints = []
        point = ""
        print("Enter Coordinates one by one, enter 'Done' once complete")
        while point != "Done":      #Obtain all the main points on the flight till the user enters done
            point = input("Enter Coordinate in form (x,y,z) >>")
            if point != "Done":
                HighPoints.append(point)
        StartTime = int(input("Enter start time in seconds since UNIX time >>"))
        Sucess,Message,FlightInfo = self._UserInterface.AddFlight(DroneID,HighPoints,StartTime)
        self.DisplayResults(Sucess,Message,FlightInfo)
    
        
    def RemoveFlight(self):
        FlightID = int(input("FlightID >>"))
        Sucess,Message = self._UserInterface.RemoveFlight(FlightID)
        self.DisplayResults(Sucess,Message)

    ###################################################

    def GetFlightWaypointsUser(self):
        Sucess,Message,UserWaypoints = self._UserInterface.GetFlightWaypointsUser()
        self.DisplayResults(Sucess,Message,UserWaypoints)

    def GetFlightWaypointsAll(self):
        Sucess,Message,AllWaypoints = self._UserInterface.GetFlightWaypointsAll()
        self.DisplayResults(Sucess,Message,AllWaypoints)

    ###################################################

    def GetMonitorID(self):
        MonitorName = input("MonitorName >>")
        Sucess,Message,MonitorID = self._UserInterface.GetMonitorID(MonitorName)
        self.DisplayResults(Sucess,Message,MonitorID)

    def GetMonitorName(self):
        MonitorID = int(input("MonitorID >>"))
        Sucess,Message,MonitorName = self._UserInterface.GetMonitorName(MonitorID)
        self.DisplayResults(Sucess,Message,MonitorName)

    ##################################################

    def AddMonitorPermission(self):
        MonitorID = int(input("MonitorID >>"))
        ExpiryDate = int(input("Expiry Date >>"))
        Sucess,Message = self._UserInterface.AddMonitorPermission(MonitorID,ExpiryDate)
        self.DisplayResults(Sucess,Message)

    def RemoveMonitorPermission(self):
        MonitorID = int(input("MonitorID >>"))
        Sucess,Message = self._UserInterface.RemoveMonitorPermission(MonitorID)
        self.DisplayResults(Sucess,Message)

    def ModifyMonitorPermissionDate(self):
        MonitorID = int(input("MonitorID >>"))
        ExpiryDate = int(input("ExpiryDate"))
        Sucess,Message = self._UserInterface.ModifyMonitorPermissionDate(MonitorID,ExpiryDate)
        self.DisplayResults(Sucess,Message)

    def GetMonitorPermissionUser(self):
        Sucess,Message,MonitorPermissionsUser = self._UserInterface.GetMonitorPermissionUser()
        self.DisplayResults(Sucess,Message,MonitorPermissionsUser)

    #################################################

    def Call_Exit(self):        #Exit communication from the server and exit
        print("Exiting..")
        try:
            Sucess,Message = self._UserInterface.Exit()
            self.DisplayResults(Sucess,Message)
        except:
            print("Unable to close server connection")
        self._Exit = True





if __name__ == "__main__":
    print("AATC User Text Interface")
    Exit = False
    while not Exit:
        try:
            print("Connecting to server...")
            U = AATC_Client.CreateUserInterface(IP = "127.0.0.1")   #Connect to server

            TextUI = UserTextUI(U,MenuOptions)
            TextUI.Main_Loop()      #Run main loop
            
            Choice = input("Exit? (Y/N) >>").upper()
            if Choice == "Y":
                print("Exiting")
                Exit = True  #When user selects exit
            else:
                print("Exit cancelled")
                
        except Exception as e:
            print("Error occured creating user interface",e)
            _ = input()













	
