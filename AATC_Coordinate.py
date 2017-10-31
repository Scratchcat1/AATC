import math

class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self._x = x
        self._y = y
        self._z = z
        self._xSize = xSize
        self._ySize = ySize
        self._zSize = zSize
        
    def Get_X(self):
        return self._x
    def Get_Y(self):
        return self._y
    def Get_Z(self):
        return self._z

    def Set_X(self,x):
        self._x = x
    def Set_Y(self,y):
        self._y = y
    def Set_Z(self,z):
        self._z = z

    def Get_XSize(self):
        return self._xSize
    def Get_YSize(self):
        return self._ySize
    def Get_ZSize(self):
        return self._zSize

    def Set_XSize(self,x):
        self._xSize = x
    def Set_YSize(self,y):
        self._ySize = y
    def Set_ZSize(self,z):
        self._zSize = z


    def Print(self):
        print("Coordinate:")
        print("X: {:<8}   xSize:{:<8}".format(round(self._x,7),self._xSize))
        print("Y: {:<8}   ySize:{:<8}".format(round(self._y,7),self._ySize))
        print("Z: {:<8}   zSize:{:<8}".format(round(self._z,7),self._zSize))

    def __str__(self):
        return str((round(self._x,8),round(self._y,8),round(self._z,8)))

    def getTuple(self):
        return (self._x,self._y,self._z)

    def copy(self):
        return Coordinate(self._x,self._y,self._z,self._xSize,self._ySize,self._zSize)


def AddCoords(Coord,VectorCoord):   #Simulates the drone moving
    x = Coord.Get_X() + VectorCoord.Get_X()
    y = Coord.Get_Y() + VectorCoord.Get_Y()
    z = Coord.Get_Z() + VectorCoord.Get_Z()
    Coord.Set_X(x)
    Coord.Set_Y(y)
    Coord.Set_Z(z)
    return Coord

def CalculateVector(Coords,TargetCoords,Speed):
    dx = TargetCoords.Get_X()- Coords.Get_X()
    dy = TargetCoords.Get_Y()- Coords.Get_Y()
    dz = TargetCoords.Get_Z()- Coords.Get_Z()


    yCircumference = 40008000
    xCircumference = 40075160
    #Converts to metres
    mdy = dy * yCircumference /360
    mdx = dx * xCircumference * math.cos(toRadian(TargetCoords.Get_Y())) /360
    
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


def AtWaypoint(Coords,WaypointCoords,xSize,ySize,zSize):
    x,y,z = False,False,False
    if abs(Coords.Get_X()-WaypointCoords.Get_X()) <= xSize:
        x = True
    if abs(Coords.Get_Y()-WaypointCoords.Get_Y()) <= ySize:
        y = True
    if abs(Coords.Get_Z()-WaypointCoords.Get_Z()) <= zSize:
        z = True
    return all([x,y,z])


def DeltaCoordToMetres(aCoord,bCoord):
    #Formula for dx and dy from : https://stackoverflow.com/questions/3024404/transform-longitude-latitude-into-meters
    dx = abs(aCoord.Get_X() - bCoord.Get_X())
    dy = abs(aCoord.Get_Y() - bCoord.Get_Y()) # in degrees
    dz = abs(aCoord.Get_Z() - bCoord.Get_Z())


    yCircumference = 40008000
    xCircumference = 40075160
    
    mdy = dy * yCircumference /360
    mdx = dx * xCircumference * math.cos(toRadian(aCoord.Get_Y())) /360

    Distance = math.sqrt(mdx**2 + mdy**2 + dz**2)
    return Distance
