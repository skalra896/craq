
host_list = ["10.10.1.1"]
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
        
        # Init thrift connection and protocol handlers
        transport = TSocket.TSocket( host_list[0] , port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        # Set client to our Example
        client = Handler.Client(protocol)

        # Connect to server
        transport.open()

        val = client.write(1,1)
        print(val)

        # Close connection
        transport.close()

except Thrift.TException as tx:
        print('Something went wrong : %s' % (tx.message))
