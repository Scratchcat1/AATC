import os,pickle,heapq,time,math

class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize
        
class DynoGraph:
    def __init__(self,BlockSize = 500,FolderName = "GraphFolder",GraphFileName = "Graph",GraphFileSuffix = ".graph",BlockFileName = "GraphNodes",BlockFileSuffix = ".blk"):
        self.Nodes = {}
        self.BlockSize = BlockSize
        self.cwd = os.getcwd()

        self.GraphFileName = GraphFileName
        self.GraphFileSuffix = GraphFileSuffix
        self.FolderName = FolderName
        self.BlockFileName = BlockFileName
        self.BlockFileSuffix = BlockFileSuffix
        
        
    def Size(self,xSize,ySize,zSize):
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize
    def add_node(self,node):
        self.Nodes[node.NodeID] = node

    def clean_edges(self):
        print("Cleaning edges...")
        for item in self.Nodes.values():
            for num in item.Friends:
                friend = self.Nodes[num]
                if item.NodeID not in friend.Friends:
                    friend.add_friend(item.NodeID)

    
    def Add_Edges(self,xRange,yRange,zRange):
        print("Adding edges...")
        xCount = int(xRange/self.xSize)
        yCount = int(yRange/self.ySize)
        zCount = int(zRange/self.zSize)

        print("xCount:",xCount)
        print("yCount:",yCount)
        print("zCount:",zCount)
        

        for node in self.Nodes.values():
            friends = self.CalculateNeighbours(node.NodeID,xCount,yCount,zCount)
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

    def MapHash(self,value,div):
        return int(value//div)
                
    def Build_Node_Cache(self):
        self.Node_Cache = {}
        for node in self.Nodes.values():
            x = node.Coords.x + 0.25*self.xSize  #Prevents floating point rounding errors
            y = node.Coords.y + 0.25*self.ySize
            z = node.Coords.z + 0.25*self.zSize

            mx,my,mz = self.MapHash(x,self.xSize),self.MapHash(y,self.ySize),self.MapHash(z,self.zSize)
            self.Node_Cache[(mx,my,mz)] = node.NodeID

    def Direct_NodeID(self,x,y,z):
        return self.Node_Cache[(x,y,z)]

    def All_NodeIDs(self):
        return self.Node_Cache.values()

    def Find_NodeID(self,x,y,z):
        mx,my,mz = self.MapHash(x,self.xSize),self.MapHash(y,self.ySize),self.MapHash(z,self.zSize)
        NodeID = self.Node_Cache[(mx,my,mz)]
        return NodeID

    def Obj_Find_NodeID(self,Obj):
        x,y,z = Obj.Coords.x,Obj.Coords.y,Obj.Coords.z
        NodeID = self.Find_NodeID(x,y,z)
        return NodeID

    #############################

    def SaveGraph(self,AutoNodeSave = True):
        print("Saving graph...")
        if AutoNodeSave:
            self.SaveNodes()

        self.Nodes = {}
        try:
            filename = os.path.join(self.cwd,self.FolderName,self.GraphFileName+self.GraphFileSuffix)
            file = open(filename,"wb")
            pickle.dump(self,file,protocol = pickle.HIGHEST_PROTOCOL)
            file.close()
            print("Saved graph sucessfully")
        except Exception as e:
            print("Error occured while saving graph file ",e)

    def ImportGraph(self):
        print("Importing graph")
        try:
            filename = os.path.join(self.cwd,self.FolderName,self.GraphFileName+self.GraphFileSuffix)
            file = open(filename,"rb")
            ImportFile = pickle.load(file)
            file.close()
            self.__dict__.update(ImportFile.__dict__)
            print("Imported graph sucessfully")
        except Exception as e:
            print("An error occured while importing graph data",e)
    
    ################
    def Hash(self,Value):
        return int(Value//self.BlockSize)
    def GetNode(self,NodeID):
        if NodeID not in self.Nodes:
            BlockID = self.Hash(NodeID)
            try:
                filename = os.path.join(self.cwd,self.FolderName,self.BlockFileName+str(BlockID)+self.BlockFileSuffix)
                file = open(filename,"rb")
                block = pickle.load(file)
                file.close()
                self.Nodes.update(block)
                

            except Exception as e:
                print(e)

        if NodeID in self.Nodes:
            return self.Nodes[NodeID]
        else:
             #Raises error if cannot get node
            raise ValueError("NodeID requested is not in the BlockID checked. Check BlockSize or regenerate blockfiles")

    def SaveNodes(self):
        Sets = {}
        m = self.Hash(max(self.Nodes))  #Finds max blockID
        for x in range(m+1):
            Sets[x] = {}   #Creates sets for each block

        for node in self.Nodes.values():
            r = self.Hash(node.NodeID)
            Sets[r][node.NodeID] = node


        for Set in Sets: #Set = BlockID
            filename = os.path.join(self.cwd,self.FolderName,self.BlockFileName+str(Set)+self.BlockFileSuffix)
            file = open(filename,"wb")
            data = Sets[Set]
            pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)
            file.close()

    def EvictNode(self,NodeID):  #Removes a node from the Nodes dict
        if NodeID in self.Nodes:
            self.Nodes.pop(NodeID)
            

class Node:
    def __init__(self,NodeID,Cost,Coords):
        self.NodeID = NodeID
        self.Friends = []
        self.Cost = Cost
        self.Coords = Coords
    def add_friend(self,friend):
        if friend not in self.Friends:
            self.Friends.append(friend)
    def Get_Coords(self):
        return self.Coords
    def Get_Cost(self):
        return self.Cost

def EstimateDistance(Node,Target,xSize,ySize,zSize):
    return abs(Node.Coords.x-Target.Coords.x)/xSize+abs(Node.Coords.y-Target.Coords.y)/ySize+abs(Node.Coords.z-Target.Coords.z)/zSize
def AStar(graph,start,target,xSize=1,ySize=1,zSize = 1):   # Set all g to node_count + 1
    StartTime = time.time()
    ClosedSet = {}  #Dict to hash find closed nodes
    OpenSet = {start:1}
    cameFrom = {}
    g,f = {},{}

    for NodeID in graph.Nodes:
        g[NodeID] = NodeCount +1
        f[NodeID] = NodeCount +1

    g[start] = 0
    f[start] = EstimateDistance(graph.Nodes[start],graph.Nodes[target],xSize,ySize,zSize)
    Found = False
    while len(OpenSet) != 0:
        OpenList = []
        for x in OpenSet:
            OpenList.append((f[x],x))  # f score and ID
            
        heapq.heapify(OpenList)
        current = OpenList.pop(0)[1]  # Gets ID with lowest f
        
        if current == target:
            #print("Found Target")
            Found = True
            break

        
        OpenSet.pop(current)
        ClosedSet[current] = 1
        for NodeID in graph.Nodes[current].Friends:
            if ClosedSet.get(NodeID) != None:
                continue
            if OpenSet.get(NodeID) == None:
                OpenSet[NodeID] = 1

            tScore = g[current]+ 1
            if tScore >= g[NodeID]:
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            f[NodeID] = g[NodeID] + EstimateDistance(graph.Nodes[NodeID],graph.Nodes[target],xSize,ySize,zSize)
    EndTime = time.time()
    print("[A* Time] "+str((EndTime-StartTime)*1000)+" Milliseconds")
    if Found:
        return FindPath(cameFrom,current)
    else:
        print("A* Search FAILED. Start:",start,"Target:",target)
        print(FindPath(cameFrom,current))

def AStar2(graph,start,target,xSize=1,ySize=1,zSize = 1):   # Set all g to node_count + 1
    StartTime = time.time()

    xSize,ySize,zSize = graph.xSize,graph.ySize,graph.zSize
    
    ClosedSet = {}  #Dict to hash find closed nodes
    OpenSet = {start:1}
    cameFrom = {}
    g,f = {},{}

    for NodeID in graph.Nodes:
        g[NodeID] = math.inf
        f[NodeID] = math.inf

    g[start] = 0
    f[start] = EstimateDistance(graph.GetNode(start),graph.GetNode(target),xSize,ySize,zSize)
    Found = False
    while len(OpenSet) != 0:
        OpenList = []
        for x in OpenSet:
            OpenList.append((f[x],x))  # f score and ID
            
        heapq.heapify(OpenList)
        current = OpenList.pop(0)[1]  # Gets ID with lowest f
        
        if current == target:
            #print("Found Target")
            Found = True
            break

        
        OpenSet.pop(current)
        ClosedSet[current] = 1
        for NodeID in graph.GetNode(current).Friends:
            if ClosedSet.get(NodeID) != None:
                continue
            if OpenSet.get(NodeID) == None:
                OpenSet[NodeID] = 1

            if NodeID not in g:  #if not in g it is not yet in f also
                g[NodeID] = math.inf
                f[NodeID] = math.inf

            tScore = g[current]+ graph.GetNode(NodeID).Cost
            if tScore >= g[NodeID]:
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            f[NodeID] = g[NodeID] + EstimateDistance(graph.GetNode(NodeID),graph.GetNode(target),xSize,ySize,zSize)
    EndTime = time.time()
    print("[A* Time] "+str((EndTime-StartTime)*1000)+" Milliseconds")
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
    print(str(path)+"\n"+str(len(cameFrom)))
    return path