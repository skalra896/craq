#!/usr/bin/env python

# This client demonstrates Thrift's connection and "oneway" asynchronous jobs
# Client connects to server host:port and calls 2 methods
# showCurrentTimestamp : which returns current time stamp from server
# asynchronousJob() : which calls a "oneway" method
#
import argparse
import random
import threading
import sys
import json
import multiprocessing
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
        self.bck_read_count = 0

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

    def run_write_cr_ops_for_time(self, i=0, size=500, time_sec=1):
        start_time = time.time()
        ip_dict = self.ips_dict.get(self.server_ips[0])
        if ip_dict == None: return
        while(time.time() - start_time <= time_sec):
            digits = len(str(i))
            val = str(i)+'0'*(size-digits)
            client = ip_dict['client']
            client.write_cr(i, val)
            self.write_count += 1
            i += 1

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

    def run_skew_read_ops_for_time(self, i=0, time_sec=1):
        self.total_skewed_ops = 0
        start_time = time.time()
        idx = random.randint(0, len(self.server_ips)-1)
        ip_dict = self.ips_dict.get(self.server_ips[idx])
        if ip_dict == None: return
        while(time.time() - start_time <= time_sec):
            self.total_skewed_ops += 1
            client = ip_dict['client']
            val = client.read(i)
            if val == '-1': self.skew_dirty_read += 1
            self.skew_read_count += 1
            i += 1

    def run_read_ops_for_time(self, i=0, cr=False, time_sec=1):
        self.total_read_ops = 0
        start_time = time.time()
        while(time.time() - start_time <= time_sec):
            self.total_read_ops += 1
            if cr:
                idx = -1
            else:
                idx = random.randint(0, len(self.server_ips)-1)
            ip_dict = self.ips_dict.get(self.server_ips[idx])
            if ip_dict == None: return
            client = ip_dict['client']
            val = client.read(i)
            if val == '-1': self.dirty_read += 1
            self.read_count += 1
            i += 1
    
    def handled_writes_sec(self, client, delay_time, write_req, size):
        current_time = time.time()
        i = write_req
        self.bck_read_count = 0
        while(time.time()-current_time <= 1):
            digits = len(str(i))
            val = str(i)+'0'*(size-digits)
            client.write(i, val)
            i+=1
            delay_start_time = time.time()
            j = write_req
            time.sleep(delay_time)
            '''
            while(time.time() - delay_start_time <= delay_time):
                idx = random.randint(0, len(self.server_ips)-1)
                ip_dict = self.ips_dict.get(self.server_ips[idx])
                if ip_dict == None: continue
                client_read = ip_dict['client']
                client_read.read(j)
                self.bck_read_count += 1
                j += 1
            '''

    def write_vs_read_sec(self):
        self.read_count = 0
        self.write_count = 0
        write_rates = [0, 50, 100, 150, 200, 250]
        write_ip_dict = self.ips_dict.get(self.server_ips[0])
        write_client = write_ip_dict['client']
        result_dict = {}
        for size in [500, 5000]:
            result_dict[size] = {}
            result_dict[size]['writes'] = write_rates
            result_dict[size]['reads'] = []
            for write_req in write_rates:
                self.read_count = 0
                threads = []
                delay_time = 1/write_req if write_req else 1
                write_thread = threading.Thread(target=self.handled_writes_sec, args=(write_client, delay_time, write_req, size))
                threads.append(write_thread)
                for _ in range(10):
                    read_thread = threading.Thread(target=self.run_read_ops_for_time, kwargs={'i':write_req})
                    threads.append(read_thread)
                for each_thread in threads:
                    each_thread.start()
                    each_thread.join()
                result_dict[size]['reads'].append(self.read_count+self.bck_read_count)
        try:
            with open('write_vs_read_per_sec.json', 'w') as fp:
                    json.dump(result_dict, fp)
        except:
            print('Read vs write per second not recorded')


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
            idx = random.randint(0, len(self.server_ips)-1)
            ip_dict = self.ips_dict.get(self.server_ips[idx])
            if ip_dict == None: continue
            client = ip_dict['client']
            data = client.read(i)
            if data != -1 : self.read_count += 1
        return 0

    def skew_read(self):
        idx = random.randint(0, len(self.server_ips)-1)
        ip_dict = self.ips_dict.get(self.server_ips[idx])
        if ip_dict == None: return
        client = ip_dict['client']
        for i in range(self.skew_read_ops):
            data = client.read(i)
            if data != -1: self.skew_read_count += 1

    def run_for_latency(self, load=False):
        sizes = [500,5000]
        latency_dict = {}
        for size in sizes:
            latency_dict[size] = {}
            write_ip_dict = self.ips_dict.get(self.server_ips[0])
            client = write_ip_dict['client']
            i = 1
            val = str(i)+'0'*(size-1)
            write_start_time = time.time()
            client.write(i, val)
            write_latency = time.time() - write_start_time
            latency_dict[size]['write_latency'] = write_latency
            read_ip_dict = self.ips_dict.get(self.server_ips[1])
            client = read_ip_dict['client']
            read_start_time = time.time()
            client.read(i)
            read_latency = time.time() - read_start_time
            latency_dict[size]['read_latency'] = read_latency
        if load:
            try:
                with open('read_write_latency_with_load.json', 'w') as fp:
                    json.dump(latency_dict, fp)
            except:
                import pdb; pdb.set_trace()
        else:
            try:
                with open('read_write_latency_no_load.json', 'w') as fp:
                    json.dump(latency_dict, fp)
            except:
                import pdb; pdb.set_trace()
    
    def run_for_load_latency(self):
        latency_thread = threading.Thread(target=self.run_for_latency, kwargs={'load':True})
        other_thread = threading.Thread(target=self.run_for_read_write_throughput)
        latency_thread.start()
        other_thread.start()
        latency_thread.join()
        other_thread.join()


    def run_for_read_write_throughput(self, cr=False):
        sizes = [500,5000]
        result_dict = {}
        self.write_count = 0
        self.read_count = 0
        for size in sizes:
            result_dict[size] = {}
            write_list = []
            read_list = []
            for op in range(10):
                threads_list = []
                i=200000
                if cr:
                    for _ in range(10):#10 thread for write
                        p_write = threading.Thread(target=self.run_write_cr_ops_for_time, kwargs={'i':i,'size':size})
                        threads_list.append(p_write)
                        i += 10000
                else:
                    for _ in range(10):#10 thread for write
                        p_write = threading.Thread(target=self.run_write_ops_for_time, kwargs={'i':i,'size':size})
                        threads_list.append(p_write)
                        i += 10000
                for each_thread in threads_list:
                    each_thread.start()
                    each_thread.join()
                write_list.append(self.write_count)
                threads_list = []
                if cr:
                    for _ in range(30):#30 threads for read
                        p_read=threading.Thread(target=self.run_read_ops_for_time, kwargs={'i':i, 'cr':True})
                        threads_list.append(p_read)
                else:
                    for _ in range(30):#30 threads for read
                        p_read=threading.Thread(target=self.run_read_ops_for_time, kwargs={'i':i})
                        threads_list.append(p_read)
                for each_thread in threads_list:
                    each_thread.start()
                    each_thread.join()
                read_list.append(self.read_count)
                self.write_count = 0
                self.read_count = 0
            result_dict[size]['write_list'] = write_list
            result_dict[size]['read_list'] = read_list
        try:
            with open('read_write_thp.json', 'w') as fp:
                json.dump(result_dict, fp)
        except:
            import pdb; pdb.set_trace()

    def run_for_table(self, cr=False):
        sizes = [500,5000]
        result_dict = {}
        for size in sizes:
            result_dict[size] = {}
            write_list = []
            read_list = []
            dirty_read_list = []
            clean_read_list = []
            skew_read_list = []
            dirty_skew_read_list = []
            i = 0
            for op in range(10):#no. of experiment
                threads_list = []
                if cr:
                    for _ in range(10):#10 thread of write, 30 for read
                        p_write = threading.Thread(target=self.run_write_cr_ops_for_time, kwargs={'i':i,'size':size})
                        threads_list.append(p_write)
                        for read_i in range(3):
                            p_read=threading.Thread(target=self.run_read_ops_for_time, kwargs={'i':i, 'cr':True})
                            threads_list.append(p_read)
                        #p_skew_read=threading.Thread(target=self.run_read_ops_for_time, kwargs={'i':i})
                        #print ("count is",i)
                        #threads_list.append(p_skew_read)
                        i += 10000
                else:
                    for _ in range(10):#10 thread of write, 30 for read
                        p_write = threading.Thread(target=self.run_write_ops_for_time, kwargs={'i':i,'size':size})
                        threads_list.append(p_write)
                        for read_i in range(3):
                            p_read=threading.Thread(target=self.run_read_ops_for_time, kwargs={'i':i})
                            threads_list.append(p_read)
                        #p_skew_read=threading.Thread(target=self.run_read_ops_for_time, kwargs={'i':i})
                        #print ("count is",i)
                        #threads_list.append(p_skew_read)
                        i += 10000
                for each_thread in threads_list:
                    each_thread.start()
                    each_thread.join()
                write_list.append(self.write_count)
                read_list.append(self.read_count)
                dirty_read_list.append(self.dirty_read)
                #skew_read_list.append(self.skew_read_count)
                #dirty_skew_read_list.append(self.skew_dirty_read)
                self.write_count = 0
                self.read_count = 0
                self.dirty_read = 0
                self.skew_read_count = 0
                self.skew_dirty_read = 0
            result_dict[size]['write_list'] = write_list
            result_dict[size]['read_list'] = read_list
            result_dict[size]['dirty_read_list'] = dirty_read_list
            for j in range(10):
                clean_read_list.append(read_list[j]-dirty_read_list[j])
            result_dict[size]['clean_read_list'] = clean_read_list
            #result_dict[size]['skew_read_list'] = skew_read_list
            #result_dict[size]['dirty_skew_read_list'] = dirty_skew_read_list
            
        try:
            with open('table_result.json', 'w') as fp:
                json.dump(result_dict, fp)
        except:
            import pdb; pdb.set_trace()

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
    
    #client_obj.run_for_table()
    #client_obj.run_for_table(cr=True)
    #import pdb; pdb.set_trace()
    #client_obj.run_ops()
    #client_obj.run_for_read_write_throughput()
    #client_obj.run_for_read_write_throughput(cr=True)
    #client_obj.run_for_latency()
    #client_obj.run_for_load_latency()
    client_obj.write_vs_read_sec()
    for ip in client_obj.server_ips:
        client_obj.ips_dict[ip]['transport'].close()

main()