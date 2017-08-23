import pygame,AATC_Monitor,time,ast,sys
pygame.init()

_images= {}
def GetImage(xSize,ySize,Colour):  #Efficiently get images
    result = _images.get((xSize,ySize,Colour))
    if result == None:
        result = pygame.Surface((xSize,ySize)).convert()
        result.fill(Colour)
        _images[(xSize,ySize,Colour)]=result
##    result_copy = pygame.Surface(result.get_size())
##    result_copy.blit(result,(0,0))
    return result#_copy

_texts= {}
def GetText(Text,font,AA,Colour):  #Efficiently get text
    result = _texts.get((Text,font,AA,Colour))
    if result == None:
        result = font.render(Text,AA,Colour)
        _images[(Text,font,AA,Colour)]=result
    return result

def MaxLimit(value,Max):
    if value > Max:
        value = Max
    return value

class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize


class Camera:
    def __init__(self,xpixel,ypixel,MinCoords,MaxCoords):  #COORDS (X,Y,Z)
        self.xpixel = xpixel
        self.ypixel = ypixel
        self.gameDisplay = pygame.display.set_mode((self.xpixel,self.ypixel))
        self.MinCoords = MinCoords
        self.MaxCoords = MaxCoords
        self.CameraCoord = Coordinate(self.MinCoords[0],self.MinCoords[1])
        self.CameraCoord.xSize = self.MaxCoords[0] - self.MinCoords[0]
        self.CameraCoord.ySize = self.MaxCoords[1] - self.MinCoords[1]
        self.CameraZoom = 1
        self.DrawObjects = []

    def GetZoom(self):
        return self.CameraZoom
    def SetZoom(self,Zoom):
        self.CameraZoom = Zoom

    def GetCameraCoords(self):
        return self.CameraCoord
    def IncrementCameraCoordX(self,Amount):
        self.CameraCoord.x += Amount

    def IncrementCameraCoordY(self,Amount):
        self.CameraCoord.y += Amount
        
    def SetCameraCoords(self,CameraX,CameraY):
        self.CameraCoord.x = CameraX
        self.CameraCoord.y = CameraY

    def UpdateCameraSize(self):  #Gets width of map divided by zoom level eg at zoom 1x it has whole map
        self.CameraCoord.xSize = (self.MaxCoords[0] - self.MinCoords[0])/self.CameraZoom
        self.CameraCoord.ySize = (self.MaxCoords[1] - self.MinCoords[1])/self.CameraZoom

    def CameraWipe(self,Colour = (0,0,0)):
        self.gameDisplay.fill(Colour)
    def ResetDrawObject(self):
        self.DrawObjects = []
    def AddDrawObject(self,Object,ForceDraw):
        self.DrawObjects.append({"Object":Object,"ForceDraw":ForceDraw}) 

    def Draw(self):
        CameraEndX= self.CameraCoord.x + self.CameraCoord.xSize    #Moved to new variablt to reduce recalculation
        CameraEndY = self.CameraCoord.y + self.CameraCoord.ySize
        for DrawObject in self.DrawObjects:
            Object = DrawObject["Object"]
            if ((Object.Coords.x < CameraEndX) and ((Object.Coords.x+Object.Coords.xSize) > self.CameraCoord.x)) and \
               ((Object.Coords.y < CameraEndY) and ((Object.Coords.y+Object.Coords.ySize) > self.CameraCoord.y )) :  #If DrawObject intersects with Camera , Render, otherwise ignore
                
                PosX = ((Object.Coords.x- self.CameraCoord.x)/self.CameraCoord.xSize)* self.xpixel
                PosY = ((Object.Coords.y- self.CameraCoord.y)/self.CameraCoord.ySize)* self.ypixel
##                width,height = Object.Coords.xSize*self.CameraZoom ,Object.Coords.ySize*self.CameraZoom
                width,height = int(Object.Coords.xSize/self.CameraCoord.xSize*self.xpixel) ,int(Object.Coords.ySize/self.CameraCoord.ySize*self.ypixel)
                if width > 0 and height > 0:
                    width = MaxLimit(width,self.xpixel)
                    height = MaxLimit(height,self.ypixel)
                    font_size = int(100*width/self.xpixel)
                    Object.Make_Image(width,height) # Object has coordinates and size in these coordinates
                    self.gameDisplay.blit(Object.image,(PosX,PosY))

                    if font_size > 5:
                        font = pygame.font.Font(None, font_size) #TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS
                        Object.Make_CoordsText(font)     #TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS
                        Object.Make_Text(font)          #TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS
                        Object.Make_Type(font)         #TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS#TEST THIS

                        text_height = Object.CoordsText.get_height()
                        self.gameDisplay.blit(Object.CoordsText,(PosX+width,PosY))
                        self.gameDisplay.blit(Object.DrawnType,(PosX+width,PosY+text_height))
                        self.gameDisplay.blit(Object.DrawnText,(PosX+width,PosY+text_height*2))

             
                                                    
class Monitor_Sprite(pygame.sprite.Sprite):
    def __init__(self,CoordObject,Type = "",Text = "",Colour = (255,255,255)):
        self.Coords = CoordObject
        self.Type = Type
        self.Text = Text
        self.Colour = Colour
        self.image = pygame.Surface((1,1))
        self.Make_Image(2,2)

    def Make_Image(self,width,height):
        if self.image.get_size() != (width,height):  #If new image does not match with previous
            self.image = GetImage(width,height,self.Colour)
##            self.image = pygame.Surface((width,height)).convert()
##            self.image.fill(self.Colour)
        
    def Make_CoordsText(self,font):
        self.CoordsText = GetText(str((self.Coords.x,self.Coords.y,self.Coords.z)),font,False,self.Colour)
        #self.CoordsText = font.render(str((self.Coords.x,self.Coords.y,self.Coords.z)),False,self.Colour)

    def Make_Text(self,font):
        self.DrawnText = GetText(self.Text,font,False,self.Colour)
        #self.DrawnText = font.render(self.Text,False,self.Colour)

    def Make_Type(self,font):
        self.DrawnType = GetText(self.Type,font,False,self.Colour)
        #self.DrawnType = font.render(self.Type,False,self.Colour)


def MakeDroneSprites(Message,RawDroneList):
    DroneList = []
    Columns = ast.literal_eval(Message)
    CoordIndex = Columns.index("LastCoords")
    DroneIDIndex = Columns.index("DroneID")
    UserIDIndex = Columns.index("UserID")
    DroneNameIndex = Columns.index("DroneName")
    BatteryIndex = Columns.index("LastBattery")
    for Drone in RawDroneList:
        LastCoords = ast.literal_eval(Drone[CoordIndex])
        Coord = Coordinate(LastCoords[0],LastCoords[1],LastCoords[2],0.00001,0.00001,0.00001)
        Text = "D:"+str(Drone[DroneIDIndex]) +" U:"+str(Drone[UserIDIndex]) +" N:"+str(Drone[DroneNameIndex])+" B:"+str(Drone[BatteryIndex])
        Colour = (255,255,255)
        Sprite = Monitor_Sprite(Coord,"Drone",Text,Colour)
        DroneList.append(Sprite)
    return DroneList

def MakeFlightSprites(Message,RawFlightList):
    FlightList = []
    Columns = ast.literal_eval(Message)
    FlightIDIndex = Columns.index("FlightID")
    DroneIDIndex = Columns.index("DroneID")
    StartCoordsIndex = Columns.index("StartCoords")
    EndCoordsIndex = Columns.index("EndCoords")
    StartTimeIndex = Columns.index("StartTime")
    ETAIndex = Columns.index("ETA")
    EndTimeIndex = Columns.index("EndTime")
    DistanceIndex = Columns.index("Distance")
    for Flight in RawFlightList:
        #Start Sprite
        Coords = ast.literal_eval(Flight[StartCoordsIndex])
        Coord = Coordinate(Coords[0],Coords[1],Coords[2],0.00001,0.00001,0.00001)
        Text = "F:"+ str(Flight[FlightIDIndex])+" D:"+ str(Flight[DroneIDIndex])+ "ST:"+str(Flight[StartTimeIndex])
        Colour = (0,0,255)
        FlightList.append(Monitor_Sprite(Coord,"StartPoint",Text,Colour))

        #End Sprite
        Coords = ast.literal_eval(Flight[EndCoordsIndex])
        Coord = Coordinate(Coords[0],Coords[1],Coords[2],0.00001,0.00001,0.00001)
        Text = "F:"+ str(Flight[FlightIDIndex])+" D:"+ str(Flight[DroneIDIndex])+ "ETA:"+str(Flight[ETAIndex])
        Colour = (255,0,0)
        FlightList.append(Monitor_Sprite(Coord,"EndPoint",Text,Colour))
    return FlightList


def MakeWaypointSprites(Message,RawWaypointList):
    WaypointList = []
    Columns = ast.literal_eval(Message)
    CoordIndex = Columns.index("Coords")
    WaypointNumberIndex = Columns.index("WaypointNumber")
    FlightIDIndex = Columns.index("FlightID")
    for Waypoint in RawWaypointList:
        Coords = ast.literal_eval(Waypoint[CoordIndex])
        Coord = Coordinate(Coords[0],Coords[1],Coords[2],0.00001,0.00001,0.00001)
        Text = "F:"+ str(Waypoint[FlightIDIndex]) +" W:"+ str(Waypoint[WaypointNumberIndex])
        Colour = (0,255,0)
        WaypointList.append(Monitor_Sprite(Coord,"Waypoint",Text,Colour))
    return WaypointList

def MakeZoneSprites(Message,RawZoneList):
    ZoneList = []
    Columns = ast.literal_eval(Message)
    StartCoordIndex = Columns.index("StartCoord")
    EndCoordIndex = Columns.index("EndCoord")
    LevelIndex = Columns.index("Level")
    ZoneIDIndex = Columns.index("ZoneID")
    for Zone in RawZoneList:
        StartCoords = ast.literal_eval(Zone[StartCoordIndex])
        EndCoords = ast.literal_eval(Zone[EndCoordIndex])
        Coord = Coordinate(StartCoords[0],StartCoords[1],StartCoords[2],EndCoords[0]-StartCoords[0],EndCoords[1]-StartCoords[1],EndCoords[2]-StartCoords[2])
        Text = "Z:"+ str(Zone[ZoneIDIndex]) +" L:"+ str(Zone[LevelIndex])
        Colour = (100,100,100)
        ZoneList.append(Monitor_Sprite(Coord,"NoFlyZone",Text,Colour))
    return ZoneList

def MakeSprites(M):
    print("Refreshing data")
    SpriteList = []
    Sucess,Message,DronesAll = M.GetDronesAll()
    if Sucess:
        SpriteList += MakeDroneSprites(Message,DronesAll)
        
    Sucess,Message,DronesMonitor = M.GetMonitorDrones()
    if Sucess:
        SpriteList += MakeDroneSprites(Message,DronesMonitor)
        
    Sucess,Message,FlightsAll = M.GetFlightsAll()
    if Sucess:
        SpriteList += MakeFlightSprites(Message,FlightsAll)
        
    Sucess,Message,FlightsMonitor = M.GetMonitorFlights()
    if Sucess:
        SpriteList += MakeFlightSprites(Message,FlightsMonitor)
        
    Sucess,Message,WaypointsAll = M.GetFlightWaypointsAll()
    if Sucess:
        SpriteList += MakeWaypointSprites(Message,WaypointsAll)

    Sucess,Message,WaypointsMonitor = M.GetMonitorFlightWaypoints()
    if Sucess:
        SpriteList += MakeWaypointSprites(Message,WaypointsMonitor)

    Sucess,Message,NoFlyZones = M.GetNoFlyZones()
    if Sucess:
        SpriteList += MakeZoneSprites(Message,NoFlyZones)

    #Sprites are created in this function to simplify code in case of an error(False)
    print("Refreshed data")
    return SpriteList #All sprites which were sucessfully created



xpixel = 1000
ypixel = 500
Refresh_Delay = 60
clock = pygame.time.Clock()
Exit = "N"
while Exit != "Y":
    try:
        M = AATC_Monitor.CreateMonitorInterface(Port = 8001)
        M.Login("Zini","")
        #Sucess,Message,Data =  M.GetCoordDetails()
        #MinCoords,MaxCoords,StepCoords = Data[0],Data[1],Data[2]
        MinCoords,MaxCoords = (0,0,0),(50,50,50)
        MonCamera = Camera(xpixel,ypixel,MinCoords,MaxCoords)
        while True:
            MonCamera.ResetDrawObject()
            Sprites = MakeSprites(M)
            font = pygame.font.Font(None, 30) 
            for sprite in Sprites:
                sprite.Make_CoordsText(font)
                sprite.Make_Text(font)
                sprite.Make_Type(font)
                MonCamera.AddDrawObject(sprite,False)

            Last_Refresh_Time = time.time()
            refresh = False
            #MonCamera.SetZoom(1000000)
            while not refresh:
                MonCamera.CameraWipe()
                if time.time() >= (Last_Refresh_Time + Refresh_Delay):
                    refresh = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print("Monitor exit was called")
                        pygame.quit()
                        sys.exit()
                    
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:   #Shift camera
                        MonCamera.IncrementCameraCoordY(-0.5/MonCamera.GetZoom())  #/ as Greater zoom means need more fidelety
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                        MonCamera.IncrementCameraCoordY(0.5/MonCamera.GetZoom())
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                        MonCamera.IncrementCameraCoordX(-0.5/MonCamera.GetZoom())
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                        MonCamera.IncrementCameraCoordX(0.5/MonCamera.GetZoom())
                        
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:#Zoom out
                        MonCamera.SetZoom(0.9*MonCamera.GetZoom())
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:#Zoom in
                        MonCamera.SetZoom(1.1*MonCamera.GetZoom())
                        
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        print("Camera details")
                        print(MonCamera.GetZoom())
                        print(MonCamera.CameraCoord.x)
                        print(MonCamera.CameraCoord.y)
                        print(MonCamera.CameraCoord.xSize)
                        print(MonCamera.CameraCoord.ySize)
                        print(len(MonCamera.DrawObjects))
                        print("FPS:"+str(clock.get_fps()))
                    elif event.type == pygame.KEYDOWN:
                        pass
                MonCamera.UpdateCameraSize()
                MonCamera.Draw()
                pygame.display.flip()
                clock.tick(60)
                

            
    except Exception as e:
        print(e)
        print("An error occured, restarting main loop")
        Exit = input("Exit? Y/N").upper()


















