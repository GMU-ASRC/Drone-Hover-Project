import matplotlib.pyplot as plt
import time

# Create the figure and axis once
fig, ax = plt.subplots()
hl, = ax.plot([], [], 'o-') # 'o-' adds dots at the data points

# Set limits so the window doesn't start at (0,0)
ax.set_xlim(0, 5)
ax.set_ylim(0, 25)

t_data = [1, 2, 3, 4]
x_data = [5, 10, 15, 20]

def update_line(new_t, new_x):
    # Get current data, add new data, and update the line
    curr_t = list(hl.get_xdata())
    curr_x = list(hl.get_ydata())
    
    curr_t.append(new_t)
    curr_x.append(new_x)
    
    hl.set_xdata(curr_t)
    hl.set_ydata(curr_x)
    
    # This is what forces the window to actually "paint" the update
    plt.draw()
    plt.pause(0.1) 

def main():
    
    for i in range(len(x_data)):
        update_line(t_data[i], x_data[i])
        time.sleep(1)
    
    # Keeps the window open after the loop finishes
    plt.show(block=True)

if __name__ == "__main__":
    main()