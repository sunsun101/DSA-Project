import pandas as pd
from sys import maxsize, path
import numpy as np
from datetime import datetime
import sys

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

import math

output_list = []
shortest_path = ""

def getPath(parent, vertex):
    if vertex < 0:
        return []
    return getPath(parent, parent[vertex]) + [vertex]


def printPathAndTransit(parent, j, count, departure, arrival, transit):
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
        # output_list.append(None)
        if count == 0:
            count += 1
        else:
            count += 1
            arrival = datetime.strptime(j[1], "%H:%M")
            tt = departure - arrival
            transit += ((tt.seconds // 3600) * 60) + (tt.seconds // 60) % 60
            departure = datetime.strptime(j[2], "%H:%M")
        printPathAndTransit(parent, parent[j[0]], count, departure, arrival, transit)
        print(dicts2[j[0]], end="-")
        shortest_path = shortest_path + dicts2[j[0]] + "-"
    else:
        if parent[j] == -1:
            print(dicts2[j], end="-")
            shortest_path = shortest_path + dicts2[j] + "-"
            output_list.append(None)
            return
        departure = datetime.strptime(parent[j][2], "%H:%M")
        printPathAndTransit(parent, parent[j], count, departure, arrival, transit)
        print(dicts2[j], end="-")
        shortest_path = shortest_path + dicts2[j] + "-"
        print()
        print()


def BellmanFord(graph, vertices, edges, source, dest):
    vertices_dict = {}
    for v in vertices:
        vertices_dict[v] = math.inf
    print(len(vertices))
    parent = [-1] * len(vertices)
    ArrAndDep = [-1] * len(vertices)
    vertices_dict[source] = 0

    for i in range(len(vertices) - 1):
        for j in range(edges):
            if (
                vertices_dict[graph[j][0]] + float(graph[j][2])
                < vertices_dict[graph[j][1]]
            ):
                vertices_dict[graph[j][1]] = vertices_dict[graph[j][0]] + float(
                    graph[j][2]
                )
                parent[dicts[graph[j][1]]] = dicts[graph[j][0]]
                ArrAndDep[dicts[graph[j][1]]] = [
                    dicts[graph[j][0]],
                    graph[j][3],
                    graph[j][4],
                ]

    for i in range(edges):
        x = graph[i][0]
        y = graph[i][1]
        weight = float(graph[i][2])
        if vertices_dict[x] != math.inf and (
            vertices_dict[x] + weight < vertices_dict[y]
        ):
            print("Graph contains negative weight cycle")

    print("Shortest Distance from", source)
    for val in vertices:
        global shortest_path
        shortest_path = ""
        transit = 0
        departure = 0
        arrival = 0
        count = 0
        if dest != "":
            if val == dest:
                print("%s\t--->\t%s\t%.2f" % (source, val, vertices_dict[val]))
                output_list.append(vertices_dict[val])
                printPathAndTransit(
                    ArrAndDep, dicts[val], count, departure, arrival, transit
                )
                # print("The appended shortest path is", shortest_path)
                output_list.append(shortest_path)
                print()
        else:
            output_list.append(vertices_dict[val])
            print("%s\t--->\t%s\t%.2f" % (source, val, vertices_dict[val]))
            printPathAndTransit(
                ArrAndDep, dicts[val], count, departure, arrival, transit
            )
            # print("The appended shortest path is", shortest_path)
            output_list.append(shortest_path)
            print()
            print()


class Graph:
    def __init__(self, source, destination, timeTaken, arrivalTime, DepartureTime):
        self.graph = np.column_stack(
            (source, destination, timeTaken, arrivalTime, DepartureTime)
        )


def main(origin, dest):
    global output_list
    output_list = []
    keys = range(len(unique))

    global dicts
    dicts = dict(zip(unique, keys))
    global dicts2
    dicts2 = dict(zip(keys, unique))
    vertices = unique
    edges_count = len(data.index)

    g = Graph(
        data["origin"].to_list(),
        data["destination"].to_list(),
        data["timeTaken"],
        data["scheduledArrivalTime"],
        data["scheduledDepartureTime"],
    )
    BellmanFord(g.graph, vertices, edges_count, origin, dest)
    output = np.array(output_list).reshape(-1, 3)
    print("output is", output)
    return output


if __name__ == "__main__":
    main("Guwahati", "Bhubaneswar")
