from pymavlink import mavutil
import matplotlib.pyplot as plt
import numpy as np
import zmq 
import time

import msgpack

def initialize(COM, baud, udp, local):
    master = mavutil.mavlink_connection(udp)
    if master.wait_heartbeat():
        print("successful connection")
    else:
        print("nothing")
    

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(local)
    print("Bound")

    return master, socket


def get_params(master, socket):
    try:
        message = socket.recv()
        
        
        
        msg = master.recv_match(type=message.decode(), blocking=False).to_dict()

        package = msgpack.packb(msg)
        socket.send(package)
    except Exception as e:
        return e
    


def main():
    DT = 0.5
    BAUD=57600
    COM="/dev/ttyACM0"
    UDP="udp:127.0.0.1:14550"
    LOCAL="tcp://localhost:5555"
    master, socket = initialize(COM, BAUD, UDP, LOCAL)
    
    while True:
        #  Wait for next request from client
        param = get_params(master, socket)
        # print(param)
        
        
        
        
        
        time.sleep(DT)

        #  Do some 'work'
        

if __name__=="__main__":
    main()
    