import argparse
from cot import tsp_query_cot
from greedy import tsp_query_greedy
from query import query_code_master
from src.utils import find_tsp_files

parser = argparse.ArgumentParser()
parser.add_argument('--method', type=str, default="code-master", choices=["greedy", "code-master", "cot"],help='the method to use')
parser.add_argument('--model', type=str, default="gpt-4o-mini", choices=["gpt-4o-mini", "deepseek-r1", "gpt-4o"], help='api model')
parser.add_argument("--max_trys", type=int, default=9, help="max number of tries")
args = parser.parse_args()

problem_desc= """This is a classic combinatorial optimization problem, the Traveling Salesman Problem (TSP). 
Please implement a heuristic algorithm (better than simple greedy algorithms like nearest neighbour algorithm) to attempt to find the shortest possible path that visits all nodes.

You should load the dataset, which contains the node IDs (starting from 1) and their corresponding coordinates.
An example of the data is:

```json
{{"1": [6734.0, 1453.0], "2": [2233.0, 10.0], "3": [5530.0, 1424.0], "4": [401.0, 841.0]}}
```

## Notes
Your result should be several lists indicating the order in which we should traverse the nodes, such as ["1", "3", "2", "4"]. 
Save your result dict to a file named "tmp_result.json" in the current folder.

```json
{{
    "att48": ["1", "3", "4", "1"],
    "berlin52": ["1", "3", "2"],
    ......
}}
```

The datasets you need to compute are shown as follow:
```python
dataset_path_list = ['data/tsplib-master/att48.json', 'data/tsplib-master/berlin52.json', 'data/tsplib-master/bier127.json', 'data/tsplib-master/burma14.json', 'data/tsplib-master/ch130.json', 'data/tsplib-master/ch150.json', 'data/tsplib-master/d198.json', 'data/tsplib-master/eil101.json', 'data/tsplib-master/eil51.json', 'data/tsplib-master/eil76.json', 'data/tsplib-master/gr137.json', 'data/tsplib-master/gr202.json', 'data/tsplib-master/gr229.json', 'data/tsplib-master/gr96.json', 'data/tsplib-master/kroA100.json', 'data/tsplib-master/kroA150.json', 'data/tsplib-master/kroA200.json', 'data/tsplib-master/kroB100.json', 'data/tsplib-master/kroB150.json', 'data/tsplib-master/kroB200.json', 'data/tsplib-master/kroC100.json', 'data/tsplib-master/kroD100.json', 'data/tsplib-master/kroE100.json', 'data/tsplib-master/lin105.json', 'data/tsplib-master/pr107.json', 'data/tsplib-master/pr124.json', 'data/tsplib-master/pr136.json', 'data/tsplib-master/pr144.json', 'data/tsplib-master/pr152.json', 'data/tsplib-master/pr226.json', 'data/tsplib-master/pr76.json', 'data/tsplib-master/rat195.json', 'data/tsplib-master/rat99.json', 'data/tsplib-master/rd100.json', 'data/tsplib-master/st70.json', 'data/tsplib-master/ts225.json', 'data/tsplib-master/tsp225.json', 'data/tsplib-master/u159.json', 'data/tsplib-master/ulysses16.json', 'data/tsplib-master/ulysses22.json']
```
"""

def main():
    dataset_names = find_tsp_files("data/tsplib-master")
    if args.method == "greedy":
        fitness = tsp_query_greedy(dataset_names, max_trys=9, model=args.model)
        print("Best Fitness:", fitness)
    elif args.method == "cot":
        fitness = tsp_query_cot(dataset_names, max_trys=9, model=args.model)
        print("Best Fitness:", fitness)
    elif args.method == "code-master":
        query_code_master(problem_desc, model=args.model, optimization=True, verbose=True)

if __name__ == '__main__':
    main()