import os,pickle,time,math,hashlib
from AATC_Coordinate import *
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
    def __init__(self,BlockSize = 500,FolderName = "GraphFolder",GraphFileName = "Graph",GraphFileSuffix = ".graph",BlockFileName = "GraphBlock",BlockFileSuffix = ".blk",Node_Cache_BlockSize = 10000000, ABInterval = 36000, ABSlot = 0, ABSlots = 2):
        self.Nodes = {}
        self.BlockSize = BlockSize
        self.cwd = os.getcwd()

        self.GraphFileName = GraphFileName
        self.GraphFileSuffix = GraphFileSuffix
        self.FolderName = FolderName
        self.BlockFileName = BlockFileName
        self.BlockFileSuffix = BlockFileSuffix
        self.Node_Cache_BlockSize = Node_Cache_BlockSize

        self.ABInterval = ABInterval
        self.ABSlot = ABSlot
        self.ABSlots = ABSlots
        
        
    def Size(self,xSize,ySize,zSize):
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize

    def Get_Size(self):
        return self.xSize, self.ySize, self.zSize
    
    def add_node(self,node):
        self.Nodes[node.Get_NodeID()] = node

##    def clean_edges(self):
##        print("Cleaning edges...")
##        for item in self.Nodes.values():
##            for num in item.Friends:
##                friend = self.Nodes[num]
##                if item.Get_NodeID() not in friend.Friends:
##                    friend.add_friend(item.Get_NodeID())

    
    def Add_Edges(self,xRange,yRange,zRange):
        print("Adding edges...")
        self.xCount = int(xRange/self.xSize)
        self.yCount = int(yRange/self.ySize)
        self.zCount = int(zRange/self.zSize)
        
        
        print("xCount:",self.xCount)
        print("yCount:",self.yCount)
        print("zCount:",self.zCount)
        

        for node in self.Nodes.values():
            friends = self.CalculateNeighbours(node.Get_NodeID(),self.xCount,self.yCount,self.zCount)
            for friend in friends:
                node.add_friend(friend)

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
    
    def MapHash(self,value,div):
        return int(value//div)

    def Node_Cache_Hash(self,Key):
        return int(int(hashlib.md5(str(Key).encode('utf8')).hexdigest()[:8],16)//self.Node_Cache_BlockSize) #Generates integer hash of key then int div by BlockSize
        
    ##################################
    
    def Build_Node_Cache(self):
        self.Node_Cache = {}
        for node in self.Nodes.values():
            x = node.Coords.Get_X() + 0.25*self.xSize  #Prevents floating point rounding errors
            y = node.Coords.Get_Y() + 0.25*self.ySize
            z = node.Coords.Get_Z() + 0.25*self.zSize

            mx,my,mz = self.MapHash(x,self.xSize),self.MapHash(y,self.ySize),self.MapHash(z,self.zSize)
            self.Node_Cache[(mx,my,mz)] = node.Get_NodeID()

    def Save_Node_Cache(self):
        print("Preparing to save Node Cache")
        Sets = {}
        for Key in self.Node_Cache:
            r = self.Node_Cache_Hash(Key)  #Gets Hashed key
            if r not in Sets:
                Sets[r] = {}
            Sets[r][Key] = self.Node_Cache[Key]  #Adds the item to the set
            
        print("Saving Node Cache. Sets:",len(Sets))
        for Letter in self.GetFolderNames():
            for Set in Sets:
                filename = os.path.join(self.cwd,self.FolderName,Letter,self.BlockFileName+"NC"+str(Set)+self.BlockFileSuffix)
                data = Sets[Set]
                with open(filename,"wb") as file:
                    pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)


    def Get_Node_Cache(self,x,y,z):
        Key = (x,y,z)
        if Key not in self.Node_Cache:
            NCBlockID = self.Node_Cache_Hash(Key)
            try:
                filename = os.path.join(self.cwd,self.FolderName,self.CurrentFolderName(),self.BlockFileName+"NC"+str(NCBlockID)+self.BlockFileSuffix)
                with open(filename,"rb") as file:
                    block = pickle.load(file)
                self.Node_Cache.update(block)
            
            except Exception as e:
                print(e)

        if Key in self.Node_Cache:
            return self.Node_Cache[Key]
        else:
             #Raises error if cannot get node
            raise ValueError("Node_Cache Key requested is not in the NCBlockID checked. Check BlockSize or regenerate blockfiles.")

            
    def Direct_NodeID(self,x,y,z):
        return self.Get_Node_Cache(x,y,z)

    def All_NodeIDs(self,StartValue = 1, MaxValue = None):
        if MaxValue == None:
            MaxValue = self.xCount*self.yCount*self.zCount + (StartValue-1) #Gets Maximum start value, StartValue gives the starting NodeID. -1 as x*y*z = max, if start at 1 and therefore xyz +1-1 = max value. XYZ as eg x=2,y=10,z=5 you will have 100 blocks ,starting at 1 so 100 is max.
                        
        NodeIDList = []
        for NodeID in range(1,MaxValue+1):
            NodeIDList.append(NodeID)
            
        return NodeIDList

    def Find_NodeID(self,x,y,z):
        mx,my,mz = self.MapHash(x,self.xSize),self.MapHash(y,self.ySize),self.MapHash(z,self.zSize)
        NodeID = self.Get_Node_Cache(mx,my,mz)
        return NodeID

    def Obj_Find_NodeID(self,Obj):
        x,y,z = Obj.Coords.Get_X(),Obj.Coords.Get_Y(),Obj.Coords.Get_Z()
        NodeID = self.Find_NodeID(x,y,z)
        return NodeID

    
    #############################

    def SaveGraph(self,AutoNodeSave = True,AutoNodeCacheSave = True):
        print("Saving graph...")
        for Letter in self.GetFolderNames():
            os.makedirs(os.path.join(os.getcwd(),self.FolderName,Letter),exist_ok = True)
        if AutoNodeSave:
            self.SaveNodes()
        if AutoNodeCacheSave:
            self.Save_Node_Cache()

        self.Nodes = {}
        self.Node_Cache = {}
        for Letter in self.GetFolderNames():
            try:
                filename = os.path.join(self.cwd,self.FolderName,Letter,self.GraphFileName+self.GraphFileSuffix)
                with open(filename,"wb") as file:
                    pickle.dump(self,file,protocol = pickle.HIGHEST_PROTOCOL)
                print("Saved graph sucessfully")
            except Exception as e:
                print("Error occured while saving graph file ",e)

    def ImportGraph(self):
        print("Importing graph")
        ABSlot = self.ABSlot
        try:
            filename = os.path.join(os.getcwd(),self.FolderName,"A",self.GraphFileName+self.GraphFileSuffix)   #MUST ALWAYS HAVE ATLEAST THE FOLDER "A" in order to load the configuration
            with open(filename,"rb") as file:
                ImportFile = pickle.load(file)
                
            self.__dict__.update(ImportFile.__dict__)
            print("Imported graph sucessfully")
        except Exception as e:
            print("An error occured while importing graph data",e)
            
        self.cwd = os.getcwd()
        self.ABSlot = ABSlot
    
    ################
    def Hash(self,Value):
        return int(Value//self.BlockSize)
    def GetNode(self,NodeID):
        if NodeID not in self.Nodes:
            BlockID = self.Hash(NodeID)
            try:
                filename = os.path.join(self.cwd,self.FolderName,self.CurrentFolderName(),self.BlockFileName+"N"+str(BlockID)+self.BlockFileSuffix)
                with open(filename,"rb") as file:
                    block = pickle.load(file)

                self.Nodes.update(block)
                

            except Exception as e:
                print(e)

        if NodeID in self.Nodes:
            return self.Nodes[NodeID]
        else:
             #Raises error if cannot get node
            raise ValueError("NodeID requested is not in the BlockID checked. Check BlockSize or regenerate blockfiles. NodeID: "+str(NodeID))

    def SaveNodes(self):
        Sets = {}
        m = self.Hash(max(self.Nodes))  #Finds max blockID
        for x in range(m+1):
            Sets[x] = {}   #Creates sets for each block

        for node in self.Nodes.values():
            r = self.Hash(node.Get_NodeID())
            Sets[r][node.Get_NodeID()] = node

        for Letter in self.GetFolderNames():
            for Set in Sets: #Set = BlockID
                if len(Sets[Set]) != 0:  #If set is not empty. Empty sets may cause issues with delta Node change saving.
                    filename = os.path.join(self.cwd,self.FolderName,Letter,self.BlockFileName+"N"+str(Set)+self.BlockFileSuffix)
                    data = Sets[Set]
                    with open(filename,"wb") as file:
                        pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)

    def EvictNode(self,NodeID):  #Removes a node from the Nodes dict
        if NodeID in self.Nodes:
            self.Nodes.pop(NodeID)
            return True
        else:
            return False

    #######################################

    def GetFolderNames(self):
        names = []
        for x in range(self.ABSlots):
            names.append(chr(65+x))
        return names

    def CurrentFolderName(self):
        char = chr(  int(65+ ((time.time()+self.ABInterval*self.ABSlot)//self.ABInterval)%self.ABSlots))
        return char
    
        
            

class Node:
    def __init__(self,NodeID,Cost,Coords):
        self.NodeID = NodeID
        self.Friends = []
        self.Cost = Cost
        self.Coords = Coords
    def add_friend(self,friend):
        if friend not in self.Friends:
            self.Friends.append(friend)

    def Get_NodeID(self):
        return self.NodeID
    def Get_Friends(self):
        return self.Friends
    def Get_Coords(self):
        return self.Coords
    def Get_Cost(self):
        return self.Cost

    def Set_Cost(self,cost):
        self.Cost = cost

def EstimateDistance(Node,Target,xSize,ySize,zSize):
    Node_Coords = Node.Get_Coords()
    Target_Coords = Target.Get_Coords()
    return (abs(Node_Coords.Get_X()-Target_Coords.Get_X())/xSize+abs(Node_Coords.Get_Y()-Target_Coords.Get_Y())/ySize+abs(Node_Coords.Get_Z()-Target_Coords.Get_Z())/zSize)
    #return math.sqrt((Node_Coords.Get_X()-Target_Coords.Get_X()/xSize)**2+(Node_Coords.Get_Y()-Target_Coords.Get_Y()/ySize)**2 + (Node_Coords.Get_Z()-Target_Coords.Get_Z()/zSize)**2)*0.9

def AStarPQ(graph,start,target):   # Set all g to node_count + 1
    StartTime = time.time()

    xSize,ySize,zSize = graph.Get_Size()
    
    ClosedSet = {}  #Dict to hash find closed nodes
    OpenSet = {start:1}
    cameFrom = {}
    g,f = {},{}
    fp = PriorityQueue.PriorityQueue()

    g[start] = 0
    f[start] = EstimateDistance(graph.GetNode(start),graph.GetNode(target),xSize,ySize,zSize)
    fp.put((EstimateDistance(graph.GetNode(start),graph.GetNode(target),xSize,ySize,zSize),start))
    Found = False
    while len(OpenSet) != 0:
        current = fp.pop()[1]
        
        if current == target:
            Found = True
            break
        
        OpenSet.pop(current)
        ClosedSet[current] = 1
        
        for NodeID in graph.GetNode(current).Get_Friends():
            if NodeID in ClosedSet:
                continue
            
            if NodeID not in OpenSet:
                OpenSet[NodeID] = 1
                g[NodeID] = math.inf
                f[NodeID] = math.inf
                fp.put((math.inf,NodeID))

            NewNode = graph.GetNode(NodeID)
            tScore = g[current] + NewNode.Get_Cost()
            if tScore >= g[NodeID]:
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            fp.remove((f[NodeID],NodeID))
            fTemp = g[NodeID] + EstimateDistance(NewNode,graph.GetNode(target),xSize,ySize,zSize)
            f[NodeID] = fTemp
            fp.put((fTemp,NodeID))

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
        current = min(f,key = lambda n:f[n])  #Faster (143 vs 114 ms) and doesnt require OpenList to be made
        
        if current == target:
            Found = True
            break


        OpenSet.pop(current)
        ClosedSet[current] = 1
        
        for NodeID in graph.GetNode(current).Get_Friends():
            if NodeID in ClosedSet:
                continue
            
            if NodeID not in OpenSet:
                OpenSet[NodeID] = 1
                g[NodeID] = math.inf
                f[NodeID] = math.inf

            NewNode = graph.GetNode(NodeID)
            tScore = g[current] + NewNode.Get_Cost()
            if tScore >= g[NodeID]:
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

        
def FindPath(cameFrom,current):
    path = [current]
    while current in cameFrom:
        current = cameFrom[current]
        path.append(current)
    return path[::-1]


def Benchmark(FLUSH = 100,BlockSize = 500,MAXNODE = 80000):
    import random,sys
    graph = DynoGraph(BlockSize= BlockSize)
    graph.ImportGraph()

    
    Count = 1
    while True:
        if Count % FLUSH == 0:
            graph.Nodes = {}


        a,b = random.randint(1,MAXNODE),random.randint(1,MAXNODE)
        print("A:",a," B:",b," Delta:",abs(a-b))
        Path = AStar2(graph,a,b)
        print("Path Length",len(Path)," Graph Node length",len(graph.Nodes))

        print("")
        

        



def CAStarBenchmark(Random = False):
    graph = DynoGraph()
    graph.ImportGraph()
    if Random:
        import random
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
        










        
        
    
