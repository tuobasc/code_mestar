import argparse

from cot import tsp_query_cot
from greedy import tsp_query_greedy
from src.utils import find_tsp_files

parser = argparse.ArgumentParser()
parser.add_argument('--method', type=str, default="cot", choices=["greedy", "code-master", "cot"],help='the method to use')
parser.add_argument('--model', type=str, default="gpt-4o-mini", choices=["gpt-4o-mini", "deepseek-r1", "gpt-4o"], help='api model')
parser.add_argument("--max_trys", type=int, default=9, help="max number of tries")
args = parser.parse_args()

def main():
    dataset_names = find_tsp_files("data/tsplib-master")
    if args.method == "greedy":
        fitness = tsp_query_greedy(dataset_names, max_trys=9, model=args.model)
        print("Best Fitness:", fitness)
    elif args.method == "cot":
        fitness = tsp_query_cot(dataset_names, max_trys=9, model=args.model)
        print("Best Fitness:", fitness)
    else:
        pass

if __name__ == '__main__':
    main()