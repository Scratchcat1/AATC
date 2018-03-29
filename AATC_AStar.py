import os,pickle,time,math,hashlib,random#,AATC_Coordinate
#from AATC_Coordinate import *
try:
    try:
        import PriorityQueue.PriorityQueueC as PriorityQueue
    except:
        print("PriorityQueueC not available, defaulting to pure python")
        import PriorityQueue.PriorityQueue as PriorityQueue
    
except:
    print("AStarPQ not available")
try:
    _ = math.inf
except:
    print("You do not have math.inf object, Python 3.5 onwards. Will use replacement.")
    math.inf = 10**20
        
class DynoGraph:
    """ Graph object
        BlockSize affects how many nodes are saved in a single BlockFile. Shown by an N before the BlockID 
        Node_Cache_BlockSize affects how sparsly the node information is spread across files.
        Lower means more sparse and lower memory usage but potentially worse performace, saving will take longer.
        Larger means faster performance and higher memory usage.
        HDDs and other low IOPS drives -> Higher
        SSDs and other high IOPS drives -> Lower


            """
    def __init__(self,BlockSize = 500,FolderName = "GraphFolder",GraphFileName = "Graph",GraphFileSuffix = ".graph",BlockFileName = "GraphBlock",BlockFileSuffix = ".blk",Node_Cache_BlockSize = 40, ABInterval = 36000, ABSlot = 0, ABSlots = 2):
        self._Nodes = {}
        self._BlockSize = BlockSize
        self._cwd = os.getcwd()

        self._GraphFileName = GraphFileName
        self._GraphFileSuffix = GraphFileSuffix
        self._FolderName = FolderName
        self._BlockFileName = BlockFileName
        self._BlockFileSuffix = BlockFileSuffix
        self._Node_Cache_BlockSize = Node_Cache_BlockSize

        self._ABInterval = ABInterval
        self._ABSlot = ABSlot
        self._ABSlots = ABSlots
        
        
    def Size(self,xSize,ySize,zSize):   #Sets size of graph grid
        self._xSize = xSize
        self._ySize = ySize
        self._zSize = zSize

    def Get_Size(self):                 #Gets size of graph grid
        return self._xSize, self._ySize, self._zSize

    def Get_Count(self):                #Get the count values for each dimension
        return self._xCount, self._yCount, self._zCount
    
    def add_node(self,node):            #Add a node object to the graph
        self._Nodes[node.Get_NodeID()] = node


    
    def Add_Edges(self,xRange,yRange,zRange):       #Add the edges to the graph
        print("Adding edges...")
        self._xCount = int(xRange/self._xSize)
        self._yCount = int(yRange/self._ySize)
        self._zCount = int(zRange/self._zSize)
        
        
        print("xCount:",self._xCount)
        print("yCount:",self._yCount)
        print("zCount:",self._zCount)
        

        for node in self._Nodes.values():       #Calculate edges for each node
            friends = self.CalculateNeighbours(node.Get_NodeID(),self._xCount,self._yCount,self._zCount)
            for friend in friends:
                node.add_friend(friend)         #Add edges to nodes.

    def CalculateNeighbours(self,NodeID,xCount,yCount,zCount):
        zlow,zhigh,ylow,yhigh,xlow,xhigh = False,False,False,False,False,False
        friends = []
        if (NodeID - 1) % zCount != 0:  # If not on bottom level of z
            zlow = True
        if NodeID % zCount != 0:   # if not on top level of z
            zhigh = True

        if ((NodeID-1) % (zCount*yCount)) >= zCount:   #Not on low y row
            ylow = True
        if ((NodeID-1)% (zCount*yCount))//zCount != yCount-1:  # Not on high y row
            yhigh = True

        if (NodeID-1) // (zCount*yCount) != 0:  # not on low x set
            xlow = True
        if (NodeID-1) // (zCount*yCount) != (xCount-1):
            xhigh = True

            
        #Code below finds the nodeIDs of each of the nodes neighbours by detecting if the node is not on an edge of the area for the graph.
        if zlow:
            friends.append(NodeID-1)
            if ylow:
                friends.append((NodeID-1)-zCount)
                if xlow:
                    friends.append((NodeID-1)-zCount-(zCount*yCount))
                if xhigh:
                    friends.append((NodeID-1)-zCount+(zCount*yCount))
            if yhigh:
                friends.append((NodeID-1)+zCount)
                if xlow:
                    friends.append((NodeID-1)+zCount-(zCount*yCount))
                if xhigh:
                    friends.append((NodeID-1)+zCount+(zCount*yCount))
        if zhigh:
            friends.append(NodeID+1)
            if ylow:
                friends.append((NodeID+1)-zCount)
                if xlow:
                    friends.append((NodeID+1)-zCount-(zCount*yCount))
                if xhigh:
                    friends.append((NodeID+1)-zCount+(zCount*yCount))
            if yhigh:
                friends.append((NodeID+1)+zCount)
                if xlow:
                    friends.append((NodeID+1)+zCount-(zCount*yCount))
                if xhigh:
                    friends.append((NodeID+1)+zCount+(zCount*yCount))
            
        if ylow:
            friends.append(NodeID-zCount)
            if xlow:
                friends.append(NodeID-zCount-(zCount*yCount))
            if xhigh:
                friends.append(NodeID-zCount+(zCount*yCount))
        if yhigh:
            friends.append(NodeID+zCount)
            if xlow:
                friends.append(NodeID+zCount-(zCount*yCount))
            if xhigh:
                friends.append(NodeID+zCount+(zCount*yCount))


        if zlow:
            if xlow:
                friends.append((NodeID-1)-(zCount*yCount))
            if xhigh:
                friends.append((NodeID-1)+(zCount*yCount))

        if zhigh:
            if xlow:
                friends.append((NodeID+1)-(zCount*yCount))
            if xhigh:
                friends.append((NodeID+1)+(zCount*yCount))

        if xlow:
            friends.append(NodeID-(zCount*yCount))
        if xhigh:
            friends.append(NodeID+(zCount*yCount))

        return friends
    
    ###################################
    
    def MapHash(self,value,div):        #Get the hash of the value passed
        return int(value//div)

    def Node_Cache_Hash(self,Key):      #Find the hash for the node cache value.
        return int(int(hashlib.md5(str(Key).encode('utf8')).hexdigest()[:8],16)%self._Node_Cache_BlockSize) #Generates integer hash of key then int div by BlockSize
        
    ##################################
    
    def Build_Node_Cache(self):         #Precalculates the node_cache values
        self._Node_Cache = {}
        for node in self._Nodes.values():
            x = node.Get_Coords().Get_X() + 0.25*self._xSize    #Prevents floating point rounding errors
            y = node.Get_Coords().Get_Y() + 0.25*self._ySize    #Otherwise integer division may map a node on top of another (x+1)//y = x//y in edge cases if x 
            z = node.Get_Coords().Get_Z() + 0.25*self._zSize

            mx,my,mz = self.MapHash(x,self._xSize),self.MapHash(y,self._ySize),self.MapHash(z,self._zSize)
            self._Node_Cache[(mx,my,mz)] = node.Get_NodeID()

    def Save_Node_Cache(self):
        print("Preparing to save Node Cache")
        Sets = {}
        for Key in self._Node_Cache:
            r = self.Node_Cache_Hash(Key)  #Gets Hashed key
            if r not in Sets:
                Sets[r] = {}
            Sets[r][Key] = self._Node_Cache[Key]  #Adds the item to the set
            
        print("Saving Node Cache. Sets:",len(Sets))
        for Letter in self.GetFolderNames():            #Writes to all copies as this subroutine will only be run on graph generation
            for Set in Sets:
                filename = os.path.join(self._cwd,self._FolderName,Letter,self._BlockFileName+"NC"+str(Set)+self._BlockFileSuffix)      #Generates the path to the file
                data = Sets[Set]
                with open(filename,"wb") as file:
                    pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)               #Dumps the set using pickle.


    def Get_Node_Cache(self,x,y,z):     #Load nodeID for a given coordinate using the key
        Key = (x,y,z)
        if Key not in self._Node_Cache:
            NCBlockID = self.Node_Cache_Hash(Key)
            try:
                filename = os.path.join(self._cwd,self._FolderName,self.CurrentFolderName(),self._BlockFileName+"NC"+str(NCBlockID)+self._BlockFileSuffix)
                with open(filename,"rb") as file:
                    block = pickle.load(file)
                self._Node_Cache.update(block)
            
            except Exception as e:
                print(e)

        if Key in self._Node_Cache:
            return self._Node_Cache[Key]
        else:
             #Raises error if cannot get node
            raise ValueError("Node_Cache Key requested is not in the NCBlockID checked. Check BlockSize or regenerate blockfiles.")

            
    def Direct_NodeID(self,x,y,z):  #Access NodeID without first mapping the coordinates
        return self.Get_Node_Cache(x,y,z)

    def All_NodeIDs(self,StartValue = 1, MaxValue = None):
        if MaxValue == None:
            MaxValue = self._xCount*self._yCount*self._zCount + (StartValue-1) #Gets Maximum start value, StartValue gives the starting NodeID. -1 as x*y*z = max, if start at 1 and therefore xyz +1-1 = max value. XYZ as eg x=2,y=10,z=5 you will have 100 blocks ,starting at 1 so 100 is max.
                        
        NodeIDList = []
        for NodeID in range(1,MaxValue+1):
            NodeIDList.append(NodeID)
            
        return NodeIDList

    def Find_NodeID(self,x,y,z):    #Find the NodeID a coordinate is for 
        mx,my,mz = self.MapHash(x,self._xSize),self.MapHash(y,self._ySize),self.MapHash(z,self._zSize)
        NodeID = self.Get_Node_Cache(mx,my,mz)
        return NodeID

    def Obj_Find_NodeID(self,Obj):  
        x,y,z = Obj.Get_Coords().Get_X(),Obj.Get_Coords().Get_Y(),Obj.Get_Coords().Get_Z()
        NodeID = self.Find_NodeID(x,y,z)
        return NodeID

    
    #############################

    def SaveGraph(self,AutoNodeSave = True,AutoNodeCacheSave = True):   #Save the graph to the disk.
        print("Saving graph...")
        for Letter in self.GetFolderNames():
            os.makedirs(os.path.join(os.getcwd(),self._FolderName,Letter),exist_ok = True)
        if AutoNodeSave:
            self.SaveNodes()
        if AutoNodeCacheSave:
            self.Save_Node_Cache()

        self._Nodes = {}
        self._Node_Cache = {}
        for Letter in self.GetFolderNames():
            try:
                filename = os.path.join(self._cwd,self._FolderName,Letter,self._GraphFileName+self._GraphFileSuffix)
                with open(filename,"wb") as file:
                    pickle.dump(self,file,protocol = pickle.HIGHEST_PROTOCOL)
                print("Saved graph sucessfully")
            except Exception as e:
                print("Error occured while saving graph file ",e)

    def ImportGraph(self):      #Loads graph properties
        print("Importing graph")
        ABSlot = self._ABSlot
        try:
            filename = os.path.join(os.getcwd(),self._FolderName,"A",self._GraphFileName+self._GraphFileSuffix)     #MUST ALWAYS HAVE ATLEAST THE FOLDER "A" in order to load the configuration
            with open(filename,"rb") as file:                                                                       #The graph at this point does not know how many copies there are
                ImportFile = pickle.load(file)
                
            self.__dict__.update(ImportFile.__dict__)
            print("Imported graph sucessfully")
        except Exception as e:
            print("An error occured while importing graph data",e)
            
        self._cwd = os.getcwd()
        self._ABSlot = ABSlot
    
    ################
    def Hash(self,Value):
        return int(Value//self._BlockSize)
    
    def GetNode(self,NodeID):           #Takes a nodeID, finds the hash, finds the file with the node ( a block) and loads this block.
        if NodeID not in self._Nodes:
            BlockID = self.Hash(NodeID)
            try:
                filename = os.path.join(self._cwd,self._FolderName,self.CurrentFolderName(),self._BlockFileName+"N"+str(BlockID)+self._BlockFileSuffix)
                with open(filename,"rb") as file:
                    block = pickle.load(file)

                self._Nodes.update(block)
                

            except Exception as e:
                print(e)

        if NodeID in self._Nodes:
            return self._Nodes[NodeID]
        else:
             #Raises error if cannot get node
            raise ValueError("NodeID requested is not in the BlockID checked. Check BlockSize or regenerate blockfiles. NodeID: "+str(NodeID))      #If an error occured ( node was not loaded). This is normally the case if the graph has not been generated correctly.

    def SaveNodes(self,FolderNames = None):         #Saves the current graph into the folders defined by the set FolderNames, or all if FolderNames = None.
        if FolderNames == None:
            FolderNames = self.GetFolderNames()
        Sets = {}
        m = self.Hash(max(self._Nodes))  #Finds max blockID
        for x in range(m+1):
            Sets[x] = {}   #Creates sets for each block

        for node in self._Nodes.values():
            r = self.Hash(node.Get_NodeID())
            Sets[r][node.Get_NodeID()] = node

        for Letter in FolderNames:
            for Set in Sets: #Set = BlockID
                if len(Sets[Set]) != 0:  #If set is not empty. Empty sets may cause issues with delta Node change saving.
                    filename = os.path.join(self._cwd,self._FolderName,Letter,self._BlockFileName+"N"+str(Set)+self._BlockFileSuffix)
                    data = Sets[Set]
                    with open(filename,"wb") as file:
                        pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)               #Writes the block to the file using pickle.

    def EvictNode(self,NodeID):  #Removes a node from the Nodes dict
        if NodeID in self._Nodes:
            self._Nodes.pop(NodeID)
            return True         #True if node was in memory, false if not
        else:
            return False

    def FlushGraph(self):       #Empty the graph to reduce memory usage
        self._Nodes = {}
        self._Node_Cache = {}

    def Get_Nodes(self):        #Get all nodes currently in memory
        return self._Nodes

    #######################################

    def GetFolderNames(self):       #Generates the set of foldernames the current graph will use
        names = []
        for x in range(self._ABSlots):
            names.append(chr(65+x))
        return names

    def CurrentFolderName(self):    #Finds the current folder the graph should save in.
        char = chr(  int(65+ ((time.time()+self._ABInterval*self._ABSlot)//self._ABInterval)%self._ABSlots))    
        return char
    
        
            

class Node:         #Stores the attributes of a node in object form
    def __init__(self,NodeID,Cost,Coords):
        self._NodeID = NodeID
        self._Friends = []
        self._Cost = Cost
        self._Coords = Coords
    def add_friend(self,friend):
        if friend not in self._Friends:
            self._Friends.append(friend)

    def Get_NodeID(self):
        return self._NodeID
    def Get_Friends(self):
        return self._Friends
    def Get_Coords(self):
        return self._Coords
    def Get_Cost(self):
        return self._Cost

    def Set_Cost(self,cost):
        self._Cost = cost

def EstimateDistance(Node,Target,xSize,ySize,zSize):    #Estimates the distance to the target node      A* HEURISTIC
    Node_Coords = Node.Get_Coords()
    Target_Coords = Target.Get_Coords()                 #USES THE TOTAL DISTANCE IN EACH DIMENSION TO REDUCE SEARCH TIME COMPARED TO EUCLIDIAN DISTANCE
    return (abs(Node_Coords.Get_X()-Target_Coords.Get_X())/xSize+abs(Node_Coords.Get_Y()-Target_Coords.Get_Y())/ySize+abs(Node_Coords.Get_Z()-Target_Coords.Get_Z())/zSize)
##    return math.sqrt((Node_Coords.Get_X()-Target_Coords.Get_X()/xSize)**2+(Node_Coords.Get_Y()-Target_Coords.Get_Y()/ySize)**2 + (Node_Coords.Get_Z()-Target_Coords.Get_Z()/zSize)**2)*0.9

def AStarPQ(graph,start,target):    #The priority queue version of the A* algorithm
    """
    Priority queue version of the A* algorithm.
    This replaces the task of finding the minimum of f using min with a priority queue
    This improves the performance as the size of the search increases
    However as this is less memory efficient (must keep a priority queue of all open nodes ) it is not the default option used but is offered as an alternative.

    """
    StartTime = time.time()

    xSize,ySize,zSize = graph.Get_Size()
    
    ClosedSet = {}  #Dict to hash find closed nodes
    OpenSet = {start:1}
    cameFrom = {}
    g,f = {},{}
    fp = PriorityQueue.PriorityQueue()

    g[start] = 0
    f[start] = EstimateDistance(graph.GetNode(start),graph.GetNode(target),xSize,ySize,zSize)
    fp.put((EstimateDistance(graph.GetNode(start),graph.GetNode(target),xSize,ySize,zSize),start))      #Sets the start node to the current best node
    Found = False
    while len(OpenSet) != 0:
        current = fp.pop()[1]   #Find best node
        
        if current == target:       #If the node has been found, break
            Found = True
            break
        
        OpenSet.pop(current)        
        ClosedSet[current] = 1
        
        for NodeID in graph.GetNode(current).Get_Friends():     #For each neighbour on the graph
            if NodeID in ClosedSet:         #This node has no better route, ignore
                continue
            
            if NodeID not in OpenSet:       #Add to openset if not yet in it. This only loads the nodes into the g,f,fp sets now in order to reduce memeory usage
                OpenSet[NodeID] = 1
                g[NodeID] = math.inf
                f[NodeID] = math.inf
                fp.put((math.inf,NodeID))

            NewNode = graph.GetNode(NodeID)
            tScore = g[current] + NewNode.Get_Cost()
            if tScore >= g[NodeID]:                 #If does not offer a better path continue
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            fp.remove((f[NodeID],NodeID))       #Remove from priority queue
            fTemp = g[NodeID] + EstimateDistance(NewNode,graph.GetNode(target),xSize,ySize,zSize)       
            f[NodeID] = fTemp
            fp.put((fTemp,NodeID))              #Readd to priority queue

        f.pop(current) #These values will not be refered to again since the current NodeID has been moved to the closed set . This therefore reduces memory usage very slightly
        g.pop(current)


    EndTime = time.time()
    print("[A* Time] "+str((EndTime-StartTime)*1000)+" Milliseconds."+" Total Expanded:"+str(len(cameFrom)))
    if Found:
        return FindPath(cameFrom,current)
    else:
        print("A* Search FAILED. Start:",start,"Target:",target)
        print(FindPath(cameFrom,current))
        return None

def AStar2(graph,start,target):   # Set all g to node_count + 1
    StartTime = time.time()

    xSize,ySize,zSize = graph.Get_Size()
    
    ClosedSet = {}  #Dict to hash find closed nodes
    OpenSet = {start:1}
    cameFrom = {}
    g,f = {},{}


    g[start] = 0
    f[start] = EstimateDistance(graph.GetNode(start),graph.GetNode(target),xSize,ySize,zSize)
    Found = False
    while len(OpenSet) != 0:
        current = min(f,key = lambda n:f[n])  #Faster (143 vs 114 ms) and doesnt require OpenList to be made.Find best node
        
        if current == target:
            Found = True
            break


        OpenSet.pop(current)        
        ClosedSet[current] = 1
        
        for NodeID in graph.GetNode(current).Get_Friends():     #For each neighboyur
            if NodeID in ClosedSet:
                continue
            
            if NodeID not in OpenSet:        #Add to openset if not yet in it. This only loads the nodes into the g,f sets now in order to reduce memeory usage
                OpenSet[NodeID] = 1
                g[NodeID] = math.inf
                f[NodeID] = math.inf

            NewNode = graph.GetNode(NodeID)
            tScore = g[current] + NewNode.Get_Cost()
            if tScore >= g[NodeID]:     #If not a better path contine, otherwise update.
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            f[NodeID] = g[NodeID] + EstimateDistance(NewNode,graph.GetNode(target),xSize,ySize,zSize)

        f.pop(current) #These values will not be refered to again since the current NodeID has been moved to the closed set . This therefore reduces memory usage very slightly
        g.pop(current)


    EndTime = time.time()
    print("[A* Time] "+str((EndTime-StartTime)*1000)+" Milliseconds."+" Total Expanded:"+str(len(cameFrom)))
    if Found:
        return FindPath(cameFrom,current)
    else:
        print("A* Search FAILED. Start:",start,"Target:",target)
        print(FindPath(cameFrom,current))
        return None

        
def FindPath(cameFrom,current):     #Retraces the path from the end node to the start node.
    path = [current]
    while current in cameFrom:
        current = cameFrom[current]
        path.append(current)
    return path[::-1]








##############################################

# Below are random benchmarks used for improvement of the search algorithms


def Benchmark(FLUSH = 100,MAXNODE = 80000):     #Benchmark with test of removing nodes from memory every FLUSH steps
    graph = DynoGraph()
    graph.ImportGraph()

    
    Count = 1
    while True:
        if Count % FLUSH == 0:
            graph.FlushGraph()


        a,b = random.randint(1,MAXNODE),random.randint(1,MAXNODE)
        print("A:",a," B:",b," Delta:",abs(a-b))
        Path = AStar2(graph,a,b)
        print("Path Length",len(Path)," Graph Node length",len(graph.Get_Nodes()))

        print("")
        

        
def MultiBenchmark(num_proc = 4,FLUSH=100,MAXNODE=80000):       #Benchmark but with multiple processes to simulate server
    import multiprocessing
    procs = []
    for x in range(num_proc):
        p = multiprocessing.Process(target = Benchmark,args = (FLUSH,MAXNODE))
        p.start()
        procs.append(p)


def CAStarBenchmark(Random = False):    #Test of the CAStar module. Not part of NEA
    graph = DynoGraph()
    graph.ImportGraph()
    if Random:
        source = random.randint(1,80000)
        target = random.randint(1,80000)
    else:
        source = 1
        target = 160000
    print("ok")
    _ = AStar2(graph,source,target)
    
    print("--- AStar2 ---")
    for x in range(3):
        _ = AStar2(graph,source,target)
    print("--------------")
    print()
    print("--- CAStar2 ---")
    from CAStar import CAStar
    for x in range(3):
        _ = CAStar.AStar2(graph,source,target)
    print("--------------")
    print("")
        










        
        
    
