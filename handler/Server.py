
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
    
    server_ips = ["10.10.1.1", "10.10.1.2"]
    index = 0
    
    def __init__(self): 
        self.length = len(self.server_ips)
        self.map = {} 
        self.next = None
        self.prev = None
        self.tail = None

    
    def set_node_connections(self):
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
