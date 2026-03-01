import time
import zmq

def initialize(local):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(local)
    
    return socket

def main():
    LOCAL = "tcp://0.0.0.0:5555"
    
    socket = initialize(LOCAL)
    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)

        #  Do some 'work'
        time.sleep(0.05)

        #  Send reply back to client
        socket.send(b"World")
        
if __name__=="__main__":
    main()
