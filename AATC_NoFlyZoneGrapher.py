import AATC_DB,AATC_AStar,ast,time,AATC_Config,AATC_Coordinate

def NoFlyZoneGrapher_Launch(Thread_Name,Thread_Queue,Interval = 36000):  
    NFZG = NoFlyZoneGrapher(Thread_Name,Thread_Queue,Interval)
    NFZG.Main_Loop()

class NoFlyZoneGrapher:
    """ Selects all NoFlyZones, calculates the nodes which they correspond to and modifies the cost of those nodes
        Reads all NoFlyZones and converts into dictionary object and adds to list.
        This list is then read and converted into a dictionary of NodeID:MaxCost
        Then for all nodes, the node is loaded, cost modified
        Then graph is saved
        Repeats every interval seconds.
        Must load entire graph and all NoFlyZones at once as if a NoFlyZone is removed there may be other smaller NoFlyZones which affect the cost of the node.  #DEALT WITH , DONE IN GROUPS
        Very RAM intensive. Could be run on a different device and update via a network share.
        Could use an A/B method to update if file locking occurs where the Updating takes place on one set of data while the other set of data is read from by eg A* pathfinding

    """
    def __init__(self,Thread_Name,Thread_Queue,Interval = 36000):
        self._DB = AATC_DB.DBConnection()
        self._Interval = Interval
        self._Thread_Name = Thread_Name
        self._Thread_Queue = Thread_Queue

        graph = AATC_AStar.DynoGraph()
        graph.ImportGraph()
        self._xSize,self._ySize,self._zSize = graph.Get_Size()
        del graph

    
        
    def Main_Loop(self):
        self._Exit = False
        while not self._Exit:
            try:
                NoFlyZoneData = self.GetNoFlyZones()
                self.Make_Values(NoFlyZoneData)
            except Exception as e:
                print("Error occured in NoFlyZoneGrapher",e)
            print("NoFlyZoneGrapher completed. Sleeping...")
            time.sleep(self._Interval)

            if not self._Thread_Queue.empty():
                data = self._Thread_Queue.get()
                Command,Arguments = data[0],data[1]
                if Command == "Exit":
                    self._Exit = True
                    
        print("NoFlyZoneGrapher exiting...")

    def Force_Write(self):  #Cycles through all slots and writes current state.
        graph = AATC_AStar.DynoGraph()
        graph.ImportGraph()
        NoFlyZoneData = self.GetNoFlyZones()
        for Slot in range(len(graph.GetFolderNames())):
            self.Make_Values(NoFlyZoneData,ABSlot = Slot)
        
    def Mod(self,Coords):
        return int(Coords.Get_X()//self._xSize),int(Coords.Get_Y()//self._ySize),int(Coords.Get_Z()//self._zSize)
        
    def GetNoFlyZones(self):
        _,Columns,Data = self._DB.GetNoFlyZones()
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
                "StartCoord":AATC_Coordinate.Coordinate(*ast.literal_eval(line[StartCoordIndex])),
                "EndCoord":AATC_Coordinate.Coordinate(*ast.literal_eval(line[EndCoordIndex])),
                "Level":line[LevelIndex],
                "OwnerUserID":line[OwnerUserIDIndex]}
            ProcessedData.append(lineDict)  #Also turns sthe coords into objects rather than strings
            
        return ProcessedData

    def Make_Values(self,NoFlyZoneData,ABSlot = 1):
        graph = AATC_AStar.DynoGraph(ABSlot = ABSlot)
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
                        
                        if NodeID in Values:
                            v = max([Zone["Level"],Values[NodeID]])
                        else:
                            v = Zone["Level"]

                        Values[NodeID] = v  #This gets the maximum cost for that node

##        ######MODIFY TO BE OK
##        graph.Node_Cache = {}  #Reduces memory usage.
        graph.FlushGraph()  #Reduces memory usage by removing the Node_Caches

        print("[NoFlyZoneGrapher] Length of Values:",len(Values))
        for NodeID in graph.All_NodeIDs():   #CHECK THIS. Only using those involved with a new no fly zone may cause issues if a no fly zone was removed. Maybe should be set to all node IDs.
            node = graph.GetNode(NodeID)
            if node.Get_NodeID() in Values:
                node.Set_Cost( Values[node.Get_NodeID()])
                Values.pop(node.Get_NodeID())# Reduce memory usage by evicting Node values which have been added already
            else:
                node.Set_Cost(1)
            if NodeID % AATC_Config.NOFLYZONEGRAPHER_FLUSH_GRAPH_NUMBER == 0:  #Every N nodes the program will save the current nodes and remove them from memory
                try:
                    graph.SaveNodes([graph.CurrentFolderName()])  #Ensures any loaded nodes are saved. As all nodes in a block are loaded , entire blocks are saved thus no nodes are lost.
                except Exception as e:
                    print("Error saving nodes",e," Most likely no NoFlyZoneData yet")
                graph.FlushGraph()  #The graph nodes are then emptied to reduce memory usage.
                #print("Processede block to ",NodeID)
            
        try:
            graph.SaveNodes([graph.CurrentFolderName()])   #Saves any last nodes.
        except Exception as e:
            print("Error saving nodes",e," Most likely no NoFlyZoneData yet")

        del graph

        

                        
                        
            
            
        








        
