#!/usr/bin/env python

# This client demonstrates Thrift's connection and "oneway" asynchronous jobs
# Client connects to server host:port and calls 2 methods
# showCurrentTimestamp : which returns current time stamp from server
# asynchronousJob() : which calls a "oneway" method
#
import argparse
import random

import sys

# Example files
from Example import *
from Example.ttypes import *

# Thrift files
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
# your gen-py dir
sys.path.append('gen-py')


server_ips = ["10.10.1.1", "10.10.1.2", "10.10.1.3"]
handy = ""
port = 9090

ips_dict = {}

for ip in server_ips:
    try:
        transport = TSocket.TSocket(ip , port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)  
        # Set client to our Example
        client = Example.Client(protocol)
        ips_dict[ip] = {}
        ips_dict[ip]['host'] = ip
        ips_dict[ip]['transport'] = transport
        ips_dict[ip]['protocol'] = protocol
        ips_dict[ip]['client'] = client
    except Thrift.TException as tx:
        print('Something went wrong : %s' % (tx.message))

def write(oprs):
    ip_dict = ips_dict.get(server_ips[0])
    if ip_dict == None: return
    ip_dict.transport.open()
    for i in range(oprs):
        # Run showCurrentTimestamp() method on server
        client = ip_dict.client
        data = client.write(i, 0)
        print(data)
    ip_dict.tranport.close()
        
def read(oprs):
    for i in range(oprs):
        idx = random.randint(0, 2)
        ip_dict = ips_dict.get(server_ips[idx])
        if ip_dict == None: continue
        ip_dict.transport.open()
        client = ip_dict.client
        data = client.read(i)
        print(data)
        ip_dict.tranport.close()
    
def skew_read(oprs):
    idx = random.randint(0, 2)
    ip_dict = ips_dict.get(server_ips[idx])
    if ip_dict == None: return
    ip_dict.transport.open()
    client = ip_dict.client
    for i in range(oprs):
        data = client.read(i)
        print(data)
    ip_dict.tranport.close()

def main():
    parser = argparse.ArgumentParser(
                    prog = 'CRAQ Client',
                    description = 'Parses args through cli')
    parser.add_argument('--write', type=int)
    parser.add_argument('--read', type=int)
    parser.add_argument('--skew_read', type=int)
    args = parser.parse_args()
    write_ops = args.write
    read_ops = args.read
    skew_read_ops = args.skew_read_ops
    try:
        host = random.random(host_list)
        # Init thrift connection and protocol handlers
        transport = TSocket.TSocket( host , port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        # Set client to our Example
        client = Example.Client(protocol)

        if write_ops:
            write(client, write_ops)

        if read_ops:
            read(client, read_ops)

        if skew_read_ops:
            skew_read(client, skew_read_ops)
        # Connect to server
        transport.open()

        # Assume that you have a job which takes some time
        # but client sholdn't have to wait for job to finish
        # ie. Creating 10 thumbnails and putting these files to sepeate folders
        #client.asynchronousJob()

        # Close connection
        transport.close()

    except Thrift.TException as tx:
        print('Something went wrong : %s' % (tx.message))
main()
