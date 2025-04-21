import argparse
import json
import math
from src.tsp_file_parser import TSPParser
import os

def find_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if "tsp" in file:
                file_list.append(os.path.join(root, file))
    return file_list

def parse_boolean(value: str) -> bool:
    value = value.lower()

    if value in ["true", "yes", "y", "1", "t"]:
        return True
    elif value in ["false", "no", "n", "0", "f"]:
        return False

    return False


def calculate_distance(node1, node2):
    """计算两个节点之间的欧式距离"""
    x1, y1 = node1
    x2, y2 = node2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def greedy_tsp(node_data):
    """使用最近邻贪心算法求解TSP"""
    nodes = list(node_data.keys())
    start_node = nodes[0]
    unvisited = set(nodes)
    unvisited.remove(start_node)
    current_node = start_node
    tour = [current_node]

    while unvisited:
        next_node = min(unvisited, key=lambda x: calculate_distance(node_data[current_node], node_data[x]))
        unvisited.remove(next_node)
        tour.append(next_node)
        current_node = next_node

    return tour

def calculate_tour_length(tour, node_data):
    """计算给定路径的长度"""
    total_length = 0.0
    for i in range(len(tour)):
        current_node = tour[i]
        next_node = tour[(i + 1) % len(tour)]
        total_length += calculate_distance(node_data[current_node], node_data[next_node])
    return total_length


if __name__ == '__main__':
    # file_names = find_files("data/tsplib-master")
    # should_plot = False
    # for file_name in file_names:
    #     try:
    #         p = TSPParser(filename=str(file_name), plot_tsp=should_plot)
    #         saved_file_name = file_name.split(".")[0] + ".json"
    #         with open(saved_file_name, "w") as f:
    #             json.dump(p.tsp_cities_dict, f)
    #     except Exception as e:
    #         pass

    res = {}
    with open("data/tsplib-master/solutions.txt", "r") as file:
        for line in file:
            dataset = line.strip().split(":")[0].strip()
            best = line.strip().split(":")[1].strip()
            res[dataset] = int(best)

    with open("data/tsplib-master/solutions.json", "w") as f:
        json.dump(res, f)