from types import NoneType

import zmq
from pymavlink import mavutil
import time

def initialize(port, local):
    context = zmq.Context()
    master = mavutil.mavlink_connection(port)
    if master.wait_heartbeat():
        print("Connection successful")
    
    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect(local)
    
    return master, socket

def fetch_params(master, params, values):
    
    vals = []
    try:
        for i in range(len(params)):
            msg = master.recv_match(type=params[i], blocking=True).to_dict()
            vals.append(str(msg[values[i]]))
            # print(msg)
                
        return vals
    except:
        return["unable to fetch params"]

        

    
# def fetch_values(msgs, params, values):
#     vals = []
#     for i in range(len(params)):
#         vals.append(msgs[params][values])
#     return vals

def main():
    TCP = "tcp://0.0.0.0:5555"
    UDP = "udp:127.0.0.1:14550"
    PARAMS=["ATTITUDE", ]
    VALS=["yaw", "roll"]
    master, socket = initialize(UDP, TCP)
    print("initialization complete")
    while True:
        values = fetch_params(master, PARAMS, VALS)
        print(values)
        # for i in range(len(values)):
        #     string = str(VALS[i]) + ":" + " " + values[i]
        #     socket.send(string.encode("utf-8"))
        #     print("Sending request")
        
        

        #  Get the reply.
        message = socket.recv()
        
if __name__=="__main__":
    main()