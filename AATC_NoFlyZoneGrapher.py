import AATC_DB,AATC_AStar,ast,time

class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize

class NoFlyZoneGrapher:
    def __init__(self,xSize,ySize,zSize,Interval = 36000):
        self.DB = AATC_DB.DBConnection()
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize
        self.Interval = Interval

    def Mod(self,Coords):
        return int(Coords.x//self.xSize),int(Coords.y//self.ySize),int(Coord.z//self.zSize)
        
    def GetNoFlyZones(self):
        _,Columns,Data = self.DB.GetNoFlyZones()
        Columns = ast.literal_eval(Columns)
        
        ZoneIDIndex = Columns.index("ZoneID")#Gets indexes for the columns
        StartCoordIndex = Columns.index("StartCoord")
        EndCoordIndex = Columns.index("EndCoord")
        LevelIndex = Columns.index("Level")
        OwnerUserIDIndex = Columns.index("OwnerUserID")
        
        ProcessedData = []
        for line in Data:  #Converts each line into a dict with the column name as a key
            lineDict = {
                "ZoneID":line[ZoneIDIndex],
                "StartCoord":Coordinate(*ast.literal_eval(line[StartCoordIndex])),
                "EndCoord":Coordinate(*ast.literal_eval(line[EndCoordIndex])),
                "Level":line[LevelIndex],
                "OwnerUserID":line[OwnerUserIDIndex]}
            ProcessedData.append(lineDict)  #Also turns sthe coords into objects rather than strings
            
        return ProcessedData

    def Make_Values(self,NoFlyZoneData):
        graph = AATC_AStar.DynoGraph()
        graph.ImportGraph()
        Values = {}
        for Zone in NoFlyZoneData:
            StartCoord = Zone["StartCoord"]
            EndCoord = Zone["EndCoord"]

            StartX, StartY, StartZ = self.Mod(StartCoord)
            EndX, EndY, EndZ = self.Mod(EndCoord)

            for x in range(StartX,EndX):   #For every block which is in the NoFlyZone
                for y in range(StartY,EndY):
                    for z in range(StartZ,EndZ):
                        NodeID = graph.Direct_NodeID(x,y,z)  #Gets NodeID for that area

                        if NodeID in Values:
                            v = max([Zone["Level"],Values[NodeID]])
                        else:
                            v = Zone["Level"]

                        Values[NodeID] = v  #This gets the maximum cost for that node

        for NodeID in graph.All_NodeIDs():
            node = graph.GetNode(NodeID)
            if node.NodeID in Values:
                node.Cost = Values[node.NodeID]
            else:
                node.Cost = 1
        graph.SaveNodes()
        time.sleep(self.Interval)

                        
                        
            
            
        








        
