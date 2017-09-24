#!python
#cython: boundscheck=False, wraparound=False, infer_types=True,cdivision = True


import os,pickle,heapq,time,math,hashlib
from AATC_Coordinate import *
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
    def __init__(self,BlockSize = 500,FolderName = "GraphFolder",GraphFileName = "Graph",GraphFileSuffix = ".graph",BlockFileName = "GraphBlock",BlockFileSuffix = ".blk",Node_Cache_BlockSize = 10000000):
        self.Nodes = {}
        self.BlockSize = BlockSize
        self.cwd = os.getcwd()

        self.GraphFileName = GraphFileName
        self.GraphFileSuffix = GraphFileSuffix
        self.FolderName = FolderName
        self.BlockFileName = BlockFileName
        self.BlockFileSuffix = BlockFileSuffix
        self.Node_Cache_BlockSize = Node_Cache_BlockSize
        
        
    def Size(self,xSize,ySize,zSize):
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize

    def Get_Size(self):
        return self.xSize, self.ySize, self.zSize
    
    def add_node(self,node):
        self.Nodes[node.Get_NodeID()] = node

    def clean_edges(self):
        print("Cleaning edges...")
        for item in self.Nodes.values():
            for num in item.Friends:
                friend = self.Nodes[num]
                if item.Get_NodeID() not in friend.Friends:
                    friend.add_friend(item.Get_NodeID())

    
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
        for Set in Sets:
            filename = os.path.join(self.cwd,self.FolderName,self.BlockFileName+"NC"+str(Set)+self.BlockFileSuffix)
            file = open(filename,"wb")
            data = Sets[Set]
            pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)
            file.close()

    def Get_Node_Cache(self,x,y,z):
        Key = (x,y,z)
        if Key not in self.Node_Cache:
            NCBlockID = self.Node_Cache_Hash(Key)
            try:
                filename = os.path.join(self.cwd,self.FolderName,self.BlockFileName+"NC"+str(NCBlockID)+self.BlockFileSuffix)
                file = open(filename,"rb")
                block = pickle.load(file)
                file.close()
                self.Node_Cache.update(block)
            
            except Exception as e:
                print(e)

        if Key in self.Node_Cache:
            return self.Node_Cache[Key]
        else:
             #Raises error if cannot get node
            raise ValueError("Node_Cache Key requested is not in the NCBlockID checked. Check BlockSize or regenerate blockfiles")

            
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
        x,y,z = Obj.Coords.x,Obj.Coords.y,Obj.Coords.z
        NodeID = self.Find_NodeID(x,y,z)
        return NodeID

    
    #############################

    def SaveGraph(self,AutoNodeSave = True,AutoNodeCacheSave = True):
        print("Saving graph...")
        if AutoNodeSave:
            self.SaveNodes()
        if AutoNodeCacheSave:
            self.Save_Node_Cache()

        self.Nodes = {}
        self.Node_Cache = {}
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
            filename = os.path.join(os.getcwd(),self.FolderName,self.GraphFileName+self.GraphFileSuffix)
            file = open(filename,"rb")
            ImportFile = pickle.load(file)
            file.close()
            self.__dict__.update(ImportFile.__dict__)
            print("Imported graph sucessfully")
        except Exception as e:
            print("An error occured while importing graph data",e)
        self.cwd = os.getcwd()
    
    ################
    def Hash(self,Value):
        return int(Value//self.BlockSize)
    def GetNode(self,NodeID):
        if NodeID not in self.Nodes:
            BlockID = self.Hash(NodeID)
            try:
                filename = os.path.join(self.cwd,self.FolderName,self.BlockFileName+"N"+str(BlockID)+self.BlockFileSuffix)
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
            r = self.Hash(node.Get_NodeID())
            Sets[r][node.Get_NodeID()] = node


        for Set in Sets: #Set = BlockID
            filename = os.path.join(self.cwd,self.FolderName,self.BlockFileName+"N"+str(Set)+self.BlockFileSuffix)
            file = open(filename,"wb")
            data = Sets[Set]
            pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)
            file.close()

    def EvictNode(self,NodeID):  #Removes a node from the Nodes dict
        if NodeID in self.Nodes:
            self.Nodes.pop(NodeID)
            return True
        else:
            return False
        
            

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

##cdef int EstimateDistance(Node,Target, float xSize, float ySize, float zSize):
##    return int(abs(Node.Coords.x-Target.Coords.x)/xSize+abs(Node.Coords.y-Target.Coords.y)/ySize+abs(Node.Coords.z-Target.Coords.z)/zSize)

cdef float EstimateDistance(int NodeID, int TargetID, int xCount,int yCount,int zCount, float xSize, float ySize, float zSize):
    cdef float x,y,z,Nx,Ny,Nz,Tx,Ty,Tz
    cdef float Distance
    Nx,Ny,Nz = GetxCoord(NodeID,xCount,yCount,zCount,xSize,ySize,zSize),GetyCoord(NodeID,xCount,yCount,zCount,xSize,ySize,zSize),GetzCoord(NodeID,xCount,yCount,zCount,xSize,ySize,zSize)
    Tx,Ty,Tz = GetxCoord(TargetID,xCount,yCount,zCount,xSize,ySize,zSize),GetyCoord(TargetID,xCount,yCount,zCount,xSize,ySize,zSize),GetzCoord(TargetID,xCount,yCount,zCount,xSize,ySize,zSize)
    x=(Nx-Tx)/xSize
    y=(Ny-Ty)/ySize
    z=(Nz-Tz)/zSize
    if x < 0:
        x = x*-1
    if y < 0:
        y = y*-1
    if z < 0:
        z = z*-1
    Distance = x+y+z
    return Distance



def AStar2(graph, int start, int target):   # Set all g to node_count + 1
    StartTime = time.time()

    cdef float xSize,ySize,zSize,gNode
    cdef dict ClosedSet,OpenSet,cameFrom,g,f
    cdef int NodeID,current,tScore,xCount,yCount,zCount
    cdef list FriendList


    TargetNode = graph.GetNode(target)
    xSize,ySize,zSize = graph.xSize,graph.ySize,graph.zSize
    xCount,yCount,zCount = graph.xCount,graph.yCount,graph.zCount
    
    ClosedSet = {}  #Dict to hash find closed nodes
    OpenSet = {start:1}
    cameFrom = {}
    g,f = {},{}
    current = -1


    g[start] = 0
    f[start] = EstimateDistance(start,target,xCount,yCount,zCount,xSize,ySize,zSize)
    Found = False
    while len(OpenSet) != 0:
##        OpenList = []
##        for x in OpenSet:
##            OpenList.append((f[x],x))  # f score and ID
##            
##        heapq.heapify(OpenList)
##        current = OpenList.pop(0)[1]  # Gets ID with lowest f

        current = min(f, key = lambda n:f[n])  #Faster (106 vs 62 ms) and doesnt require OpenList to be made

        
        if current == target:
            #print("Found Target")
            Found = True
            break

        
        OpenSet.pop(current)
        ClosedSet[current] = 1

        FriendList = graph.GetNode(current).Friends
        for NodeID in FriendList:
            if NodeID in ClosedSet:
                continue
            if NodeID not in OpenSet:
                OpenSet[NodeID] = 1
                g[NodeID] = math.inf
                f[NodeID] = math.inf

            Node = graph.GetNode(NodeID)
            tScore = g[current]+ Node.Cost
            if tScore >= g[NodeID]:
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            f[NodeID] = g[NodeID] + EstimateDistance(NodeID,target,xCount,yCount,zCount,xSize,ySize,zSize)
    EndTime = time.time()
    print("[A* Time] "+str((EndTime-StartTime)*1000)+" Milliseconds."+" Total Expanded:"+str(len(cameFrom)))
    if Found:
        return FindPath(cameFrom,current)
    else:
        print("A* Search FAILED. Start:",start,"Target:",target)
        print(FindPath(cameFrom,current))
        return None

        
cdef FindPath(dict cameFrom, int current):
    cdef list path
    path = [current]
    while current in cameFrom:
        current = cameFrom[current]
        path.append(current)
    return path


def Benchmark(FLUSH = 100,BlockSize = 500,MAXNODE = 2000000):
    import random,sys
    graph = DynoGraph(BlockSize= 500)
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
        

        


cdef float GetxCoord(int ID, int xCount, int yCount, int zCount, float xSize, float ySize,float zSize):
    cdef float xCoord
    xCoord = ((ID-1)//(zCount*yCount)) * xSize
    return xCoord
    
cdef float GetyCoord(int ID, int xCount, int yCount, int zCount, float xSize, float ySize,float zSize):
    cdef float yCoord
    yCoord = (((ID-1)%(zCount*yCount))//zCount)*ySize
    return yCoord

cdef float GetzCoord(int ID, int xCount, int yCount, int zCount, float xSize, float ySize,float zSize):
    cdef float zCoord
    zCoord = ((ID-1)%zCount)*zSize
    return zCoord









    
    

