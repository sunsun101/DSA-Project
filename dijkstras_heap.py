import pandas as pd
from collections import defaultdict
import numpy as np
import time
from datetime import datetime
import math

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
output_list = []
shortest_path = ""


class Heap:
    def __init__(self):
        self.array = []
        self.size = 0
        self.pos = []

    def newMinHeapNode(self, v, dist):
        minHeapNode = [v, dist]
        return minHeapNode

    def swapMinHeapNode(self, a, b):
        t = self.array[a]
        self.array[a] = self.array[b]
        self.array[b] = t

    def minHeapify(self, idx):
        smallest = idx
        left = 2 * idx + 1
        right = 2 * idx + 2

        if left < self.size and self.array[left][1] < self.array[smallest][1]:
            smallest = left

        if right < self.size and self.array[right][1] < self.array[smallest][1]:
            smallest = right

        if smallest != idx:
            self.pos[self.array[smallest][0]] = idx
            self.pos[self.array[idx][0]] = smallest
            self.swapMinHeapNode(smallest, idx)

            self.minHeapify(smallest)

    def extractMin(self):

        if self.isEmpty() == True:
            return

        root = self.array[0]
        lastNode = self.array[self.size - 1]
        self.array[0] = lastNode
        self.pos[lastNode[0]] = 0
        self.pos[root[0]] = self.size - 1
        self.size -= 1
        self.minHeapify(0)

        return root

    def isEmpty(self):
        return True if self.size == 0 else False

    def decreaseKey(self, v, dist):

        i = self.pos[v]
        self.array[i][1] = dist

        while i > 0 and self.array[i][1] < self.array[(i - 1) // 2][1]:

            # Swap this node with its parent
            self.pos[self.array[i][0]] = (i - 1) // 2
            self.pos[self.array[(i - 1) // 2][0]] = i
            self.swapMinHeapNode(i, (i - 1) // 2)

            # move to parent index
            i = (i - 1) // 2

    def isInMinHeap(self, v):

        if self.pos[v] < self.size:
            return True
        return False


class Graph:
    def __init__(self, Vert):
        self.Vertices = Vert
        self.graph = defaultdict(list)
        self.ttransit = 0

    def addVertex(self, src, dest, weight, arrT, depT):
        newNode = [dest, weight, arrT, depT]
        self.graph[src].insert(0, newNode)

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
            shortest_path = shortest_path + dicts2[j] + "-"
            print(dicts2[j], end="-")

    def getSchedule(self, src, dist, parent, dest):
        for i in range(1, len(dist)):
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

    def dijkstra(self, src, dest):

        Vert = self.Vertices
        dist = []

        minHeap = Heap()
        parent = [-1] * Vert
        ArrAndDep = [-1] * Vert

        for v in range(Vert):
            dist.append(math.inf)
            minHeap.array.append(minHeap.newMinHeapNode(v, dist[v]))
            minHeap.pos.append(v)

        minHeap.pos[src] = src
        dist[src] = 0
        minHeap.decreaseKey(src, dist[src])

        minHeap.size = Vert
        while minHeap.isEmpty() == False:

            newHeapNode = minHeap.extractMin()
            u = newHeapNode[0]

            for adj in self.graph[u]:

                v = adj[0]

                if includeTransit:
                    transit = 0
                    departure = 0
                    arrival = 0
                    count = 0
                    self.AddWeightToTransit(
                        ArrAndDep, v, count, departure, arrival, transit
                    )
                    weightTransit = adj[1] + self.ttransit
                else:
                    weightTransit = adj[1]
                if (
                    minHeap.isInMinHeap(v)
                    and weightTransit + dist[u] < dist[v]
                    and dist[u] != math.inf
                ):
                    parent[v] = u
                    ArrAndDep[v] = [u, adj[2], adj[3]]
                    dist[v] = adj[1] + dist[u]

                    minHeap.decreaseKey(v, dist[v])

        self.getSchedule(src, dist, ArrAndDep, dest)

dicts2 = {}
dicts = {}
includeTransit = True
def main(source, destination, transit):
    global dicts
    global dicts2
    global includeTransit
    global output_list
    output_list = []
    keys = range(len(unique))

    dicts = dict(zip(unique, keys))
    dicts2 = dict(zip(keys, unique))

    graph = Graph(len(unique))

    origin = source
    destination = destination

    includeTransit = transit

    for key in dicts:
        adjacent = data.loc[
            data["origin"] == key,
            ["destination", "timeTaken", "scheduledArrivalTime", "scheduledDepartureTime"],
        ].values
        if key == origin:
            print(adjacent)
        for x in adjacent:
            graph.addVertex(dicts[key], dicts[x[0]], x[1], x[2], x[3])


    start = time.time()
    graph.dijkstra(dicts[origin], destination)
    end = time.time()
    elapsedTime = end - start
    print("elapsedTime: ", elapsedTime)
    output = np.array(output_list).reshape(-1, 3)
    print("output is", output)
    return output

if __name__ == "__main__":
    main("Guwahati", "", True)
