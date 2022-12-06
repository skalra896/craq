
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
    
    server_ips = ["10.10.1.1", "10.10.1.2", "10.10.1.3"]
    index = 0
    
    def __init__(self): 
        self.length = len(self.server_ips)
        self.map = {} 
        self.next = None
        self.prev = None
        self.tail = None
        # if self.index != self.length - 1: #not tail
        #     self.next = self.makeConnection(self.server_ips[self.index + 1]) 
        # if self.index != 0:       #not head
        #     self.prev = self.makeConnection(self.server_ips[self.index - 1])
            
        # self.tail = self.makeConnection(self.server_ips[self.self.length - 1]) 
     
    def write(self, key, val):
    
        self.map[key] = {"msg" : val, "dirtybit" : 1} #data is dirty
        return val                        


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