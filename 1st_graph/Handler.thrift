namespace py Handler

typedef i32 int 
service Handler{
    
    void write(1:int n1, 2:string n2)
    void write_cr(1:int n1, 2:string n2)
    void ack(1:int n1)
    void writeSuccessor(1:int n1, 2:string n2)
    void set_node_connections(1:int n1)
    string read(1:int n1)
    int readTail(1:int n1)
    int checkDirtybit(1:int n1) 
}