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
    """ Selects all NoFlyZones, calculates the nodes which they correspond to and modifies the cost of those nodes
        Reads all NoFlyZones and converts into dictionary object and adds to list.
        This list is then read and converted into a dictionary of NodeID:MaxCost
        Then for all nodes, the node is loaded, cost modified
        Then graph is saved
        Repeats every interval seconds.
        Must load entire graph and all NoFlyZones at once as if a NoFlyZone is removed there may be other smaller NoFlyZones which affect the cost of the node.
        Very RAM intensive. Could be run on a different device and update via a network share.
        Could use an A/B method to update if file locking occurs where the Updating takes place on one set of data while the other set of data is read from by eg A* pathfinding

    """
    def __init__(self,Interval = 36000):
        self.DB = AATC_DB.DBConnection()
        self.Interval = Interval

        graph = AATC_AStar.DynoGraph()
        graph.ImportGraph()
        self.xSize,self.ySize,self.zSize = graph.xSize,graph.ySize,graph.zSize
        del graph

        self.Main_Loop()
        
    def Main_Loop(self):
        while True:
            try:
                NoFlyZoneData = self.GetNoFlyZones()
                self.Make_Values(NoFlyZoneData)
            except Exception as e:
                print("Error occured in NoFlyZoneGrapher",e)
            print("NoFlyZoneGrapher completed. Sleeping...")
            time.sleep(self.Interval)
        
    def Mod(self,Coords):
        return int(Coords.x//self.xSize),int(Coords.y//self.ySize),int(Coords.z//self.zSize)
        
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
            for x in range(StartX,EndX+1):   #For every block which is in the NoFlyZone
                for y in range(StartY,EndY+1):
                    for z in range(StartZ,EndZ+1):
                        NodeID = graph.Direct_NodeID(x,y,z)  #Gets NodeID for that area
                        print(NodeID)
                        if NodeID in Values:
                            v = max([Zone["Level"],Values[NodeID]])
                        else:
                            v = Zone["Level"]

                        Values[NodeID] = v  #This gets the maximum cost for that node

        ######MODIFY TO BE OK
        graph.Node_Cache = {}  #Reduces memory usage.

        
        print("[NoFlyZoneGrapher] Length of Values:",len(Values))
        for NodeID in graph.All_NodeIDs():
            node = graph.GetNode(NodeID)
            if node.NodeID in Values:
                node.Cost = Values[node.NodeID]
                Values.pop(node.NodeID)# Reduce memory usage by evicting Node values which have been added already
            else:
                node.Cost = 1
        try:
            graph.SaveNodes()
        except Exception as e:
            print("Error saving nodes",e," Most likely no NoFlyZoneData yet")

        del graph

        

                        
                        
            
            
        








        
