from pymavlink import mavutil
import zmq
import time

def initialization(COM, baud, local):
    master = mavutil.mavlink_connection(COM, baud=baud)
    master.wait_heartbeat()
    print("initialized!")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(local)
    
    
    return master, socket

def main():
    BAUD=57600
    COM = '/dev/ttyACM0'
    TCP="tcp:127.0.0.1:5760"
    
    master, socket = initialization(COM ,TCP, baud=BAUD)
    PARAMS = ['OPTICAL_FLOW', 'ATTITUDE']
    msgs = {}
    while True:
        for i in PARAMS: 
            msg = master.recv_match(type=i, blocking=True).to_dict()
            msgs[i] = msg
        print("Sending Drone Params...")
        
        socket.send(msg)
        
        recieved = socket.recv()
        
        print(f"Recieved reply {recieved}")
        time.sleep(0.1)
        
if "__name__" == "__main__":
    main()