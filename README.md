CRAQ (Chain Replication with Apportioned Queries)

Background
CR (Chain Replication)
Chain replication is a technique to replicate data across multiple nodes, which are organized in the form of a chain. In chain replication, the servers replicating a given data are linearly ordered to form a chain. The head computes the data once and then forwards it down the chain.
All the write updates propagate down the chain. The tail node handles all read operations, so only values that are committed can be returned by a read.
Since the reads only happen via the tail node, it becomes a bottleneck in the throughput.

Chain in CR
CRAQ(Chain Replication with Apportioned Queries)
CRAQ (Chain Replication with Apportioned Queries), an object storage system that, while maintaining the strong consistency properties of chain replication provides lower latency and higher throughput for read operations.
Here write operations go through the head and propagate through to the tail. In return, tail acknowledges back to the chain back up the chain.
Read operations can happen from any node in the chain which brings significant improvement in the throughput.

Read requests in CRAQ
Working of CRAQ:
Write: Head node receives the write operation from the client. Here the data is marked dirty. Head then propagates the writes through the successors. Once the tail receives the data it marks it as clean and in return, tail sends back acknowledgement backwards through the chain.
Read: Reads can happen on any node in the chain. Each node keeps an identical copy of the data. If a read request is received by a dirtry node then the node contacts tail node to check its state. In return tail node sends back its state which helps in maintaining strong consistency, as read operations are serialised with respect to the tail.

Setup
The original paper implements CRAQ in C++ and zookeeper as a coordination service hence the numbers and results could vary in our implementation.
Currently, the implementation is done in Python. The evaluation is performed on Emulab, a network testbed for researchers, using pc3000 machines on a 100 Mbit network. We are using multithreading to generate clients. Our results could vary compared to the original paper since threading in python has a limitation of running in a concurrent manner because of the global interpreter lock(GIL) and thus threads can’t achieve true parallelism.
We used Thrift to make an RPC connection between client to server and server to server. Each node stores the connection of its predecessor and successor and tail node. We are maintaing a separate node for the health checkup of the server nodes.
Key Results:
CRAQ performed better than CR in terms of read operations since a read can happen from any node unlike CR in which a read operation happens only on the tail node.
In the presence of a lot of state check queries on the tail CRAQ outperforms CR since state check queries are lightweight compared to full read requests.
The read throughput of CRAQ outperformed CR by a factor of the length of the chain. Write operations can get slow due to the length of the chain since every write operation propagates through the chain and acknowledgment comes back from tail to head.
Current Implementation
Framework: We used multithreading to create multiple clients using a single connection. In the original paper, they used multiple connections for every client hence results could vary. For connection apache thrift is used. Around 1500 lines of code are written for server and client nodes.
Server Nodes: Nodes are initialised with thrift connection using socket address of its successor node, previous node, and tail node. Every node keeps data in the form of a key and value. Nodes save all the above connections in memory. The following methods are present in the .thrift file and are exposed to the client.
void write(1:int n1, 2:string n2)
string read(1:int n1)
The head node takes all the write requests which propagate to the chain
We have created similar methods for CR which will run based upon a command line argument. The reads from non tail nodes will not be served.
Client: We have created multiple threads which make request to the server. Read requests can land on any node.
If the data is dirty then the node requests on the tail node and depending upon the state of tail node returns the data as clean or dirty. Client repeatedly makes requests to the server in a multithreaded fashion.
Test Setup:
We ran our experiment on chain lengths 3, 5, and 7. Nodes were running on pc3000 machines with 100MB ran on Ubuntu
Since we had time crunch, we evaluated the performance of read, write, and reads in the presence of write on 3, 5, and 7 node chains in a single-datacenter setup.
Evaluation:
Read throughput: We ran read operations with a varying numbers of clients for 500 and 5k Byte objects. A client is a single connection with multiple threads running in parallel. There is a difference in the output values since the paper creates different connections for every client unlike in our case in which a client is a single connection. In our experiment we varied clients ranging 1–10 using threads. From our observation we found that for CRAQ, the number of reads/sec increased to ~54k while the number of clients incremented to 4. Post that read operations stagnated. While for CR, with varying number of clients read operations were consistent.

Read throughput as the write increases for 500B object
Basic operation throughput: We ran 10 experiments with 10 threads for write and 25 threads for read in each experiment reading 500 Byte objects. Below is the calculated read throughput for CR-3, CRAQ-3 and write throughput for CRAQ-3 Here results could vary because of the tech stack and framework differences.

Read throughput in presence of writes: Write operations are performed by 1 writer thread and 25 reader threads each running for 1 sec. CR has almost the same throughput since all the reads are served by the tail node. CRAQ initially starts with 3 times CR throughput and then eventually downgrades with the increment in the number of writes; writes propagate through the chain and hence use resources in every node. The results correlation are not exactly same but as per the expectation read throughput goes down with varying numbers of writes for CRAQ and CR almost stays constant since all the reads are happening on the tail.

Read throughput in the presence of writes for 500B object

Read throughput in the presence of writes for 5KB object
Summary:
We reproduced the core features of CRAQ in Python. The key results were in proportion to actual paper. Due to framework differences and the way we created the connection the results do not exactly match but they are in portion with the expected results.
Future Scope: Intermittent failure of node, node crash.
References:
https://www.cs.cornell.edu/home/rvr/papers/OSDI04.pdf
https://www.usenix.org/legacy/event/usenix09/tech/full_papers/terrace/terrace.pdf
