
port = 9090

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
    
    server_ips = ["10.10.1.1", "10.10.1.2"]
    index = 0
    
    def __init__(self): 
        self.length = len(self.server_ips)
        self.map = {} 
        self.next = None
        self.prev = None
        self.tail = None

    
    def set_node_connections(self):
        print('set node connections')
        if self.index != self.length - 1 and self.next is None: #not tail
            self.next = self.makeConnection(self.server_ips[self.index + 1]) 
        if self.index != 0 and self.prev is None:       #not head
            self.prev = self.makeConnection(self.server_ips[self.index - 1])

        if self.index != self.length - 1 and self.tail is None: 
            self.tail = self.makeConnection(self.server_ips[self.length - 1]) 

    def write(self, key, val):
    
        self.map[key] = {"msg" : val, "dirtybit" : 1} #data is dirty

        if self.next != None:                             # have next node
            self.writeSuccessor(key, val)

        else:                                              # tail node
            self.ack(key)                             # commit + ack back                            
     
    def ack(self, key):
        self.set_node_connections()
        self.map[key]["dirtybit"] = 0
        try:
            self.prev.ack(key)
        except Thrift.TException as tx:
            print('writeSuccessor couldnt pass message: %s' % (tx.message))

    def writeSuccessor(self, key, value):
        self.set_node_connections()
        try:
            val = self.next.write(key, value)
            return val

        except Thrift.TException as tx:
            print('writeSuccessor couldnt pass message: %s' % (tx.message))

    def makeConnection(self, host): 
        try: 
            # Init thrift connection and protocol handlers
            print('count' )
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
