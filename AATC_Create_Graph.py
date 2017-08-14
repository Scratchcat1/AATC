#Create graph module
import decimal,AATC_AStar

class Coordinate:
    def __init__(self,x,y,z=0,xSize=0,ySize=0,zSize=0):
        self.x = x
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize


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
graph = AATC_AStar.DynoGraph()
graph.Size(xInterval,yInterval,zInterval)
nodeID = 1
for x in drange(xStart,xEnd,xInterval):
    for y in drange(yStart,yEnd,yInterval):
        for z in drange(zStart,zEnd,zInterval):
            Coord = Coordinate(x,y,z)
            node = AATC_AStar.Node(nodeID,1,Coord)
            graph.add_node(node)
            nodeID +=1

xRange = xEnd - xStart
yRange = yEnd - yStart
zRange = zEnd - zStart

graph.Add_Edges(xRange,yRange,zRange)
graph.clean_edges()
graph.Build_Node_Cache()
graph.SaveGraph()
























