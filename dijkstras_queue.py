import pandas as pd
from collections import defaultdict
import sys
from datetime import datetime
import numpy as np
import time
import pprint
import math

# import queue

data = pd.read_csv("Flight_Schedule_without_missing.csv")
data = data.drop(["dayOfWeek", "validFrom", "validTo"], axis=1)
data.drop(data[data["airline"] != "GoAir"].index, inplace=True)
data = data.dropna()
data = data.drop_duplicates(subset=["origin", "destination"], keep="last")
data.reset_index(drop=True, inplace=True)

arr = pd.to_datetime(data["scheduledArrivalTime"], format="%H:%M")
dep = pd.to_datetime(data["scheduledDepartureTime"], format="%H:%M")

diff = arr - dep
data["timeTaken"] = (diff.dt.components["hours"] * 60) + diff.dt.components["minutes"]

unique = pd.unique(data[["origin", "destination"]].values.ravel("K"))

dicts2 = {}
dicts = {}
includeTransit = True

output_list = []
shortest_path = ""


class Graph:
    def __init__(self):
        self.ttransit = 0

    def extractMin(self, dist, queue):
        minn = math.inf
        initial = -1

        for i in range(len(dist)):
            if dist[i] < minn and i in queue:
                minn = dist[i]
                initial = i
        return initial

    def printPathAndTransit(self, parent, j, count, departure, arrival, transit):
        global shortest_path
        check = isinstance(j, list)
        if check:
            if parent[j[0]] == -1:
                arrival = datetime.strptime(j[1], "%H:%M")
                if count != 0 and departure != 0:
                    tt = departure - arrival
                    transit = (
                        transit + ((tt.seconds // 3600) * 60) + (tt.seconds // 60) % 60
                    )
                    print("Total transit time: ", transit)
                    output_list.append(transit)
                else:
                    output_list.append(None)
                print(dicts2[j[0]], end="-")
                shortest_path = shortest_path + dicts2[j[0]] + "-"
                return transit
            if count == 0:
                count += 1
            else:
                count += 1
                arrival = datetime.strptime(j[1], "%H:%M")
                tt = departure - arrival
                transit += ((tt.seconds // 3600) * 60) + (tt.seconds // 60) % 60
                departure = datetime.strptime(j[2], "%H:%M")
            self.printPathAndTransit(
                parent, parent[j[0]], count, departure, arrival, transit
            )
            print(dicts2[j[0]], end="-")
            shortest_path = shortest_path + dicts2[j[0]] + "-"
        else:
            if parent[j] == -1:
                print(dicts2[j], end="-")
                shortest_path = shortest_path + dicts2[j] + "-"
                output_list.append(None)
                return
            departure = datetime.strptime(parent[j][2], "%H:%M")
            self.printPathAndTransit(
                parent, parent[j], count, departure, arrival, transit
            )
            print(dicts2[j], end="-")
            shortest_path = shortest_path + dicts2[j] + "-"

    def AddWeightToTransit(self, parent, j, count, departure, arrival, transit):
        check = isinstance(j, list)
        if check:
            if parent[j[0]] == -1:
                arrival = datetime.strptime(j[1], "%H:%M")
                if count != 0 and departure != 0:
                    tt = departure - arrival
                    transit = (
                        transit + ((tt.seconds // 3600) * 60) + (tt.seconds // 60) % 60
                    )
                    self.ttransit = transit
                    transit = 0
                    departure = 0
                    arrival = 0
                    count = 0
                return
            if count == 0:
                count += 1
            else:
                count += 1
                arrival = datetime.strptime(j[1], "%H:%M")
                tt = departure - arrival
                transit += ((tt.seconds // 3600) * 60) + (tt.seconds // 60) % 60
                departure = datetime.strptime(j[2], "%H:%M")
            self.AddWeightToTransit(
                parent, parent[j[0]], count, departure, arrival, transit
            )
        else:
            if parent[j] == -1:
                return
            departure = datetime.strptime(parent[j][2], "%H:%M")
            self.AddWeightToTransit(
                parent, parent[j], count, departure, arrival, transit
            )

    def getSchedule(self, src, dist, parent, dest):
        for i in range(0, len(dist)):
            global shortest_path
            shortest_path = ""
            if dest != "":
                if dicts[dest] == i:
                    transit = 0
                    departure = 0
                    arrival = 0
                    count = 0
                    output_list.append(dist[i])
                    print(
                        "\n%s --> %s \t\t%.2f \t\t\t\t\t"
                        % (dicts2[src], dicts2[i], dist[i])
                    ),
                    self.printPathAndTransit(
                        parent, i, count, departure, arrival, transit
                    )
                    output_list.append(shortest_path)
            else:
                transit = 0
                departure = 0
                arrival = 0
                count = 0
                output_list.append(dist[i])
                print(
                    "\n%s --> %s \t\t%.2f \t\t\t\t\t"
                    % (dicts2[src], dicts2[i], dist[i])
                ),
                self.printPathAndTransit(parent, i, count, departure, arrival, transit)
                output_list.append(shortest_path)
                print()

    def dijkstra(self, graph, src, dest):

        vert = len(graph)

        dist = [math.inf] * vert

        parent = [-1] * vert  # parent stores path
        ArrAndDep = [-1] * vert

        dist[src] = 0  # Distance of source always 0

        queue = []
        #         q = queue.PriorityQueue()
        for v in range(vert):
            #             print(i)
            #             q.put(i)
            queue.append(v)  # Add all vertices in queue

        weightTransit = 0
        while queue:

            u = self.extractMin(dist, queue)
            #             u = q.get()

            if u == -1:
                break

            queue.remove(u)

            for v in range(vert):
                if graph[u][v][0] and v in queue:
                    if includeTransit:
                        transit = 0
                        departure = 0
                        arrival = 0
                        count = 0
                        self.AddWeightToTransit(
                            ArrAndDep, v, count, departure, arrival, transit
                        )
                        weightTransit = graph[u][v][0] + self.ttransit
                    else:
                        weightTransit = graph[u][v][0]
                    if dist[u] + weightTransit < dist[v]:
                        dist[v] = dist[u] + graph[u][v][0]
                        #                         q.put(u)
                        parent[v] = u
                        ArrAndDep[v] = [u, graph[u][v][1], graph[u][v][2]]

        self.getSchedule(src, dist, ArrAndDep, dest)

def main(source, destination, transit):
    # vertices = []
    # airports = []
    # path = []
    global dicts
    global dicts2
    global includeTransit
    global output_list
    output_list = []

    keys = range(len(unique))

    dicts = dict(zip(unique, keys))
    dicts2 = dict(zip(keys, unique))

    n = len(unique)
    graph = [[[0 for k in range(3)] for j in range(n)] for i in range(n)]

    origin = source
    destination = destination
    includeTransit = transit
    g = Graph()
    for key in dicts:

        adjacent = data.loc[
            data["origin"] == key,
            ["destination", "timeTaken", "scheduledArrivalTime", "scheduledDepartureTime"],
        ].values

        for x in adjacent:
            graph[dicts[key]][dicts[x[0]]] = [x[1], x[2], x[3]]
    # print(graph)
    start = time.time()
    g.dijkstra(graph, dicts[origin], destination)
    end = time.time()
    elapsedTime = end - start
    print()
    print("elapsedTime: ", elapsedTime)
    output = np.array(output_list).reshape(-1, 3)
    print("output is", output)
    return output

if __name__ == "__main__":
    main("Guwahati", "", True)
