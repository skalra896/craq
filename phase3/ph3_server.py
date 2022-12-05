class ServerHandler:
    port = 9090
    server_ips = ["10.10.1.1", "10.10.1.2", "10.10.1.3"]
    index = 0
    
    def __init__(self): 
        self.length = len(server_ips)
        self.map = {} 
        self.next = None
        self.prev = None
        self.tail = None
        if self.index != self.length - 1: #not tail
            self.next = self.makeConnection(self.server_ips[self.index + 1]) 
        if self.index != 0:       #not head
            self.prev = self.makeConnection(self.server_ips[self.index - 1])
            
        self.tail = self.makeConnection(self.server_ips[self.self.length - 1]) 
            

    def write(self, key, val):

        self.node.map[key] = {"msg" : val, "dirtybit" : 1} #data is dirty

        if self.next != None:                             # have next node
            self.writeSuccessor(key, val)

        else:                                              # tail node
            self.ack(self, key)                             # commit + ack back                            
            
        
    def read(self, key):
        if self.node.map.get(key) == None: 
            return None                       #key is not present
    
        if(self.node.map[key]["dirtybit"] == 0):   #data is commited at current node
            return self.node.map[key]["msg"]
        
        bitAtTail = self.readTail(key)       #check dirty bita at tail
        
        if bitAtTail == 0:                      # data is commited at tail
            return self.node.map[key]["msg"]        # return data
        
        return None                           #tail does not have data
    
    def ack(self, key):
        self.node.map[key]["dirtybit"] = 0
        try:
            self.node.prev.ack(key)
        except Thrift.TException as tx:
            print('writeSuccessor couldnt pass message: %s' % (tx.message))

  
    def readTail(self, key): 
        bit = self.tail.checkDirtybit(key)
        if bit == 1: 
            return 1  #uncommited data
        return 0      #commited data
                      
    def checkDirtybit():
        if self.map.get(key) == None: 
            return 1                      #data is not present
        return self.map[key]["dirtybit"]       
        
    def writeSuccessor(self, key, value):
        try:
            val = self.node.next.write(key, value)
            return val

        except Thrift.TException as tx:
            print('writeSuccessor couldnt pass message: %s' % (tx.message))
        
    def makeConnection(self, host): 
        try: 
            # Init thrift connection and protocol handlers
            transport = TSocket.TSocket(host , self.port)
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            # Set client to our Example
            client = Example.Client(protocol)
            # Connect to server
            transport.open()
        except Thrift.TException as tx:
                print('openSocket error : %s, host: %s, port: %s' 
                        % (tx.message, host, self.port)) # TODO add host and port 
        return client
    
"""
    def closeSocket(self, tranport):
        # Close connection
        try:
            transport.close()
        except Thrift.TException as tx:
                print('closeSocket : %s' % (tx.message)) # TODO add host and port 
"""