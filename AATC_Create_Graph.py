#Create graph module
import pickle,decimal
class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize
        
class Graph:
    def __init__(self):
        self.Nodes = {}

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
            zlow,zhigh,ylow,yhigh,xlow,xhigh = False,False,False,False,False,False
            friends = []
            if (node.NodeID - 1) % zCount != 0:  # If not on bottom level of z
                zlow = True
            if node.NodeID % zCount != 0:   # if not on top level of z
                zhigh = True

            if ((node.NodeID-1) % (zCount*yCount)) >= zCount:   #Not on low y row
                ylow = True
            if ((node.NodeID-1)% (zCount*yCount))//zCount != yCount-1:  # Not on high y row
                yhigh = True

            if (node.NodeID-1) // (zCount*yCount) != 0:  # not on low x set
                xlow = True
            if (node.NodeID-1) // (zCount*yCount) != (xCount-1):
                xhigh = True

            if zlow:
                friends.append(node.NodeID-1)
                if ylow:
                    friends.append((node.NodeID-1)-zCount)
                    if xlow:
                        friends.append((node.NodeID-1)-zCount-(zCount*yCount))
                    if xhigh:
                        friends.append((node.NodeID-1)-zCount+(zCount*yCount))
                if yhigh:
                    friends.append((node.NodeID-1)+zCount)
                    if xlow:
                        friends.append((node.NodeID-1)+zCount-(zCount*yCount))
                    if xhigh:
                        friends.append((node.NodeID-1)+zCount+(zCount*yCount))
            if zhigh:
                friends.append(node.NodeID+1)
                if ylow:
                    friends.append((node.NodeID+1)-zCount)
                    if xlow:
                        friends.append((node.NodeID+1)-zCount-(zCount*yCount))
                    if xhigh:
                        friends.append((node.NodeID+1)-zCount+(zCount*yCount))
                if yhigh:
                    friends.append((node.NodeID+1)+zCount)
                    if xlow:
                        friends.append((node.NodeID+1)+zCount-(zCount*yCount))
                    if xhigh:
                        friends.append((node.NodeID+1)+zCount+(zCount*yCount))
                
            if ylow:
                friends.append(node.NodeID-zCount)
                if xlow:
                    friends.append(node.NodeID-zCount-(zCount*yCount))
                if xhigh:
                    friends.append(node.NodeID-zCount+(zCount*yCount))
            if yhigh:
                friends.append(node.NodeID+zCount)
                if xlow:
                    friends.append(node.NodeID+zCount-(zCount*yCount))
                if xhigh:
                    friends.append(node.NodeID+zCount+(zCount*yCount))


            if zlow:
                if xlow:
                    friends.append((node.NodeID-1)-(zCount*yCount))
                if xhigh:
                    friends.append((node.NodeID-1)+(zCount*yCount))

            if zhigh:
                if xlow:
                    friends.append((node.NodeID+1)-(zCount*yCount))
                if xhigh:
                    friends.append((node.NodeID+1)+(zCount*yCount))

            if xlow:
                friends.append(node.NodeID-(zCount*yCount))
            if xhigh:
                friends.append(node.NodeID+(zCount*yCount))

                
            for friend in friends:
                node.add_friend(friend)
            
##        for node1 in self.Nodes.values():
##            for node2 in self.Nodes.values():
##                Friend = False
##                if node2.Coords.x > node1.Coords.x - self.xSize and node2.Coords.x < node1.Coords.x + self.xSize and \
##                   node2.Coords.y > node1.Coords.y - self.ySize and node2.Coords.y < node1.Coords.y + self.ySize and \
##                   node2.Coords.z > node1.Coords.z - self.zSize and node2.Coords.z < node1.Coords.z + self.zSize:    # If node 2 is in a cuboid of x,y,z, size around node 1
##                    Friend = True
##                if Friend:
##                    node1.add_friend(node2.NodeID)
##                    node2.add_friend(node1.NodeID)

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

def drange(start,end,step):
  step = decimal.Decimal(step)
  r = decimal.Decimal(start)
  while r < end:
    yield float(r)
    r += decimal.Decimal(step)

xStart =float(input("Enter start x Coord"))
yStart = float(input("Enter start y Coord"))
zStart = float(input("Enter start z Coord"))

xEnd = float(input("Enter End x Coord"))
yEnd = float(input("Enter End y Coord"))
zEnd = float(input("Enter End z Coord"))

xInterval = float(input("Enter x interval"))
yInterval = float(input("Enter y interval"))
zInterval = float(input("Enter z interval"))

print("creating graph")
graph = Graph()
graph.Size(xInterval,yInterval,zInterval)
nodeID = 1
for x in drange(xStart,xEnd,xInterval):
    for y in drange(yStart,yEnd,yInterval):
        for z in drange(zStart,zEnd,zInterval):
            Coord = Coordinate(x,y,z)
            node = Node(nodeID,1,Coord)
            graph.add_node(node)
            nodeID +=1

xRange = xEnd - xStart
yRange = yEnd - yStart
zRange = zEnd - zStart

graph.Add_Edges(xRange,yRange,zRange)
graph.clean_edges()
    























