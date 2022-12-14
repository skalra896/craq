
port = 9090

from operator import index
import sys
# your gen-py dir
sys.path.append('gen-py')

import time

from Handler import *
from Handler.ttypes import *

# Thrift files
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class ServiceHandler:
    
    server_ips = [["10.10.1.3", "10.10.1.2", "10.10.1.5", "10.10.1.6", "10.10.1.7"]# node 0,1,2

    def __init__(self): 
        self.length = len(self.server_ips)
        self.map = {} 
        self.next = None
        self.prev = None
        self.tail = None

    
    def set_node_connections(self, index):
        self.index = index
        
        print('inside set node connections method ')

        if self.index != self.length - 1 : #not tail
            print('making next connection set node connections, index: %s '% (self.index))
            self.next = self.makeConnection(self.server_ips[self.index + 1]) 
            print('connected %s to %s as next node' %(self.server_ips[self.index], self.server_ips[self.index+1]))
    
        
        if self.index != 0 :       #not head
            print('making prev connection set node connections, index: %s '% (self.index))
            self.prev = self.makeConnection(self.server_ips[self.index - 1])
            print('connected %s to %s as prev node' %(self.server_ips[self.index], self.server_ips[self.index-1]))

        if self.index != self.length - 1: 
            print('making tail connection set node connections, index: %s '% (self.index))
            self.tail = self.makeConnection(self.server_ips[self.length - 1]) 
            print('connected %s to %s as tail node' %(self.server_ips[self.index], self.server_ips[self.length-1]))


    def makeConnection(self, host): 
        try: 
            # Init thrift connection and protocol handlers
            
            transport = TSocket.TSocket(host , port)
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            
            client = Handler.Client(protocol)
            
            # Connect to server
            transport.open()
            print('connected to host : %s' %(host))
            
        except Thrift.TException as tx:
                print('openSocket error : %s, host: %s, port: %s' 
                        % (tx.message, host, port)) # TODO add host and port 
  
        return client

    def write(self, key, val):
        #print('making next connection set node connections, index: %s '% (self.index))
        
        self.map[key] = {"msg" : val, "dirtybit" : 1} #data is dirty

        if self.next != None:                             # have next node
            self.writeSuccessor(key, val)

        else:                                              # tail node
            self.ack(key)                             # commit + ack back        
    
    def write_cr(self, key, val):
        #print('making next connection set node connections, index: %s '% (self.index))
        
        self.map[key] = {"msg" : val, "dirtybit" : 0} #data is dirty

        if self.next != None:                             # have next node
            self.writeSuccessor(key, val)
     
    def ack(self, key):
        self.map[key]["dirtybit"] = 0
        #print('inside ack method sending from %s' % (self.server_ips[self.index]))
        if self.prev != None: 
            try:
                self.prev.ack(key)
                #print('sent ack from %s to %s ' % (self.server_ips[self.index], self.server_ips[self.index - 1]))
            except Thrift.TException as tx:
                pass
                #print('Ack couldnt pass message: %s' % (tx.message))

    def read(self, key):
        #print('making read at index: %s '% (self.index))
        if self.map.get(key) == None: 
            return '-1'                     #key is not present
        
        #print('Dirty bit val: %s'%(self.map[key]["dirtybit"]))

        if(self.map[key]["dirtybit"] == 0):   #data is commited at current node
            return self.map[key]["msg"]
        
        if self.tail != None: 
            bitAtTail = self.readTail(key)       #check dirty bit at tail
            
            if bitAtTail == 0:                      # data is commited at tail
                return self.map[key]["msg"]        # return data
            
        return '-1'    

    def readTail(self, key):
        #print('Checking tail for read') 
        bit = self.tail.checkDirtybit(key)
        if bit == 0: 
            return 0  #commited data
        return 1      #uncommited data
                      
    def checkDirtybit(self, key):
        #print('Checking dirtybit for read')
        if self.map.get(key) == None: 
            return 1                      #data is not present
        return self.map[key]["dirtybit"]   

    def writeSuccessor(self, key, value):
        try:
            self.next.write(key, value)

        except Thrift.TException as tx:
            pass
            #print('writeSuccessor could not pass message: %s' % (tx.message))
    
        
# set handler to our implementation
handle = ServiceHandler()

processor = Handler.Processor(handle)
transport = TSocket.TServerSocket("0.0.0.0", port)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

# set server
server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

print('Starting server')
server.serve()
handle.createChain()
