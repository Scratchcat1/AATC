ClientConnection = Class
    __init__ #Uses private __ but is inheritable 
    Public:
        Connection_Loop #repeat command running/ catch error/ exit
        Send            #Send to client
        Recv            #Recv data
        Exit            #Set Exit
    Protected:
        DB              #Database object
        Thread_Name     #Name of this objects thread
        Thread_Queue    #Command queue for this thread
        con             #Connection object to client
        Crypto          #Crypto object to encrypt communications
        ClientID        #Current clientID
        ExitLoop        #Bool if should exit
EndClass


UserConection = Class(ClientConnection)   #For explanations see AATC_Server_002 UserConnection documentation
    Public:         
        Create_Commands
        ProcessCommand
        Login
        GetNoFlyZones
        AddNoFlyZone
        RemoveNoFlyZone
        ModifyNoFlyZoneLevel
        AddDrone
        RemoveDrone
        GetDroneID
        GetDroneCredentials
        SetDroneCredentials
        CheckDroneOwnership
        GetDroneInfo
        GetDronesUser
        GetDronesAll
        GetUserID
        GetUsername
        AddUser
        SetFlightVisibility
        SetAccountType
        UserChangePassword
        GetFlightsUser
        GetFlightsAll
        AddFlight
        RemoveFlight
        GetFlightWaypointsUser
        GetFlightWaypointsAll
        GetMonitorID
        GetMonitorName
        AddMonitorPermission
        RemoveMonitorPermission
        ModifyMonitorPermissionDate
        GetMonitorPermissionUser
    Protected:
        Non_Authenticated_Commands
        Authenticated_Commands
EndClass

BotConnection = Class(UserConnection)
    __init__(Override)          #Overrides __init__ of grandparent. Uses private __ but is inheritable
    Public:
        Main                    #Processes the command and arguments once instead of in a loop
        Send(Override)          #Sends the result back to the main bot process      
        Login(Override)         #Alters the login to the bot's requirements
    Protected:
        ClientID
        chat_id                 #Note: This is now protected. Some screenshots may include an outdated version
        Output_Queue            #Note: This is now protected. Some screenshots may include an outdated version
        DB
        Thread_Name
EndClass
        
MonitorConnection = Class(ClientConnection)
    Public:
        Create_Commands
        ProcessCommand
        Login
        AddMonitor
        MonitorChangePassword
        GetNoFlyZones
        GetDronesAll
        GetUserID
        GetUsername
        GetMonitorDrones
        GetMonitorFlights
        GetMonitorFlightWaypoints
        GetMonitorID
        GetMonitorName
        RemoveMonitorPermission
        GetMonitorPermissionMonitor
        GetFlightsAll
        GetFlightWaypointsAll
    Protected:
        Non_Authenticated_Commands
        Authenticated_Commands
EndClass


DroneConnection = Class(ClientConnection)
    Public:
        Create_Commands
        ProcessCommand
        Login
        Update_Drone_Status
        DroneGetDroneInfo
        CheckForFlight
        GetFlight
        GetFlightWaypoints
        MarkFlightComplete
    Protected:
        Non_Authenticated_Commands
        Authenticated_Commands
EndClass
        
#####################################################################


DynoGraph = Class
    Public:
        Size
        Get_Size
        Get_Count
        add_node
        Add_Edges
        CalculateNeighbours
        MapHash
        Node_Cache_Hash
        Build_Node_Cache
        Save_Node_Cache
        Get_Node_Cache
        Direct_NodeID
        All_NodeIDs
        Find_NodeID
        Obj_Find_NodeID
        SaveGraph
        ImportGraph
        Hash
        GetNode
        SaveNodes
        EvictNode
        FlushGraph
        Get_Nodes
        GetFolderNames
        CurrentFolderName
    Protected:
        Nodes
        BlockSize
        cwd
        GraphFileName
        GraphFileSuffix
        FolderName
        BlockFileName
        BlockFileSuffix
        Node_Cache_BlockSize
        ABInterval
        ABSlot
        ABSlots
        xSize
        ySize
        zSize
        xCount
        yCount
        zCount
EndClass


Node = Class
    Public:
        add_friend
        Get_NodeID
        Get_Friends
        Get_Coords
        Get_Cost
        Set_Cost
    Protected:
        NodeID
        Friends
        Cost
        Coords
EndClass


#####################################################################################

UserInterface = Class
    Public:
        Login
        GetNoFlyZones
        AddNoFlyZone
        RemoveNoFlyZone
        ModifyNoFlyZoneLevel
        AddDrone
        RemoveDrone
        GetDroneID
        GetDroneCredentials
        SetDroneCredentials
        CheckDroneOwnership
        GetDroneInfo
        GetDronesUser
        GetDronesAll
        GetUserID
        GetUsername
        AddUser
        SetFlightVisibility
        SetAccountType
        UserChangePassword
        GetFlightsUser
        GetFlightsAll
        AddFlight
        RemoveFlight
        GetFlightWaypointsUser
        GetFlightWaypointsAll
        GetMonitorID
        GetMonitorName
        AddMonitorPermission
        RemoveMonitorPermission
        ModifyMonitorPermissionDate
        GetMonitorPermissionUser
        Exit
        Send
        Recv
    Protected:
        Username
        Crypto
        con
EndClass

###########################################################################

UserTextUI = Class
    Public:
        Main_Loop
        PrintMainMenu
        GetMenuChoice
        EvaluateChoice
        DisplayResults
        Login
        GetNoFlyZones
        AddNoFlyZone
        RemoveNoFlyZone
        ModifyNoFlyZoneLevel
        AddDrone
        RemoveDrone
        GetDroneID
        GetDroneCredentials
        SetDroneCredentials
        CheckDroneOwnership
        GetDroneInfo
        GetDronesUser
        GetDronesAll
        GetUserID
        GetUsername
        AddUser
        SetFlightVisibility
        SetAccountType
        UserChangePassword
        GetFlightsUser
        GetFlightsAll
        AddFlight
        RemoveFlight
        GetFlightWaypointsUser
        GetFlightWaypointsAll
        GetMonitorID
        GetMonitorName
        AddMonitorPermission
        RemoveMonitorPermission
        ModifyMonitorPermissionDate
        GetMonitorPermissionUser
        Call_Exit
    Protected:
        UserInterface
        MenuOptions
        Exit
EndClass


#############################################################################

Coordinate = Class
    Public:
        Get_X
        Get_Y
        Get_Z
        Set_X
        Set_Y
        Set_Z
        Get_X_Size
        Get_Y_Size
        Get_Z_Size
        Set_X_Size
        Set_Y_Size
        Set_Z_Size
        Print
        getTuple
        copy
    Protected:
        x
        y
        z
        xSize
        ySize
        zSize
    Private:
        __str__         #Overridden String method of class
EndClass

###########################################################################

Crypter = Class
    Public:
        SetMode
        GenerateKey
        ClientGenerateKey
        ClientPreSharedKeys
        ClientExchangeKeys
        ServerGenerateKey
        ServerGenerateKeys
        GetServerCertificateChain
        ServerSetKey
        SetEncryptionKeys
        Encrypt
        Decrypt
        Send
        Recv
        SplitData
    Protected:
        con
        mode
        Exit            #This could be simply a local variable however the general "server" program layout uses this system and later ajustments may uses this as an attribute, therefore it is an attribute not a local variable
        AESKey
        IV
        EncryptAES
        DecryptAES
EndClass

###########################################################################

DBConnection = Class
    Public:
        Exit
        Table_Headers
        AddDrone
        RemoveDrone
        DroneCheckCredentials
        DroneGetDroneInfo
        GetDroneID
        GetDroneCredentials
        SetDroneCredentials
        CheckDroneOwnership
        GetDroneInfo
        GetDronesUSer
        GetDronesAll
        UpdateDroneStatus
        GetUserID
        GetUsername
        AddUser
        CheckCredentials
        SetFlightVisibility
        SetAccountType
        UserChangePassword
        GetFlightsUser
        GetFlightsAll
        AddFlight
        RemoveFlight
        CheckForFlight
        GetFlight
        MarkFlightComplete
        GetCompletedFlightIDs
        CleanFlights
        GetFlightWaypoints
        GetFlightWaypointsUSer
        GetFlightWaypointsAll
        AddWaypoint
        AddWaypoints
        RemoveFlightWaypoints
        CleanCompletedFlightWaypoints
        AddMonitor
        MonitorCheckCredentials
        MonitorChangePassword
        GetMonitorDrones
        GetMonitorFlights
        GetMonitorFlightWaypoints
        GetMonitorID
        GetMonitorName
        AddMonitorPermission
        RemoveMonitorPermission
        ModifyMonitorPermissionDate
        GEtMonitorPermissionUser
        GetMonitorPermissionMonitor
        UpdateMonitorPermissionLastAccessed
        CleanMonitorPermissions
        AddNoFlyZone
        RemoveNoFlyZone
        ModifyNoFlyZoneLevel
        GetNoFlyZone
        Bot_addValue
        Bot_getCommand
        Bot_getStack
        Bot_getStackSize
        Bot_flushStack
        Bot_SetUserID
        Bot_GetUserID
        ResetDatabase
    Protected:
        db_con
        cur
        cur_header
EndClass

##############################################################################

DroneInterface = Class
    Public:
        Send
        Recv
        Login
        UpdateDroneStatus
        DroneGetDroneInfo
        CheckForFlight
        GetFlight
        GetFlightWaypoints
        MarkFlightComplete
        Exit
    Protected:
        con
        Crypto
        DroneName
EndClass

Flight = Class
    Public:
        Get_FlightID
        Get_DronID
        Get_StartCoord
        Get_EndCoord
        Get_StartTime
        Get_ETA
        Get_Distance
    Protected:
        FlightID
        DroneID
        StartCoord
        EndCoord
        StartTime
        ETA
        Distance
EndClass

Waypoint = Class
    Public:
        Get_FlightID
        Get_WaypointNumber
        Get_Coord
        Get_ETA
    Protected:
        FlightID
        WaypointNumber
        Coord
        ETA
EndClass

DroneInformation = Class
    Public:
        Get_DroneID
        Get_UserID
        Get_DroneName
        Get_DroneType
        Get_DroneSpeed
        Get_DroneRane
        Get_DroneWeight
    Protected:
        DroneID
        UserID
        DroneName
        DroneType
        DroneSpeed
        DroneRange
        DroneWeight
EndClass


############################################################################
        

DroneLogicSystem = Class
    Public:
        Main
        CheckForFlight
        RunFlight
    Protected:
        DroneID
        DronePassword
        FlightQueue
        StatusQueue
        GPIO_Queue
        Sleep_Time
        D
EndClass

############################################################################

Thread_Handle = Class
    Public:
        Get_Thread_Name
        Get_ThreadPointer
        Get_Queue
    Protected:
        Thread_Name
        Thread_Pointer
        Queue
EndClass

Thread_Controller = Class
    Public:
        Create_Thread
        Close_Thread
        PassData
        Main
        Reset
    Protected:
        Name
        Command_Queue
        Threads
        Exit
EndClass
        

##########################################################################

MonitorInterface = Class
    Public:
        Send
        Recv
        Login
        AddMonitor
        MonitorChangePassword
        GetNoFlyZones
        GetDronesAll
        GetUserID
        GetUsername
        GetMonitorDrones
        GetMonitorFlights
        GetMonitorFlightWaypoints
        GetMonitorID
        GetMonitorName
        RemoveMonitorPermission
        GetMonitorPermissionMonitor
        GetFlightsAll
        GetFlightWaypointsAll
        Exit
    Protected:
        con
        Crypto
        MonitorName
EndClass

########################################################################

Camera = Class
    Public:
        GetZoom
        SetZoom
        IncrementCameraCoordX
        IncrementCameraCoordY
        SetCameraCoords
        UpdateCameraSize
        CameraWipe
        ResetDrawObject
        AddDrawObject
        Get_DrawObjects
        Get_Coord
        Draw
    Protected:
        xpixel
        ypixel
        gameDisplay
        MinCoords
        MaxCoords
        CameraCoord
        CameraZoom
        DrawObjects
EndClass

Monitor_Sprite = Class
    Public:
        Make_Image
        Make_Text
        Get_Coords
    Protected:
        Coords
        Type
        Text
        Colour
        image
EndClass

TimeWarper
    Public:
        GetTimeWarp
    Protected:
        targetFrameRate
        minimumFrameRate
        Time
EndClass

##########################################################################

NoFlyZoneGrapher = Class
    Public:
        Main_Loop
        Force_Write
        Mod
        GetNoFlyZones
        Make_Values
    Protected:
        DB
        Interval
        Thread_Name
        Thread_Queue
        xSize
        ySize
        zSize
        Exit
EndClass
        
###########################################################################

OWM_Control = Class
    Public:
        Get_Adjusted_Speed
    Protected:
        owm
EndClass
