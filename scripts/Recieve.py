import zmq
import time
import msgpack
import matplotlib.pyplot as plt
import numpy as np

def initialize(local, local2):
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect(local)

    socket2 = context.socket(zmq.REQ)
    socket2.connect(local2)

    return socket, socket2
def launch_graph(num_values):
    vect_lst = []
    plt.ion()
    fig, ax = plt.subplots()
    for i in range(num_values):
        vect_lst.append(ax.plot([], []))
    return fig, ax, vect_lst

def fetch_params(socket, params):
    socket.send(params.encode("utf-8"))

    print(f"Requesting {params}")
    message = socket.recv()

    return msgpack.unpackb(message, raw=False)
        
def get_values(message, value):
    try:
        return message[value]
    except KeyError as error:
        return None
    
def init_timestamps(num):
    stamps = []
    for i in range(num):
        stamps.append([])
    return stamps

def send_vectors(socket2, ax):
    vect = ax.get_lines()
    for i in range(len(vect)):
        timestamp = list(vect[i].get_xdata())
        val = list(vect[i].get_ydata())
        print(timestamp)
        t = msgpack.packb(timestamp)
        val = msgpack.packb(val)
        socket2.send(val)
        
        time.sleep(1)

        
        message = socket2.recv()

        print(message)

def update_list(vect, values, cur_time, ax, fig, stamps):
    vect[0].set_xdata(np.append(vect[0].get_xdata(), cur_time))
    vect[0].set_ydata(np.append(vect[0].get_ydata(), values))
    stamps.append(cur_time)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()

def main():
    DT = 0.5
    timestep = 0
    PARAMS=["GPS_RAW_INT", "GPS_RAW_INT"]
    Values=["alt", "lat"]
    LOCAL="tcp://localhost:5555"
    LOCAL2="tcp://localhost:5000"
    socket, socket2 = initialize(LOCAL, LOCAL2)
    # print(len(PARAMS))
    fig, ax, vect_lst = launch_graph(len(PARAMS))
    print(len(vect_lst))
    stamps = init_timestamps(len(Values))


    while timestep < 5:
        cur_time = time.time()
        for i in range(len(PARAMS)):
            message = fetch_params(socket, PARAMS[i])
            values = get_values(message, Values[i])
            update_list(vect_lst[i], values, cur_time, ax, fig, stamps[i])
            print(f"time : {stamps[i][-1]}")
            print(f"{Values[i]}:{values}")
            
        timestep += DT
        print(timestep)
        time.sleep(DT)
        
    send_vectors(socket2, ax)

    
if __name__=="__main__":
    main()
    

