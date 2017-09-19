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
