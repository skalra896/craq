#!/usr/bin/env python

# This client demonstrates Thrift's connection and "oneway" asynchronous jobs
# Client connects to server host:port and calls 2 methods
# showCurrentTimestamp : which returns current time stamp from server
# asynchronousJob() : which calls a "oneway" method
#
import argparse
import random

import sys
import time
from Handler import *
from Handler.ttypes import *

# Thrift files
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
# your gen-py dir
sys.path.append('gen-py')

class Client:
    server_ips = ["155.98.39.2", "155.98.39.3", "155.98.39.4"]
    handy = "155.98.39.100"
    port = 9090

    ips_dict = {}

    def __init__(self, write, read, skew_read):
        self.write_ops = write
        self.read_ops = read
        self.skew_read_ops = skew_read
        self.write_count = 0
        self.read_count = 0
        self.skew_read_count = 0
        self.read_time = 0
        self.write_time = 0
        self.skew_read_time = 0

    def connect_servers(self):
        for ip in self.server_ips:
            try:
                print('connecting host')
                transport = TSocket.TSocket(ip , self.port)
                transport = TTransport.TBufferedTransport(transport)
                protocol = TBinaryProtocol.TBinaryProtocol(transport)  
                # Set client to our Example
                client = Handler.Client(protocol)
                self.ips_dict[ip] = {}
                self.ips_dict[ip]['host'] = ip
                self.ips_dict[ip]['transport'] = transport
                self.ips_dict[ip]['protocol'] = protocol
                self.ips_dict[ip]['client'] = client
                self.ips_dict[ip]['transport'].open()
                print('index : %s calling set node connection' %i)
                client.set_node_connections()
                print('done connection')
            except Thrift.TException as tx:
                print('Something went wrong : %s' % (tx.message))

    def run_ops(self):
        start_time = time.time()
        self.write()
        self.write_time = time.time() - start_time
        start_time = time.time()
        self.read()
        self.read_time = time.time() - start_time
        start_time = time.time()
        self.skew_read()
        self.skew_read_time = time.time() - start_time

    def write(self):
        ip_dict = self.ips_dict.get(self.server_ips[0])
        if ip_dict == None: return
        for i in range(self.write_ops):
            client = ip_dict.client
            client.write(i, i)
            self.write_count += 1      
            
    def read(self):
        for i in range(self.read_ops):
            idx = random.randint(0, 2)
            ip_dict = self.ips_dict.get(self.server_ips[idx])
            if ip_dict == None: continue
            client = ip_dict.client
            data = client.read(i)
            if data: self.read_count += 1
        
    def skew_read(self):
        idx = random.randint(0, 2)
        ip_dict = self.ips_dict.get(self.server_ips[idx])
        if ip_dict == None: return
        client = ip_dict.client
        for i in range(self.skew_read_ops):
            data = client.read(i)
            if data: self.skew_read_count += 1

def main():
    parser = argparse.ArgumentParser(
                    prog = 'CRAQ Client',
                    description = 'Parses args through cli')
    parser.add_argument('--write', type=int, default=10)
    parser.add_argument('--read', type=int, default=0)
    parser.add_argument('--skew_read', type=int, default=0)
    args = parser.parse_args()
    write_ops = args.write
    read_ops = args.read
    skew_read_ops = args.skew_read_ops

    client_obj = Client(write_ops, read_ops, skew_read_ops)
    client_obj.connect_servers()
    client_obj.run_ops()
    for ip in client_obj.server_ips:
        client_obj.ips_dict[ip]['transport'].close()
    
main()
