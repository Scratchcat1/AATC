#!python
#cython: boundscheck=False, wraparound=False, infer_types=True,cdivision = True

from libcpp.unordered_map cimport unordered_map

import os,pickle,heapq,time,math,hashlib
from AATC_Coordinate import *
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



def AStar2(graph, int start, int target):   # Set all g to node_count + 1
    StartTime = time.time()

    cdef unordered_map[int, int] ClosedSet,OpenSet
    cdef unordered_map[int, float] g,f
    cdef float xSize,ySize,zSize,gNode
    cdef dict cameFrom
    cdef int NodeID,current,tScore,xCount,yCount,zCount
    cdef list FriendList


    TargetNode = graph.GetNode(target)
    xSize,ySize,zSize = graph.xSize,graph.ySize,graph.zSize
    xCount,yCount,zCount = graph.xCount,graph.yCount,graph.zCount
    
    #ClosedSet = {}  #Dict to hash find closed nodes
    OpenSet[start] = 1
    cameFrom = {}
    
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

        
        OpenSet.erase(current)
        ClosedSet[current] = 1

        FriendList = graph.GetNode(current).Friends
        for NodeID in FriendList:
            if ClosedSet.count(NodeID) != 0:
                continue
            if OpenSet.count(NodeID) == 0 :
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

        f.erase(current) #These values will not be refered to again since the current NodeID has been moved to the closed set . This therefore reduces memory usage very slightly
        g.erase(current)
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
