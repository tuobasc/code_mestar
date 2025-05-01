from coder import Coder
from src.utils import request, parser_codes

cot_query_prompt = """You are an expert in algorithms and data structures.
Given a competitive programming problem, please generate a detailed plan and python code to solve the problem.
## Problem: 
{problem_desc} 
## Sample Input/Outputs: 
We will test your solution through the following function call.
{samples} 
## Notes:
Please think step by step, make a detailed plan and realize the code. No need to include test code.
Please make sure your code complies with the function call method

Your response must follow the following format:
```python
\"\"\"
Describe your plan here step by step.
\"\"\"
# follow your plan to realize the code step by step.
```
"""

cot_tsp_query = """
You are an expert in algorithms and data structures.
Here is a classic combinatorial optimization problem, the Traveling Salesman Problem (TSP). 
Please implement a heuristic algorithm (better than simple greedy algorithms like nearest neighbour algorithm) to attempt to find the **shortest** possible path that visits all nodes.
Please think step by step, make a detailed plan and then solve the problem.
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

Your response must follow the following format:
```python
\"\"\"
Describe your plan here step by step.
\"\"\"

dataset_path_list = ['data/tsplib-master/att48.json', 'data/tsplib-master/berlin52.json', 'data/tsplib-master/bier127.json', 'data/tsplib-master/burma14.json', 'data/tsplib-master/ch130.json', 'data/tsplib-master/ch150.json', 'data/tsplib-master/d198.json', 'data/tsplib-master/eil101.json', 'data/tsplib-master/eil51.json', 'data/tsplib-master/eil76.json', 'data/tsplib-master/gr137.json', 'data/tsplib-master/gr202.json', 'data/tsplib-master/gr229.json', 'data/tsplib-master/gr96.json', 'data/tsplib-master/kroA100.json', 'data/tsplib-master/kroA150.json', 'data/tsplib-master/kroA200.json', 'data/tsplib-master/kroB100.json', 'data/tsplib-master/kroB150.json', 'data/tsplib-master/kroB200.json', 'data/tsplib-master/kroC100.json', 'data/tsplib-master/kroD100.json', 'data/tsplib-master/kroE100.json', 'data/tsplib-master/lin105.json', 'data/tsplib-master/pr107.json', 'data/tsplib-master/pr124.json', 'data/tsplib-master/pr136.json', 'data/tsplib-master/pr144.json', 'data/tsplib-master/pr152.json', 'data/tsplib-master/pr226.json', 'data/tsplib-master/pr76.json', 'data/tsplib-master/rat195.json', 'data/tsplib-master/rat99.json', 'data/tsplib-master/rd100.json', 'data/tsplib-master/st70.json', 'data/tsplib-master/ts225.json', 'data/tsplib-master/tsp225.json', 'data/tsplib-master/u159.json', 'data/tsplib-master/ulysses16.json', 'data/tsplib-master/ulysses22.json']
# Follow your plan to realize the code step by step.
```
"""

def query_cot(problem_desc, samples, test_samples=None, max_trys=9, model="gpt-4o-mini", verbose=False):
    coder = Coder()
    query = cot_query_prompt.format(problem_desc=problem_desc, samples=samples)
    input_tokens_total = 0
    output_tokens_total = 0
    for _ in range(max_trys):
        res, input_tokens, output_tokens = request(query, model=model, temperature=0.5)
        input_tokens_total += input_tokens
        output_tokens_total += output_tokens
        code = parser_codes(res)
        test_cases_res, exec_res, pass_count = coder.run(code, samples, verbose=verbose) # 在部分测试用例上可以通过则submit
        if pass_count == len(test_cases_res):
            # submit
            if test_samples:
                test_cases_res, exec_res, pass_count = coder.run(code, test_samples, verbose=verbose)
                fitness = pass_count / len(test_cases_res)
                if pass_count == len(test_cases_res):
                    print("Pass through all test cases.")
                    # pass the question
                    return 1, input_tokens_total, output_tokens_total, fitness
                else:
                    return 0, input_tokens_total, output_tokens_total, fitness # fail to pass
            else:
                print("No test samples.")
                print("######## Codes:")
                print(code)
                return 1, input_tokens_total, output_tokens_total, 1

    return 0, input_tokens_total, output_tokens_total, 0 # fail to pass even examples

def tsp_query_cot(dataset_name_list, max_trys=9, model="gpt-4o-mini"):
    file_path_list = []
    for dataset_name in dataset_name_list:
        file_path_list.append(f"data/tsplib-master/{dataset_name}")
    coder = Coder()
    fitness_list = []
    for _ in range(max_trys):
        res, input_tokens, output_tokens = request(cot_tsp_query, temperature=0.5, model=model)
        code = parser_codes(res)
        print(code)
        try:
            fitness = coder.fast_tsp_run(code)
        except Exception as e:
            print(e)
            fitness = 0
        print("fitness: ", fitness)
        fitness_list.append(fitness)
        # exit(0)
    return max(fitness_list)

