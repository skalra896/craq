
server_ips = ["155.98.39.2", "155.98.39.3", "155.98.39.4"]

port = 9090

import sys

# your gen-py dir
sys.path.append('gen-py')


from Handler import *
from Handler.ttypes import *

# Thrift files
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


try:
        for i in range(0, len(server_ips)):
                print('connecting host')
                transport = TSocket.TSocket( server_ips[i] , port)
                transport = TTransport.TBufferedTransport(transport)
                protocol = TBinaryProtocol.TBinaryProtocol(transport)
                client = Handler.Client(protocol)
                transport.open()
                print('index : %s calling set node connection' %i)
                client.set_node_connections(i)
                print('done connection')
                
except Thrift.TException as tx:
                print('Something went wrong : %s' % (tx.message))

client.write(1,1)