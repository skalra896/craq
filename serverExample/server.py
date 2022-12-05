class ServerHandler:
    map = {}
    server_ips = ["10.10.1.1", "10.10.1.2", "10.10.1.3"]
    handy = ""
    head = ""
    tail = ""
    port = 9090
    
    def ServerHandler(self, index): 
        self.index = index
        self.len = len(server_ips)
        
        if index != len - 1:
            self.next = makeConnection(self, server_ips[index + 1], port) 
        if index != 0: 
            self.prev = makeConnection(self, server_ips[index - 1], port)
            
        tail = makeConnection(self, server_ips[len - 1], port) 
            

    def write(self, key, val):
        self.map[key] = {"msg" : val, "dirtybit" : 1} #data is dirty
        
        if self.next != None: #if you have a next node. Tail has no next node
            writeSuccessor(self, key, val)
        if self.prev != None: # if you hava a prev node. Head has no prev node
            self.prev.ack(self, key)  # TODO for write request client gets any output? as per paper there is no output
            
        
    def read(self, key):
        if(self.map[key]["dirtybit"] == 0): #data is commited at current node
            return self.map[key]["msg"]
        
        bitAtTail = readTail(self, key)     #check tail dirty bit
        
        if(bitAtTail == 0):         # tail has commited
            return self.map[key]["msg"] # return data
        
        return None #data is not commited at tail
    
    def ack(self, key):
        self.map[key]["dirtybit"] = 0
        
        if(self.map[key]["dirtybit"] == 0):
            return null
        return list[0]
    
    
    def readTail(self, key): 
        bit = self.tail.read(key)
        if bit is None: 
            return 1 
        return 0
        
        
    def writeSuccessor(self, host, port):
        try:
            # Run showCurrentTimestamp() method on server
            currentTime = self.next.showCurrentTimestamp()
            print(currentTime)

        except Thrift.TException as tx:
            print('Something went wrong : %s' % (tx.message))
        

    
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