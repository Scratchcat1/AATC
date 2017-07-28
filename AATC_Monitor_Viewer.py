import pygame,AATC_Monitor
pygame.init()



class Camera:
    def __init__(self,xpixel,ypixel):
        self.xpixel = xpixel
        self.ypixel = ypixel
        self.gameDisplay = pygame.display.set_mode((self.xpixel,self.ypixel))
        self.CameraX = 0
        self.CameraY = 0
        self.CameraWidth = self.xpixel
        self.CameraHeight = self.ypixel
        self.CameraZoom = 1
        self.DrawObjects = []

    def GetZoom(self):
        return self.CameraZoom
    def SetZoom(self,Zoom):
        self.CameraZoom = Zoom

    def GetCameraCoords(self):
        return (self.CameraX,self.CameraY)
    def SetCameraCoords(self,CameraX,CameraY):
        self.CameraX = CameraX
        self.CameraY = CameraY

    def UpdateCameraSize(self):
        self.CameraWidth = self.xpixel//self.CameraZoom
        self.CameraHeight = self.ypixel//self.CameraZoom

    def CameraWipe(self,Colour = (0,0,0)):
        self.DrawObjects = []
        self.gameDisplay.fill(Colour)

    def AddDrawObject(self,Surface,ForceDraw):
        self.DrawObjects.append({"Surface":Surface,"ForceDraw":ForceDraw})

    def Draw(self):
        CameraEndX= self.CameraX + self.CameraWidth
        CameraEndY = self.CameraY + self.CameraHeight
        for DrawObject in self.DrawObjects:
            if DrawObject.rect.x in range(self.CameraX,CameraEndX) or (DrawObject.rect.x+DrawObject.rect.width) in range(self.CameraX,CameraEndX) and \
               DrawObject.rect.y in range(self.CameraY,CameraEndY) or (DrawObject.rect.y+DrawObject.rect.height) in range(self.CameraY,CameraEndY) :  #If DrawObject intersects with Camera , Render, otherwise ignore
                self.gameDisplay.blit(DrawObject,(DrawObject.rect.x-self.CameraX  ,DrawObject.rect.y-self.CameraY))  #Draw sprite
                                                    
class Drone(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,font,Coords,Text = "",Colour = (255,255,255)):
        self.x,self.y,self.width,self.height = x,y,width,height
        super().__init__()
        self.font = font
        self.Coords = Coords
        self.Text = Text
        self.Colour = Colour
        
    def Make_Image(self):
        self.image= pygame.Surface((self.width,self.height)).convert()
        self.image.fill(Colour)
        self.CoordsText = self.font.render(str(Coords,)))#####################################################################################################

M = AATC_Monitor.CreateMonitorInterface()                                                              
