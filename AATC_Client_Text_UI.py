#import AATC Client , prettytable
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

    def MainLoop(self):
        self.Exit = False
        while not self.Exit:
            self.PrintMainMenu()
            MenuChoice = self.GetMenuChoice()
            self.EvaluateChoice(MenuChoice)
            
    def PrintMainMenu(self):
        print("\n"*2)
        print("AATC Client Main Menu")
        for x in self.MenuOptions.items():
            print("{0:>3} : {1}".format(str(x[0]),x[1]))
            
    def GetMenuChoice(self):
        MenuChoice = -1
        while MenuChoice not in self.MenuOptions:  #will exit once valid menu option is chosen
            try:
                 MenuChoice = int(input("Choice >>"))
            except:
                print("Integers only")
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
            self.GetFlightWaypointUser()
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

        else:
            print("Please correctly register method to EvaluateChoice method")

    def DisplayResults(self,Sucess,Message,Data = None):
        print("Sucess >>",Sucess)
        print("Message >>",Message)
        if Data not in [None,[]]:
            pass
        

    def Login(self):
        Username = input("Username >>")
        Password = input("Password >>")
        Sucess,Message = self.UserInterface.Login(Username,Password)
        self.DisplayResults(Sucess,Message)

    #######################################

    def GetNoFlyZones(self):
        Sucess,Message,NoFlyZones =self.UserInterface.GetNoFlyZones()
        self.DisplayResults(Sucess,Message,NoFlyZones)

    def AddNoFlyZone(self):
        StartCoords = input("Enter Start Coordinates in form (x,y,z) >>")
        EndCoords = input("Enter End Coordinates in form (x,y,z) >>")
        Level = input("Enter Level of No Fly Zone >>")
        Sucess,Message = self.MonitorInteface.AddNoFlyZone(StartCoords,EndCoords,Level)
        self.DisplayResults(Sucess,Message)
        
    def RemoveNoFlyZone(self):
        ZoneID = input("Enter ZoneID >>")
        Sucess,Message = self.UserInterface.RemoveNoFlyZone(ZoneID)
        self.DisplayResults(Sucess,Message)

    def ModifyNoFlyZoneLevel(self):
        ZoneID = input("Enter ZoneID >>")
        Level = input("Enter Level >>")
        Sucess,Message = self.UserInterface.ModifyNoFlyZoneLevel(ZoneID,Level)
        self.DisplayResults(Sucess,Message)


    #####################################
    
    def AddDrone(self):
        DroneName = input("Drone Name >>")
        DronePassword = input("Drone Password >>")
        Type = input("Drone Type >>")
        Speed = input("Speed (m/s) >>")
        Range = input("Range (m) >>")
        Weight = input("Weight (kg) >>")
        Sucess,Message = self.UserInterface.AddDrone(DroneName,DronePassword,Type,Speed,Range,Weight)
        self.DisplayResults(Sucess,Message)

    def RemoveDrone(self):
        DroneID = input("DroneID >>")
        Sucess,Message = self.UserInterface.RemoveDrone(DroneID)
        self.DisplayResults(Sucess,Message)

    def GetDroneID(self):
        DroneName = input("Drone Name >>")
        Sucess,Message,DroneID = self.UserInterface.GetDroneID(DroneName)
        self.DisplayResults(Sucess,Message,DroneID)
        
    def GetDroneCredentials(self):
        DroneID = input("DroneID >>")
        Sucess,Message,Credentials = self.UserInterface.GetDroneCredentials(DroneID)
        self.DisplayResults(Sucess,Message,Credentials)

    def SetDroneCredentials(self):
        DroneID = input("DroneID >>")
        DronePassword = input("Drone Password >>")
        Sucess,Message = self.UserInterface.SetDroneCredentials(DroneID,DronePassword)
        self.DisplayResults(Sucess,Message,Credentials)

    def CheckDroneOwnership(self):
        UserID = input("UserID >>")
        DroneID = input("DroneID >>")
        Sucess,Message = self.UserInterface.CheckDroneOwnership(UserID,DroneID)
        self.DisplayResults(Sucess,Message)

    def GetDroneInfo(self):
        DroneID = input("DroneID >>")
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
        Username = input("Username >>")
        Sucess,Message,UserID = self.UserInterface.GetUserID(Username)
        self.DisplayResults(Sucess,Message,DroneInfo)

    def GetUsername(self):
        UserID = input("UserID >>")
        Sucess,Message,Username = self.UserInterface.GetUsername(UserID)
        self.DisplayResults(Sucess,Message,Username)

    def AddUser(self):
        Username = input("Username >>")
        Password = input("Password >>")
        Sucess,Message = self.UserInterface.AddUser(Username,Password)
        self.DisplayResults(Sucess,Message)

    def SetFlightVisibility(self):
        Visibility = input("Visibility >>")
        Sucess,Message = self.UserInterface.SetFlightVisibility(Visibility)
        self.DisplayResults(Sucess,Message)

    def SetAccountType(self):
        Type = input("Account Type >>")
        Sucess,Message = self.UserInterface.SetAccountType(Type)
        self.DisplayResults(Sucess,Message)

    def GetFlightsUser(self):
        Sucess,Message,UserFlights = self.UserInterface.GetFlightsUser()
        self.DisplayResults(Sucess,Message,UserFlights)

    def GetFlightsAll(self):
        Sucess,Message,AllFlights = self.UserInterface.GetFlightsAll()
        self.DisplayResults(Sucess,Message,AllFlights)

    
    
        






















	
