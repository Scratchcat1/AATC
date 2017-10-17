import math

class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize
        
    def Get_X(self):
        return self.x
    def Get_Y(self):
        return self.y
    def Get_Z(self):
        return self.z

    def Print(self):
        print("Coordinate:")
        print("X: {:<8}   xSize:{:<8}".format(round(self.x,7),self.xSize))
        print("Y: {:<8}   ySize:{:<8}".format(round(self.y,7),self.ySize))
        print("Z: {:<8}   zSize:{:<8}".format(round(self.z,7),self.zSize))

    def __str__(self):
        return str((round(self.x,8),round(self.y,8),round(self.z,8)))

    def copy(self):
        return Coordinate(self.x,self.y,self.z,self.xSize,self.ySize,self.zSize)


def AddCoords(Coord,VectorCoord):   #Simulates the drone moving
    Coord.x += VectorCoord.x
    Coord.y += VectorCoord.y
    Coord.z += VectorCoord.z
    return Coord

def CalculateVector(Coords,TargetCoords,Speed):
    dx = TargetCoords.x- Coords.x
    dy = TargetCoords.y- Coords.y
    dz = TargetCoords.z- Coords.z


    yCircumference = 40008000
    xCircumference = 40075160
    #Converts to metres
    mdy = dy * yCircumference /360
    mdx = dx * xCircumference * math.cos(toRadian(TargetCoords.y)) /360
    
    v = math.sqrt(mdx**2+mdy**2+ dz**2)
    ratio = Speed/v
    svx = dx*ratio  #Gets Speed vectors
    svy = dy*ratio
    svz = dz*ratio
    return Coordinate(svx,svy,svz)

def toRadian(x):
    return x*math.pi/180

def toDegree(x):
    return 180*x/math.pi


def DeltaCoordToMetres(aCoord,bCoord):
    #Formula for dx and dy from : https://stackoverflow.com/questions/3024404/transform-longitude-latitude-into-meters
    dx = abs(aCoord.x - bCoord.x)
    dy = abs(aCoord.y - bCoord.y) # in degrees
    dz = abs(aCoord.z - bCoord.z)


    yCircumference = 40008000
    xCircumference = 40075160
    
    mdy = dy * yCircumference /360
    mdx = dx * xCircumference * math.cos(toRadian(aCoord.y)) /360

    Distance = math.sqrt(mdx**2 + mdy**2 + dz**2)
    return Distance
