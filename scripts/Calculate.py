from statistics import correlation

import matplotlib.pyplot as plt
import numpy as np
import time
import zmq
import msgpack

def initialize(local):
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REP)
    socket.bind(local)



    return socket

def separate_values(vectors, timestamps, values):
    
    timestamps.append(vectors[0])
    values.append(vectors[1])
    
def get_correlation(timestamps, values):
    v0 = (values[0] - np.mean(values[0])) / np.std(values[0])
    v1 = (values[1] - np.mean(values[1])) / np.std(values[1])
    correlation = np.correlate(v0, v1, mode='full')
    correlation /= len(v0)  # normalize by length
    return correlation
    

def get_num_params(socket):
    num_params = socket.recv()
    msg = "thx"
    
    
    socket.send(msg.encode())
    
    return msgpack.unpackb(num_params)


def get_vectors(socket):
    try:
        vector = socket.recv()
        
        
        
        msg = "thank you"

        vector = msgpack.unpackb(vector)
        socket.send(msg.encode())
        
        return vector
        
    except Exception as e:
        return None
    
    
def main():
    LOCAL="tcp://0.0.0.0:5000"
    socket = initialize(LOCAL)
    timestamps = []
    values = []
    num_params = get_num_params(socket)
    n=0
    vectors = []
    while n < num_params:
        # print(timestamps)
        message = get_vectors(socket)
        # print(message)
        
        
        separate_values(message, timestamps, values)
        # print(timestamps)
        # print(values)
        # if len(timestamps) == num_params:
        #     break
        n+=1
        time.sleep(0.1)
        
        
    correlation= get_correlation(timestamps, values)
    print(correlation)
    x = np.arange(0, len(correlation))
    plt.plot(x, correlation)
    plt.show()
        
        # time.sleep(0.5)

if __name__ == "__main__":
    main()


