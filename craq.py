import argparse
import paramiko
import os
import time

class DoubleLL:
    def __init__(self):
        self.head = ListNode(None, None)
        self.tail = ListNode(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_node(self, node):
        prev_node = self.tail.prev
        self.tail.prev = node
        node.next = self.tail
        prev_node.next = node
        node.prev = prev_node

class ListNode:
    def __init__(self, ip, user):
        self.ip = ip
        self.user = user
        self.next = None
        self.prev = None
        self.client = False
        self.server = False
        self.headnode = False
        self.tailnode = False
        self.commit_ids = []
        self.msg_id_dict = {}
        self.ssh_obj = None

class craq:
    def __init__(self, ips, users):
        self.ip_list = ips
        self.users_list = users
        self.usern = 'sk6691'
        self.hostname = '.emulab.net'
        self.ssh_dict = {}
        self.ip_node_dict = {}
        self.user_node_dict = {}
        self.dll = DoubleLL()
        self.nodes_list = []
        for ip in range(len(ip_list)):
            node = ListNode(self.ip_list[i], self.users_list[i])
            self.ip_node_dict[self.ip_list[i]] = node
            self.user_node_dict[self.users_list[i]] = node
            self.dll.add_node(node)
            self.nodes_list.append(node)
        self.setup_ssh_obj()
    
    def setup_ssh_obj(self):
        for user, node in self.user_node_dict.items():
            if not node.ssh_obj:
                ssh_obj = paramiko.SSHClient()
                ssh_obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_obj.connect(user+self.hostname, username=self.usern, key_filename='craq')
                node.ssh_obj = ssh_obj
                ssh_obj.close()

    def set_headnode(self):
        self.dll.head.next.headnode = True
    
    def set_tailnode(self):
        self.dll.tail.prev.tailnode = True
    
    def _server_run(self, user):
        client = self.ssh_dict[user]
        client.connect(user+self.hostname, username=self.usern, key_filename='craq')
        stdin, stdout, stderr = client.exec_command("cd /tmp/work_dir/serverExample\n; python3 ServerPython.py")
        client.close()

    def run_servers(self):
        for ip,node in self.ip_node_dict.items():
            if node.headnode:
                continue
            self._server_run(node.user)

    def add_setup_obj(self):
        for node in self.nodes_list:
            each_user = node.user
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = client.exec_command("sudo rm -r /tmp/work_dir")
            time.sleep(1)
            stdin, stdout, stderr = client.exec_command("mkdir /tmp/work_dir")
            time.sleep(1)
            stdin, stdout, stderr = client.exec_command("sudo apt-get -y install libboost-dev libboost-test-dev libboost-program-options-dev \
            libboost-filesystem-dev libboost-thread-dev libevent-dev automake libtool flex bison pkg-config g++ libssl-dev")
            stdout.readlines()
            if stderr.readlines():
                client.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = client.exec_command("cd /tmp/work_dir; wget dlcdn.apache.org/thrift/0.17.0/thrift-0.17.0.tar.gz; tar -xvzf thrift-0.17.0.tar.gz")
            stdout.readlines()
            stdin, stdout, stderr = client.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; ./bootstrap.sh")
            stdout.readlines()
            if stderr.readlines():
                client.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = client.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; ./configure")
            print(stdout.readlines())
            stdin, stdout, stderr = client.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; sudo make")
            print(stdout.readlines())
            if stderr.readlines():
                client.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = client.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; sudo make install")
            print(stdout.readlines())
            if stderr.readlines():
                client.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = client.exec_command("thrift -version")
            print(stdout.readlines())
            stdin, stdout, stderr = client.exec_command("cd /tmp/work_dir/thrift-0.17.0/lib/py\n; sudo python3 setup.py install")
            os.popen("echo 2225 | sudo -S scp -i craq -o StrictHostKeyChecking=no -r client %s@%s%s:/tmp/work_dir/"%(usern,each_user,hostname)).read()
            os.popen("echo 2225 | sudo -S scp -i craq -o StrictHostKeyChecking=no -r serverExample %s@%s%s:/tmp/work_dir/"%(usern,each_user,hostname)).read()
            #import pdb; pdb.set_trace()
            ssh_dict[each_user] = client
            client.close()

    def update_ip(self, host_user, server_ip):
        client = self.ssh_dict[host_user]
        client.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
        stdin, stdout, stderr = client.exec_command("sudo sed -i 's/host = .*/host = \"%s\"/' client/PythonClient.py"%(server_ip))
        client.close()
    
    def setup_nodes(self):
        self.add_setup_obj()
        self.set_headnode()
        self.set_tailnode()
        self.run_servers()

def main():
    parser = argparse.ArgumentParser(
                    prog = 'CRAQ',
                    description = 'Parses args through cli')
    parser.add_argument('--users', nargs='+', help = 'nodes')
    parser.add_argument('--ips', nargs='+', help = 'ips')
    parser.add_argument("--setup", action='store_true', help="Sets up nodes")
    args = parser.parse_args()
    import pdb; pdb.set_trace()
    if args.setup:
        craq_obj = craq(args.ips, args.users)
        craq_obj.setup_nodes()

main()