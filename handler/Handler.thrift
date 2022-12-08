namespace py Handler

typedef i32 int 
service Handler{
    
    int write(1:int n1, 2:int n2)
    int ack(1:int n1)
    int writeSuccessor(1:int n1, 2:int n2)
     
    
}