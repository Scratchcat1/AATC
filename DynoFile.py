import pickle,os
class DynoFile:
    def __init__(self,SaveDirectory,Prefix,Suffix,BlockSize):
        self.cwd = SaveDirectory  # eg /home/pi/maps
        self.Prefix = Prefix      # eg GraphBlock_
        self.Suffix = Suffix      # eg .map
        self.BlockSize = BlockSize

        self.Loaded = {}

    def Hash(self,ID):
        return int(ID//self.BlockSize)

    def Load(self,ID):
        if ID not in self.Loaded:
            BlockID = self.Hash(ID)
            filename = os.path.join(self.cwd,self.Prefix+str(BlockID)+self.Suffix)
            file = open(filename,"rb")
            block = pickle.load(file)
            file.close()
            self.Loaded.update(block)
        return self.Loaded[ID]

    def Save(self,Nodes):
        Sets = {}
        m = self.Hash(max(Nodes))
        for x in range(m):
            Sets[x] = {}

        for node in Nodes:
            r = hash(node.NodeID)
            Sets[r][node.NodeID] = node

        fileprefix = os.path.join(self.cwd,self.Prefix)
        for Set in Sets:
            filename = fileprefix+str(Set)+self.Suffix
            file = open(filename,"wb")
            data = Sets[Set]
            pickle.dump(data,file,protocol = pickle.HIGHEST_PROTOCOL)
            file.close()
        
