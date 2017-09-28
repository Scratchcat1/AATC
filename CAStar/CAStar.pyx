#!python
#cython: boundscheck=False, wraparound=False, infer_types=True,cdivision = True


import os,pickle,heapq,time,math,hashlib
from AATC_Coordinate import *
try:
    try:
        import PriorityQueue.PriorityQueueC as PriorityQueue
    except:
        print("PriotityQueueC not available, defaulting to pure python")
        import PriorityQueue.PriorityQueue
except:
    print("AStarPQ not available")
    
try:
    _ = math.inf
except:
    print("You do not have math.inf object, Python 3.5 onwards. Will use replacement.")
    math.inf = 10**20
    
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

def AStarPQ(graph, int start, int target):   # Set all g to node_count + 1
    StartTime = time.time()

    cdef float xSize,ySize,zSize,gNode,fTemp
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
    fp = PriorityQueue.PriorityQueue()


    g[start] = 0
    f[start] = EstimateDistance(start,target,xCount,yCount,zCount,xSize,ySize,zSize)
    fp.put((EstimateDistance(start,target,xCount,yCount,zCount,xSize,ySize,zSize),start))
    Found = False
    while len(OpenSet) != 0:
        current = fp.pop()[1]
        if current == target:
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
                fp.put((math.inf,NodeID))

            Node = graph.GetNode(NodeID)
            tScore = g[current]+ Node.Get_Cost()
            if tScore >= g[NodeID]:
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            fp.remove((f[NodeID],NodeID))
            fTemp = g[NodeID] + EstimateDistance(NodeID,target,xCount,yCount,zCount,xSize,ySize,zSize)
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
        current = min(f, key = lambda n:f[n])  #Faster (106 vs 62 ms) and doesnt require OpenList to be made
        if current == target:
            Found = True
            break

        OpenSet.pop(current)
        ClosedSet[current] = 1

        FriendList = graph.GetNode(current).Get_Friends()
        for NodeID in FriendList:
            if NodeID in ClosedSet:
                continue
            if NodeID not in OpenSet:
                OpenSet[NodeID] = 1
                g[NodeID] = math.inf
                f[NodeID] = math.inf

            Node = graph.GetNode(NodeID)
            tScore = g[current]+ Node.Get_Cost()
            if tScore >= g[NodeID]:
                continue
            cameFrom[NodeID] = current
            g[NodeID] = tScore
            f[NodeID] = g[NodeID] + EstimateDistance(NodeID,target,xCount,yCount,zCount,xSize,ySize,zSize)
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

        
cdef FindPath(dict cameFrom, int current):
    cdef list path
    path = [current]
    while current in cameFrom:
        current = cameFrom[current]
        path.append(current)
    return path


        

        



##cdef class CSet:
##    cdef int[:,:] Set
##    cdef int MaxSize
##    cdef int CurrentSize
##
##    def __init__(self, int Size = 4):
##        self.Size = Size
##
##    cdef Add(self, int Value):
##        if self.CurrentSize +1 >= self.MaxSize:
##            self.Resize()
##
##        BucketID = Value % self.MaxSize
##        self.Set[BucketID].append(Value)
##
##    
##
##
##    cdef Resize(self):
##        cdef int[:] Items
##        cdef int[:] OneDim
##        cdef int Counter = 0
##        cdef int item
##
##        self.Items[0][0] = 1
##
##        for OneDim in self.Set:
##            for item in OneDim:
##                Items[Counter] = item
##                Counter +=1
##
##        self.MaxSize = self.MaxSize *2
##        self.CurrentSize = 0
##
##        for item in Items:
##            self.Add(item)
##        
##        
##
##
##
##
##    
##    
##

