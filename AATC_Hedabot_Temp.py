import prettytable,AATC_Client,ast,HedaBot
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
            
            20:"GetFlightsUser",
            21:"GetFlightsAll",
            22:"AddFlight",
            23:"RemoveFlight",
            
            24:"GetFlightWaypointsUser",
            25:"GetFlightWaypointsAll",
            
            26:"GetMonitorID",
            27:"GetMonitorName",
            
            28:"AddMonitorPermission",
            29:"RemoveMonitorPermission",
            30:"ModifyMonitorPermissionDate",
            31:"GetMonitorPermissionUser",


            -1:"Exit"
            }


class UserTextUI:
    def __init__(self,UserInterface,MenuOptions):
        self.UserInterface = UserInterface
        self.MenuOptions = MenuOptions
        self.bot = HedaBot.Telebot(HedaBot.telepot.Bot(HedaBot.BOT_TOKEN))

    def Main_Loop(self):
        self.Exit = False
        while not self.Exit:
            try:
                self.PrintMainMenu()
                MenuChoice = self.GetMenuChoice()
                self.EvaluateChoice(MenuChoice)
                _ = self.bot.textInput("Any message when ready")
            except Exception as e:
                print("Error occured in Client Text UI",e)
                
    def PrintMainMenu(self):
        #self.bot.sendMessage("\n"*2)
        menu = ""
        menu += "AATC Client Main Menu" +"\n"
        for x in self.MenuOptions.items():
            menu += "{0:>3} : {1}".format(str(x[0]),x[1])+"\n"
        self.bot.sendMessage(menu)
            
    def GetMenuChoice(self):
        MenuChoice = -99
        while MenuChoice not in self.MenuOptions:  #will exit once valid menu option is chosen
            try:
                 MenuChoice = int(self.bot.textInput("Choice >>"))
            except:
                self.bot.sendMessage("Integers only")
        return MenuChoice

    def EvaluateChoice(self,MenuChoice):
        Command = self.MenuOptions[MenuChoice]  #Gets full, easier to work with string

        if Command == "Login":
            self.Login()
            
        elif Command == "GetNoFlyZones":
            self.GetNoFlyZones()
        elif Command == "AddNoFlyZone":
            self.AddNoFlyZone()
        elif Command == "RemoveNoFlyZone":
            self.RemoveNoFlyZone()
        elif Command == "ModifyNoFlyZoneLevel":
            self.ModifyNoFlyZoneLevel()
            
        elif Command == "AddDrone":
            self.AddDrone()
        elif Command == "RemoveDrone":
            self.RemoveDrone()
        elif Command == "GetDroneID":
            self.GetDroneID()
        elif Command == "GetDroneCredentials":
            self.GetDroneCredentials()
        elif Command == "SetDroneCredentials":
            self.SetDroneCredentials()
        elif Command == "CheckDroneOwnership":
            self.CheckDroneOwnership()
        elif Command == "GetDroneInfo":
            self.GetDroneInfo()
        elif Command == "GetDronesUser":
            self.GetDronesUser()
        elif Command == "GetDronesAll":
            self.GetDronesAll()
            
        elif Command == "GetUserID":
            self.GetUserID()
        elif Command == "GetUsername":
            self.GetUsername()
        elif Command == "AddUser":
            self.AddUser()
        elif Command == "SetFlightVisibility":
            self.SetFlightVisibility()
        elif Command == "SetAccountType":
            self.SetAccountType()

        elif Command == "GetFlightsUser":
            self.GetFlightsUser()
        elif Command == "GetFlightsAll":
            self.GetFlightsAll()
        elif Command == "AddFlight":
            self.AddFlight()
        elif Command == "RemoveFlight":
            self.RemoveFlight()
            
        elif Command == "GetFlightWaypointsUser":
            self.GetFlightWaypointsUser()
        elif Command == "GetFlightWaypointsAll":
            self.GetFlightWaypointsAll()

        elif Command == "GetMonitorID":
            self.GetMonitorID()
        elif Command == "GetMonitorName":
            self.GetMonitorName()

        elif Command == "AddMonitorPermission":
            self.AddMonitorPermission()
        elif Command == "RemoveMonitorPermission":
            self.RemoveMonitorPermission()
        elif Command == "ModifyMonitorPermissionDate":
            self.ModifyMonitorPermissionDate()
        elif Command == "GetMonitorPermissionUser":
            self.GetMonitorPermissionUser()



        elif Command == "Exit":
            self.Call_Exit()
        else:
            self.bot.sendMessage("Please correctly register method to EvaluateChoice method")

    def DisplayResults(self,Sucess,Message,Data = None):
        result = ""
        result +="Sucess >>"+str(Sucess)+"\n"
        result +="Message >>"+str(Message)+"\n"
        if Data not in [None,[]]:
            try:
                Columns = ast.literal_eval(Message)
                Table = prettytable.PrettyTable(Columns)
                for row in Data:
                    Table.add_row(row)
                result += str(Table) +"\n"
            except Exception as e:
                result += "Error creating asthetic table" + str(e) +"\n"
                for row in Data:
                    result += str(row) +"\n"
        self.bot.sendMessage(result)
        

    def Login(self):
        Username = self.bot.textInput("Username >>")
        Password = self.bot.textInput("Password >>")
        Sucess,Message = self.UserInterface.Login(Username,Password)
        self.DisplayResults(Sucess,Message)

    #######################################

    def GetNoFlyZones(self):
        Sucess,Message,NoFlyZones =self.UserInterface.GetNoFlyZones()
        self.DisplayResults(Sucess,Message,NoFlyZones)

    def AddNoFlyZone(self):
        StartCoords = self.bot.textInput("Enter Start Coordinates in form (x,y,z) >>")
        EndCoords = self.bot.textInput("Enter End Coordinates in form (x,y,z) >>")
        Level = int(self.bot.textInput("Enter Level of No Fly Zone >>"))
        Sucess,Message = self.UserInterface.AddNoFlyZone(StartCoords,EndCoords,Level)
        self.DisplayResults(Sucess,Message)
        
    def RemoveNoFlyZone(self):
        ZoneID = int(self.bot.textInput("Enter ZoneID >>"))
        Sucess,Message = self.UserInterface.RemoveNoFlyZone(ZoneID)
        self.DisplayResults(Sucess,Message)

    def ModifyNoFlyZoneLevel(self):
        ZoneID = int(self.bot.textInput("Enter ZoneID >>"))
        Level = int(self.bot.textInput("Enter Level >>"))
        Sucess,Message = self.UserInterface.ModifyNoFlyZoneLevel(ZoneID,Level)
        self.DisplayResults(Sucess,Message)


    #####################################
    
    def AddDrone(self):
        DroneName = self.bot.textInput("Drone Name >>")
        DronePassword = self.bot.textInput("Drone Password >>")
        Type = self.bot.textInput("Drone Type >>")
        Speed = int(self.bot.textInput("Speed (m/s) >>"))
        Range = int(self.bot.textInput("Range (m) >>"))
        Weight = float(self.bot.textInput("Weight (kg) >>"))
        Sucess,Message = self.UserInterface.AddDrone(DroneName,DronePassword,Type,Speed,Range,Weight)
        self.DisplayResults(Sucess,Message)

    def RemoveDrone(self):
        DroneID = int(self.bot.textInput("DroneID >>"))
        Sucess,Message = self.UserInterface.RemoveDrone(DroneID)
        self.DisplayResults(Sucess,Message)

    def GetDroneID(self):
        DroneName = self.bot.textInput("Drone Name >>")
        Sucess,Message,DroneID = self.UserInterface.GetDroneID(DroneName)
        self.DisplayResults(Sucess,Message,DroneID)
        
    def GetDroneCredentials(self):
        DroneID = int(self.bot.textInput("DroneID >>"))
        Sucess,Message,Credentials = self.UserInterface.GetDroneCredentials(DroneID)
        self.DisplayResults(Sucess,Message,Credentials)

    def SetDroneCredentials(self):
        DroneID = int(self.bot.textInput("DroneID >>"))
        DronePassword = self.bot.textInput("Drone Password >>")
        Sucess,Message = self.UserInterface.SetDroneCredentials(DroneID,DronePassword)
        self.DisplayResults(Sucess,Message,Credentials)

    def CheckDroneOwnership(self):
        UserID = int(self.bot.textInput("UserID >>"))
        DroneID = int(self.bot.textInput("DroneID >>"))
        Sucess,Message,Ownership = self.UserInterface.CheckDroneOwnership(UserID,DroneID)
        self.DisplayResults(Sucess,Message,Ownership)

    def GetDroneInfo(self):
        DroneID = int(self.bot.textInput("DroneID >>"))
        Sucess,Message,DroneInfo = self.UserInterface.GetDroneInfo(DroneID)
        self.DisplayResults(Sucess,Message,DroneInfo)

    def GetDronesUser(self):
        Sucess,Message,DroneInfo = self.UserInterface.GetDronesUser()
        self.DisplayResults(Sucess,Message,DroneInfo)

    def GetDronesAll(self):
        Sucess,Message,DroneInfo = self.UserInterface.GetDronesAll()
        self.DisplayResults(Sucess,Message,DroneInfo)

    ###############################################

    def GetUserID(self):
        Username = self.bot.textInput("Username >>")
        Sucess,Message,UserID = self.UserInterface.GetUserID(Username)
        self.DisplayResults(Sucess,Message,UserID)

    def GetUsername(self):
        UserID = int(self.bot.textInput("UserID >>"))
        Sucess,Message,Username = self.UserInterface.GetUsername(UserID)
        self.DisplayResults(Sucess,Message,Username)

    def AddUser(self):
        Username = self.bot.textInput("Username >>")
        Password = self.bot.textInput("Password >>")
        Sucess,Message = self.UserInterface.AddUser(Username,Password)
        self.DisplayResults(Sucess,Message)

    def SetFlightVisibility(self):
        Visibility = int(self.bot.textInput("Visibility >>"))
        Sucess,Message = self.UserInterface.SetFlightVisibility(Visibility)
        self.DisplayResults(Sucess,Message)

    def SetAccountType(self):
        Permission = self.bot.textInput("Permission >>")
        Type = self.bot.textInput("Account Type >>")
        Sucess,Message = self.UserInterface.SetAccountType(Permission,Type)
        self.DisplayResults(Sucess,Message)

    ################################################
    
    def GetFlightsUser(self):
        Sucess,Message,UserFlights = self.UserInterface.GetFlightsUser()
        self.DisplayResults(Sucess,Message,UserFlights)

    def GetFlightsAll(self):
        Sucess,Message,AllFlights = self.UserInterface.GetFlightsAll()
        self.DisplayResults(Sucess,Message,AllFlights)

    def AddFlight(self):
        DroneID = int(self.bot.textInput("DroneID >>"))

        HighPoints = []
        point = ""
        self.bot.sendMessage("Enter Coordinates one by one, enter 'Done' once complete")
        while point != "Done":
            point = self.bot.textInput("Enter Coordinate in form (x,y,z) >>")
            if point != "Done":
                HighPoints.append(point)
        StartTime = int(self.bot.textInput("Enter start time in seconds since UNIX time >>"))
        Sucess,Message,FlightInfo = self.UserInterface.AddFlight(DroneID,HighPoints,StartTime)
        self.DisplayResults(Sucess,Message,FlightInfo)
    
        
    def RemoveFlight(self):
        FlightID = int(self.bot.textInput("FlightID >>"))
        Sucess,Message = self.UserInterface.RemoveFlight(FlightID)
        self.DisplayResults(Sucess,Message)

    ###################################################

    def GetFlightWaypointsUser(self):
        Sucess,Message,UserWaypoints = self.UserInterface.GetFlightWaypointsUser()
        self.DisplayResults(Sucess,Message,UserWaypoints)

    def GetFlightWaypointsAll(self):
        Sucess,Message,AllWaypoints = self.UserInterface.GetFlightWaypointsAll()
        self.DisplayResults(Sucess,Message,AllWaypoints)

    ###################################################

    def GetMonitorID(self):
        MonitorName = self.bot.textInput("MonitorName >>")
        Sucess,Message,MonitorID = self.UserInterface.GetMonitorID(MonitorName)
        self.DisplayResults(Sucess,Message,MonitorID)

    def GetMonitorName(self):
        MonitorID = int(self.bot.textInput("MonitorID >>"))
        Sucess,Message,MonitorName = self.UserInterface.GetMonitorName(MonitorID)
        self.DisplayResults(Sucess,Message,MonitorName)

    ##################################################

    def AddMonitorPermission(self):
        MonitorID = int(self.bot.textInput("MonitorID >>"))
        ExpiryDate = int(self.bot.textInput("Expiry Date >>"))
        Sucess,Message = self.UserInterface.AddMonitorPermission(MonitorID,ExpiryDate)
        self.DisplayResults(Sucess,Message)

    def RemoveMonitorPermission(self):
        MonitorID = int(self.bot.textInput("MonitorID >>"))
        Sucess,Message = self.UserInterface.RemoveMonitorPermission(MonitorID)
        self.DisplayResults(Sucess,Message)

    def ModifyMonitorPermissionDate(self):
        MonitorID = int(self.bot.textInput("MonitorID >>"))
        ExpiryDate = int(self.bot.textInput("ExpiryDate"))
        Sucess,Message = self.UserInterface.ModifyMonitorPermissionDate(MonitorID,ExpiryDate)
        self.DisplayResults(Sucess,Message)

    def GetMonitorPermissionUser(self):
        Sucess,Message,MonitorPermissionsUser = self.UserInterface.GetMonitorPermissionUser()
        self.DisplayResults(Sucess,Message,MonitorPermissionsUser)

    #################################################

    def Call_Exit(self):
        Choice = self.bot.textInput("Exit? (Y/N) >>").upper()
        if Choice == "Y":
            self.bot.sendMessage("Exiting..")
            try:
                Sucess,Message = self.UserInterface.Exit()
                self.DisplayResults(Sucess,Message)
            except:
                self.bot.sendMessage("Unable to close server connection")
            self.Exit = True
        else:
            self.bot.sendMessage("Exit cancelled")




if __name__ == "__main__":
    print("AATC User Text Interface")
    Exit = False
    while not Exit:
        try:
            print("Connecting to server...")
            U = AATC_Client.CreateUserInterface()

            TextUI = UserTextUI(U,MenuOptions)
            TextUI.Main_Loop()
            Exit = True  #When user selects exit
                
        except Exception as e:
            print("Error occured creating user interface",e)
            _ = input()













	
