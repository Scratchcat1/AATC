#import AATC Client
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
        























	
