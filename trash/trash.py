import multiprocessing
import threading
class Sample:
    def __init__(self):
            pass
    def hello(self, pro, vals):
            for val in vals:
                    print('hello from %s:%s'%(pro, val))
    def hi(self, pro, vals):
            for val in vals:
                    print('hi from %s:%s'%(pro, val))
def main():
    client_obj = Sample()
    P1 = threading.Thread(target=client_obj.hello, args=('P1', [1,2,3,4]))
    P2 = threading.Thread(target=client_obj.hello, args=('P2', [5,6,7,8]))
    P1.start()
    P2.start()
    P1.join()
    P2.join()
if __name__ == "__main__": # Here
    main()