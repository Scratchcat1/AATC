#Create graph module
import pickle,decimal,os
class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize


class DynoGraph:
    def __init__(self,BlockSize):
        self.Nodes = {}
        self.BlockSize = BlockSize
        self.cwd = os.getcwd()
        self.Prefix = os.path.join("BlockFolder","GraphNodes")
        self.Suffix = ".blk"
        
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

    def MapHash(self,value,div):
        return int(value//div)
                
    def Build_Node_Cache(self):
        self.Node_Cache = {}
        for node in self.Nodes.values():
            x = node.Coords.x + 0.25*self.xSize
            y = node.Coords.y + 0.25*self.ySize
            z = node.Coords.z + 0.25*self.zSize

            mx,my,mz = self.MapHash(x,self.xSize),self.MapHash(y,self.ySize),self.MapHash(z,self.zSize)
            self.Node_Cache[(mx,my,mz)] = node.NodeID

    def Find_NodeID(self,x,y,z):
        mx,my,mz = self.MapHash(x,self.xSize),self.MapHash(y,self.ySize),self.MapHash(z,self.zSize)
        NodeID = self.Node_Cache[(mx,my,mz)]
        return NodeID

    def Obj_Find_NodeID(self,Obj):
        x,y,z = Obj.Coords.x,Obj.Coords.y,Obj.Coords.z
        NodeID = self.Find_NodeID(x,y,z)
        return NodeID

    ################
    def Hash(self,Value):
        return int(Value//self.BlockSize)
    def GetNode(self,NodeID):
        if NodeID not in self.Nodes:
            print("Chek")
            BlockID = self.Hash(NodeID)
            try:
                filename = os.path.join(self.cwd,self.Prefix+str(BlockID)+self.Suffix)
                file = open(filename,"rb")
                block = pickle.load(file)
                file.close()
                self.Nodes.update(block)
                
                if NodeID in self.Nodes:
                    return self.Nodes[NodeID]
            except:
                pass
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
            filename = os.path.join(self.cwd,self.Prefix+str(Set)+self.Suffix)
            file = open(filename,"wb")
            data = Sets[Set]
            pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)
            file.close()
        
            

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
graph = DynoGraph(50)
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

























