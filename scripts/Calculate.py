import matplotlib.pyplot as plt
import numpy
import time
import zmq
import msgpack

def initialize(local):
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    if socket.bind(local):
        print("connected")


    return socket

def get_vectors(socket):
    try:
        vectors = socket.recv()

        message = "recieved"
        socket.send(message.encode())
    except Exception as e:
        return None
    
    print(vectors)
def main():
    LOCAL="tcp://localhost:5000"
    socket = initialize(LOCAL)
    while True:
        message = get_vectors(socket)
        print(message)
        if message:
            break
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()


   