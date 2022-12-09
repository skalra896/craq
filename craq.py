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
        self.ip_list = ips[2:]
        self.users_list = users[2:]
        self.usern = 'sk6691'
        self.hostname = '.emulab.net'
        self.ip_node_dict = {}
        self.user_node_dict = {}
        self.dll = DoubleLL()
        self.nodes_list = []
        self.client_node = ListNode(ips[0], users[0])
        self.handy_node = ListNode(ips[1], users[1])
        self._ssh_obj_setup(self.client_node)
        self._ssh_obj_setup(self.handy_node)
        for i in range(len(self.ip_list)):
            node = ListNode(self.ip_list[i], self.users_list[i])
            self.ip_node_dict[self.ip_list[i]] = node
            self.user_node_dict[self.users_list[i]] = node
            self.dll.add_node(node)
            self.nodes_list.append(node)
        self.setup_ssh_obj()
    
    def _ssh_obj_setup(self, node):
        ssh_obj = paramiko.SSHClient()
        ssh_obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_obj.connect(node.user+self.hostname, username=self.usern, key_filename='craq')
        node.ssh_obj = ssh_obj
        ssh_obj.close()

    def setup_ssh_obj(self):
        for user, node in self.user_node_dict.items():
            if not node.ssh_obj:
                self._ssh_obj_setup(node)

    def set_headnode(self):
        self.dll.head.next.headnode = True
    
    def set_tailnode(self):
        self.dll.tail.prev.tailnode = True
    
    def _server_run(self, node):
        ssh_obj = node.ssh_obj
        ssh_obj.connect(node.user+self.hostname, username=self.usern, key_filename='craq')
        stdin, stdout, stderr = ssh_obj.exec_command("cd /tmp/work_dir/serverExample\n; python3 ServerPython.py")
        ssh_obj.close()

    def run_servers(self):
        for node in self.nodes_list:
            self._server_run(node)

    def _server_stop(self, node):
        ssh_obj = node.ssh_obj
        ssh_obj.connect(node.user+self.hostname, username=self.usern, key_filename='craq')
        stdin, stdout, stderr = ssh_obj.exec_command("ps -ef | grep python3 | grep ServerPython.py")
        response = stdout.readlines()
        for each_res in response:
            proc = each_res.strip().split()[1]
            stdin, stdout, stderr = ssh_obj.exec_command("kill -9 %s"%(proc))
        ssh_obj.close()

    def stop_servers(self):
        for node in self.nodes_list:
            self._server_stop(node)

    def add_client_server_files(self):
        for node in ([self.client_node, self.handy_node] + self.nodes_list):
            each_user = node.user
            os.popen("echo 2225 | sudo -S scp -i craq -o StrictHostKeyChecking=no -r handler %s@%s%s:/tmp/work_dir/"%(self.usern,each_user,self.hostname)).read()
            os.popen("echo 2225 | sudo -S scp -i craq -o StrictHostKeyChecking=no -r client %s@%s%s:/tmp/work_dir/"%(self.usern,each_user,self.hostname)).read()
            os.popen("echo 2225 | sudo -S scp -i craq -o StrictHostKeyChecking=no -r serverExample %s@%s%s:/tmp/work_dir/"%(self.usern,each_user,self.hostname)).read()

    def add_setup_obj(self):
        for node in ([self.client_node, self.handy_node] + self.nodes_list):
            each_user = node.user
            ssh_obj = node.ssh_obj
            ssh_obj.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = ssh_obj.exec_command("thrift --version")
            res = stdout.read()
            if "Thrift version" in str(res): continue
            stdin, stdout, stderr = ssh_obj.exec_command("sudo rm -r /tmp/work_dir")
            print(stdout.readlines())
            stdin, stdout, stderr = ssh_obj.exec_command("mkdir /tmp/work_dir")
            print(stdout.readlines())
            stdin, stdout, stderr = ssh_obj.exec_command("sudo apt-get -y update; sudo apt-get -y install libboost-dev libboost-test-dev libboost-program-options-dev \
            libboost-filesystem-dev libboost-thread-dev libevent-dev automake libtool flex bison pkg-config g++ libssl-dev")
            stdout.readlines()
            if stderr.readlines():
                ssh_obj.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = ssh_obj.exec_command("cd /tmp/work_dir; wget dlcdn.apache.org/thrift/0.17.0/thrift-0.17.0.tar.gz; tar -xvzf thrift-0.17.0.tar.gz")
            stdout.readlines()
            stdin, stdout, stderr = ssh_obj.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; ./bootstrap.sh")
            stdout.readlines()
            if stderr.readlines():
                ssh_obj.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = ssh_obj.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; ./configure")
            print(stdout.readlines())
            stdin, stdout, stderr = ssh_obj.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; sudo make")
            print(stdout.readlines())
            if stderr.readlines():
                ssh_obj.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = ssh_obj.exec_command("cd /tmp/work_dir/thrift-0.17.0\n; \")
            print(stdout.readlines())
            if stderr.readlines():
                ssh_obj.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
            stdin, stdout, stderr = ssh_obj.exec_command("thrift -version")
            print(stdout.readlines())
            stdin, stdout, stderr = ssh_obj.exec_command("cd /tmp/work_dir/thrift-0.17.0/lib/py\n; sudo python3 setup.py install")
            ssh_obj.close()

    def _update_ips(self, host_node, handy_node = None):
        ssh_obj = host_node.ssh_obj
        ssh_obj.connect(each_user+self.hostname, username=self.usern, key_filename='craq')
        stdin, stdout, stderr = ssh_obj.exec_command("sudo sed -i 's/host = .*/host = %s/'"%(self.ip_list))
        if handy_node:
            pass #add logic to have handy node details in cases of node failure
        ssh_obj.close()

    def update_ips_server(self):
        for node in self.nodes_list:
            self._update_ips(node)

    def update_ips_client(self):
        self._update_ips(self.client_node)
    
    def setup_nodes(self):
        self.add_setup_obj()
        self.set_headnode()
        self.set_tailnode()
        self.run_servers()
        
    def run_client(write_ops, read_ops, skew_read_ops):
        self.client_node.ssh_obj.connect(node.user+self.hostname, username=self.usern, key_filename='craq')
        stdin, stdout, stderr = ssh_obj.exec_command("python3 client.py --write %s --read %s --skew_read %s"
                                %(write_ops, read_ops, skew_read_ops))
        self.client_node.ssh_obj.close()


def main():
    parser = argparse.ArgumentParser(
                    prog = 'CRAQ',
                    description = 'Parses args through cli')
    parser.add_argument('--users', nargs='+', help = 'nodes')
    parser.add_argument('--ips', nargs='+', help = 'ips')
    parser.add_argument("--setup", action='store_true', help="Sets up nodes")
    parser.add_argument('--write_ops', type=int, default=200)
    parser.add_argument('--read_ops', type=int, default=200)
    parser.add_argument('--skew_read_ops', type=int, default=200)
    args = parser.parse_args()
    craq_obj = craq(args.ips, args.users)
    import pdb; pdb.set_trace()
    if args.setup:
        craq_obj.setup_nodes()
        return
    craq_obj.update_ips_client()
    craq_obj.update_ips_server()
    craq_obj.run_client(args.write_ops, args.read_ops, args.skew_read_ops)

main()