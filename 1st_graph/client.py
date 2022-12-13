#!/usr/bin/env python

# This client demonstrates Thrift's connection and "oneway" asynchronous jobs
# Client connects to server host:port and calls 2 methods
# showCurrentTimestamp : which returns current time stamp from server
# asynchronousJob() : which calls a "oneway" method
#
import argparse
import random

import sys
# your gen-py dir
sys.path.append('gen-py')
import time
import matplotlib.pyplot as plt
from Handler import *
from Handler.ttypes import *

# Thrift files
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

class Client:
    server_ips = ["10.10.1.3", "10.10.1.2", "10.10.1.5"]
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
        self.dirty_read=0
        self.skew_dirty_read=0

    def connect_servers(self):
        for i in range(len(self.server_ips)):
            ip = self.server_ips[i]
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
                client.set_node_connections(i)
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

    def run_write_ops_for_time(self, i=0, size=500, time_sec=1):
        start_time = time.time()
        ip_dict = self.ips_dict.get(self.server_ips[0])
        if ip_dict == None: return
        while(time.time() - start_time <= time_sec):
            digits = len(str(i))
            val = str(i)+'0'*(size-digits)
            client = ip_dict['client']
            client.write(i, val)
            self.write_count += 1
            i += 1

            #self.read()
            #self.skew_read()

    def run_skew_read_ops_for_time(self, i=0, time_sec=1):
        self.total_skewed_ops = 0
        start_time = time.time()
        idx = random.randint(0, 2)
        ip_dict = self.ips_dict.get(self.server_ips[idx])
        if ip_dict == None: return
        while(time.time() - start_time <= time_sec):
            self.total_skewed_ops += 1
            client = ip_dict['client']
            val = client.read(i)
            if val == '-1': self.skew_dirty_read += 1
            self.skew_read_count += 1
            i += 1

    def run_read_ops_for_time(self, i=0, time_sec=1):
        self.total_read_ops = 0
        start_time = time.time()
        while(time.time() - start_time <= time_sec):
            self.total_read_ops += 1
            idx = random.randint(0, 2)
            ip_dict = self.ips_dict.get(self.server_ips[idx])
            if ip_dict == None: return
            client = ip_dict['client']
            val = client.read(i)
            if val == '-1': self.dirty_read += 1
            self.read_count += 1
            i += 1

    def write(self):
        ip_dict = self.ips_dict.get(self.server_ips[0])
        if ip_dict == None: return
        i=0
        while 1:
            client = ip_dict['client']
            client.write(i, i)
            self.write_count += 1
            i += 1

    def read(self):
        for i in range(self.read_ops):
            idx = random.randint(0, 2)
            ip_dict = self.ips_dict.get(self.server_ips[idx])
            if ip_dict == None: continue
            client = ip_dict['client']
            data = client.read(i)
            if data != -1 : self.read_count += 1
        return 0

    def skew_read(self):
        idx = random.randint(0, 2)
        ip_dict = self.ips_dict.get(self.server_ips[idx])
        if ip_dict == None: return
        client = ip_dict['client']
        for i in range(self.skew_read_ops):
            data = client.read(i)
            if data != -1: self.skew_read_count += 1

def main():
    parser = argparse.ArgumentParser(
                    prog = 'CRAQ Client',
                    description = 'Parses args through cli')
    parser.add_argument('--write', type=int, default=10)
    parser.add_argument('--read', type=int, default=10)
    parser.add_argument('--skew_read', type=int, default=10)
    args = parser.parse_args()
    write_ops = args.write
    read_ops = args.read
    skew_read_ops = args.skew_read

    client_obj = Client(write_ops, read_ops, skew_read_ops)
    client_obj.connect_servers()
    import multiprocessing
    from multiprocessing import Process
    write_list = []
    read_list = []
    dirty_read_list = []
    skew_read_list = []
    dirty_skew_read_list = []
    for op in range(10):#no. of experiment
        proc = []
        i=0
        for _ in range(10):#10 thread of write, read, skew_read: total 9 threads
            p_write=Process(target=client_obj.run_write_ops_for_time(i=i))
            p_read=Process(target=client_obj.run_read_ops_for_time(i=i))
            p_skew_read=Process(target=client_obj.run_skew_read_ops_for_time(i=i))
            #print ("count is",i)
            p_write.start()
            p_read.start()
            p_skew_read.start()
            proc.append(p_write)
            proc.append(p_read)
            proc.append(p_skew_read)
            i += 10000
        for p in proc:
            p.join()
        write_list.append(client_obj.write_count)
        read_list.append(client_obj.read_count)
        dirty_read_list.append(client_obj.dirty_read)
        skew_read_list.append(client_obj.skew_read_count)
        dirty_skew_read_list.append(client_obj.skew_dirty_read)
        client_obj.write_count = 0
        client_obj.read_count = 0
        client_obj.dirty_read = 0
        client_obj.skew_read_count = 0
        client_obj.skew_dirty_read = 0
    import pdb; pdb.set_trace()
    client_obj.run_ops()
    for ip in client_obj.server_ips:
        client_obj.ips_dict[ip]['transport'].close()

main()

# #thread

# import threading
# from queue import Queue

# def read(self, key):
#     print(key)

# def write(self, key, val):
#     print(key, val)

# queue  =  Queue()

# for x in range(2):
#     r = threading.Thread(target=read, args=(1,1))
#     queue.put( r)

# for x in range(2):
#     queue.get().start()
    
# for x in range(2):
#     queue.join()

