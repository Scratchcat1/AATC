#Create graph module
import decimal,AATC_AStar,AATC_Coordinate 

def drange(start,end,step):     #Generator function to produce each point for the graph
    step = decimal.Decimal(step)
    r = decimal.Decimal(start)
    while r < end:
        yield float(r)
        r += decimal.Decimal(step)



def CreationDialogue():     #Obtain parameters for graph and generate graph
    print("2 million nodes ~ 357MB")
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
                Coord = AATC_Coordinate.Coordinate(x,y,z)       #Add nodes to graph for each point on the 3D grid
                node = AATC_AStar.Node(nodeID,1,Coord)
                graph.add_node(node)
                nodeID +=1

    xRange = xEnd - xStart
    yRange = yEnd - yStart
    zRange = zEnd - zStart
    graph.Add_Edges(xRange,yRange,zRange)
    graph.Build_Node_Cache()
    graph.SaveGraph()           #Create edges and cache and save graph
    #return graph



if __name__ == "__main__":
    graph = CreationDialogue()    

























