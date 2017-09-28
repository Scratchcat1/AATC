class PriorityQueue:
    def __init__(self):
        self.Queue = []

    def put(self,item):
##        print(self.Queue,  "<--" , item)
        found,index = BinarySearch(self.Queue,item)
        if self.Queue != [] and self.Queue[index] < item:
            index +=1
        self.Queue.insert(index,item)
##        print(self.Queue,index)

    def pop(self):
        return self.Queue.pop(0)

    def remove(self,item):
        found,index = BinarySearch(self.Queue,item)
        if found:
            self.Queue.pop(index)
        else:
            raise ValueError("Item not in priority queue")


def BinarySearch(SearchList,item):
    found = False
    start = 0
    end = len(SearchList)-1
    mid = (start+end)//2
    while not found and start <= end:
        mid = (start+end)//2
        current = SearchList[mid]
        if current < item:
            start = mid +1
        elif current > item:
            end = mid - 1
        else:
            found = True
##        if current  == item:
##            found = True
##        elif current < item:
##            start = mid + 1
##        else:
##            end = mid - 1

    return found,mid
        