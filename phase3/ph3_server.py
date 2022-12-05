class CraqNode(): 
    def __init__(self):
        self.map = {} #data
        self.next = None
        self.prev = None
        self.tail = None
        
class ServerHandler:
    port = 9090
    server_ips = ["10.10.1.1", "10.10.1.2", "10.10.1.3"]
    index = 0
    
    def ServerHandler(self): 
        self.len = len(server_ips)
        self.node = CraqNode()
        
        if index != len - 1: #not tail
            self.node.next = makeConnection(self, server_ips[self.index + 1], port) 
        if index != 0:       #not head
            self.node.prev = makeConnection(self, server_ips[self.index - 1], port)
            
        self.node.tail = makeConnection(self, server_ips[self.len - 1], port) 
            

    def write(self, key, val):

        self.map[key] = {"msg" : val, "dirtybit" : 1} #data is dirty
        
        
        if self.next != None:                             # have next node
            writeSuccessor(self, key, val)
        else:                                              # tail node
            ack(self, key);                               # commit + ack back
            
        if self.prev != None:                             # if you hava a prev node. Head has no prev node
            self.prev.ack(self, key)         
            
        
    def read(self, key):
        if map.get(key) == None: 
            return None                       #key is not present
    
        if(self.map[key]["dirtybit"] == 0):   #data is commited at current node
            return self.map[key]["msg"]
        
        bitAtTail = readTail(self, key)       #check dirty bita at tail
        
        if bitAtTail == 0:                      # data is commited at tail
            return self.map[key]["msg"]        # return data
        
        return None                           #tail does not have data
    
    def ack(self, key):
        self.map[key]["dirtybit"] = 0
        try:
            self.node.prev.ack(key)
        except Thrift.TException as tx:
            print('writeSuccessor couldnt pass message' : %s' % (tx.message))

  
    def readTail(self, key): 
        bit = self.tail.checkDirtybit(key)
        if bit == 1: 
            return 1  #uncommited data
        return 0      #commited data
      
                      
    def checkDirtybit():
        if map.get(key) == None: 
            return 1                      #data is not present
        return map[key]["dirtybit"]       
      
        
    def writeSuccessor(self, key, value):
        try:
            currentTime = self.node.next.write(key, value)

        except Thrift.TException as tx:
            print('writeSuccessor couldnt pass message' : %s' % (tx.message))
        

    
    def makeConnection(self, host, port): 
        try: 
            # Init thrift connection and protocol handlers
            transport = TSocket.TSocket( host , port)
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            # Set client to our Example
            client = Example.Client(protocol)
            # Connect to server
            transport.open()
        except Thrift.TException as tx:
                print('openSocket error : %s' % (tx.message)) # TODO add host and port 
        return client
    
"""
    def closeSocket(self, tranport):
        # Close connection
        try:
            transport.close()
        except Thrift.TException as tx:
                print('closeSocket : %s' % (tx.message)) # TODO add host and port 
"""