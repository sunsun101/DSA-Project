from tkinter import *
import bellman_ford
import dijkstras_heap
import dijkstras_queue
import data_processing



window = Tk()
window.title("Flight schedular")
# window.configure(background="black")
window.geometry("500x500")


Label(window, text = "Welcome to the Flight Schedular", font=('Times',16)).grid(row=0, column=0, sticky=W)
Label(window, text = "Please choose the algorithm:", font=('Times',12)).grid(row=1, column=0, sticky=W)

output = None

def run():
    if algo == "Dijkstra's-Heap":
        output = dijkstras_heap.main(source, dest, check_var.get())
    elif algo == "Dijkstra's-Queue":
        output = dijkstras_queue.main(source, dest, check_var.get())
    else:
        # print("Check box variable", check_var.get())
        output = bellman_ford.main(source, dest)
    
    shortest_time = output[0][0] if output is not None else 'None'
    transit = output[0][1] if output[0][1] else 'None'
    path = output[0][2] if output[0][2] else 'None'

    label_st.config(text=shortest_time)
    label_transit.config(text=transit)
    label_routes.config(text=path)

    

def get_origin_list():
    global origin_list 
    origin_list = data_processing.get_origins()

def get_destination_list():
    global destination_list 
    destination_list = data_processing.get_destinations()

def set_origin(*args):
    global source 
    source = origin_variable.get()

def set_destination(*args):
    global dest
    dest = destination_variable.get()

def set_algo(*args):
    global algo
    algo = algo_variable.get()


algo_variable = StringVar(window)
algo_variable.trace_add('write', set_algo)
algo_variable.set("Dijkstra's-Heap")

algorithm_list = ["Dijkstra's-Heap", "Dijkstra's-Queue", "Bellman-Ford"]
origin_list = []
destination_list = []

get_origin_list()
get_destination_list()

algo_selector = OptionMenu(window, algo_variable,*algorithm_list)
algo_selector.config(font=('Times',12))
algo_selector.grid(row=1, column=1, sticky=W, pady=5)

Label(window, text = "Origin:", font=('Times',12)).grid(row=2, column=0, sticky=W, pady=5)
origin_variable = StringVar(window)
origin_variable.trace_add('write', set_origin)
origin_variable.set(origin_list[0]) #setting default
origin = OptionMenu(window, origin_variable, *origin_list)
origin.config(font=('Times',12))
origin.grid(row=2, column=1, sticky=W, pady=5)

Label(window, text = "Destination:", font=('Times',12)).grid(row=3, column=0, sticky=W, pady=5)
destination_variable = StringVar(window)
destination_variable.trace_add('write', set_destination)
destination_variable.set(destination_list[0]) #setting default
destination = OptionMenu(window, destination_variable, *destination_list)
destination.config( font=('Times',12))
destination.grid(row=3, column=1, sticky=W, pady=5)

check_var = IntVar()
Checkbutton(window, text="Consider Transit", variable=check_var, onvalue=1, offvalue=0,font=('Times',12)).grid(row=5, column=0, sticky=W, pady=10)

Button(window, text="RUN", width=6, command=run,font=('Times',12)).grid(row=6, column=0, sticky=W, pady=10)


Label(window, text = "Shortest Time (mins):" , font=('Times',12)).grid(row=7, column=0, sticky=W, pady=5)
label_st = Label(window, font=('Times',12))
label_st.grid(row=7, column=1, sticky=W, pady=5)

Label(window, text = "Transit:" , font=('Times',12)).grid(row=8, column=0, sticky=W, pady=5)
label_transit = Label(window, font=('Times',12))
label_transit.grid(row=8, column=1, sticky=W, pady=5)

Label(window, text = "Route" , font=('Times',12)).grid(row=9, column=0, sticky=W, pady=5)
label_routes = Label(window, font=('Times',12))
label_routes.grid(row=9, column=1, sticky=W, pady=5)

window.mainloop()