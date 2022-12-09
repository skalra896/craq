
host_list = ["10.10.1.1","10.10.1.2"]
write_node = "10.10.1.1"
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

        for i in range(0, len(host_list)):
                print('connecting host')
                transport = TSocket.TSocket( host_list[i] , port)
                transport = TTransport.TBufferedTransport(transport)
                protocol = TBinaryProtocol.TBinaryProtocol(transport)
                client = Handler.Client(protocol)
                transport.open()
                print('index : %s calling set node connection' %i)
                client.set_node_connections()
                print('done connection')
      
      


except Thrift.TException as tx:
        print('Something went wrong : %s' % (tx.message))
