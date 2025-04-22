import argparse
import json
import os

from mapcoder import query_mapcoder
from preprocess import load_dataset
from tqdm import tqdm
from query import query_code_master
from greedy import query_greedy

parser = argparse.ArgumentParser()
parser.add_argument('--dataset_name', type=str, default="APPS", help='the name of dataset')
parser.add_argument('--split_test_ratio', type=float, default=0.9, help='the ratio of test instances')
parser.add_argument('--method', type=str, default="greedy", choices=["greedy", "code-master", "cot"],help='the method to use')
parser.add_argument('--model', type=str, default="gpt-4o-mini", choices=["gpt-4o-mini", "deepseek-r1", "gpt-4o"], help='api model')
parser.add_argument('--counterfactual_think', action="store_true", help='if think before plan')
parser.add_argument('--verbose', action="store_true", help='verbose on')
parser.add_argument('--greedy_search_iterations', type=int, default=3, help='code master max debug times')
parser.add_argument('--evolution_iterations', type=int, default=3, help='code master max evolution times')


# 解析参数
args = parser.parse_args()

# todo: 查找一下不同model的cost
if args.model == "gpt-4o-mini":
    input_token_cost = 0.00000116
    output_token_cost = 0.00000466
elif args.model == "deepseek-r1":
    input_token_cost = 0.00000055
    output_token_cost = 0.00000219
elif args.model == "gpt-4o":
    input_token_cost = 0.00001941
    output_token_cost = 0.00007764

def main():
    if "HumanEvalET" in args.dataset_name or "MBPP_ET" in args.dataset_name:
        with open(f"data/{args.dataset_name}_preprocessed.json", "r") as f:
            problems = json.load(f)
            data = []
            for problem in problems:
                if not problem["instances"]:
                    print("Warning: Drop an unsatisfied problem")
                    continue
                meta_data = dict()
                meta_data["problem_description"] = problem["problem_description"]
                saved_samples_length = int((1 - args.split_test_ratio) * len(problem["instances"])) if int((1 - args.split_test_ratio) * len(problem["instances"])) else 1
                meta_data["examples"] = problem["instances"][:saved_samples_length]
                meta_data["test_examples"] = problem["instances"][saved_samples_length:]
                data.append(meta_data)
    elif "APP" in args.dataset_name:
        problems = load_dataset("data/APPS_selected150.jsonl", args.split_test_ratio)
        # Drop the problem with too long context
        data = []
        for problem in problems:
            if len(problem["problem_description"].split(" ")) >= 20000:
                print("Warning: Drop an unsatisfied problem")
                continue
            else:
                data.append(problem)
    else:
        raise RuntimeError

    print("Dataset problems: {}".format(len(data)))
    if args.method == "code-master":
        pass_count = 0
        input_tokens_total = 0
        output_tokens_total = 0
        fitness_list = []
        for i, problem in tqdm(enumerate(data), total=len(data), desc="Running code-master with model {}".format(args.model)):
            problem_desc = problem["problem_description"]
            examples = problem["examples"]
            test_examples = problem["test_examples"] # true test_cases
            rerun = True
            for j in range(4):
                if rerun:
                    print("rerun:",  rerun)
                    try:
                        success, input_tokens, output_tokens, fitness = query_code_master(problem_desc=problem_desc, samples=examples, test_samples=test_examples,
                                      counterfactual_thinking=args.counterfactual_think,
                                      greedy_search_iterations=args.greedy_search_iterations,
                                      evolution_iterations=args.evolution_iterations,
                                      model=args.model, verbose=args.verbose)
                        rerun = False
                        pass_count += success
                        fitness_list.append(fitness)
                        input_tokens_total += input_tokens
                        output_tokens_total += output_tokens
                    except Exception as e:
                        print(e)
                if j == 3 and rerun:
                    fitness_list.append(0)
                    input_tokens_total += int(input_tokens_total / (i + 1))
                    output_tokens_total += int(output_tokens_total / (i + 1))
        pass_rate = pass_count / len(data)
        avg_input_tokens = input_tokens_total / len(data)
        avg_output_tokens = output_tokens_total / len(data)
        print(f"pass_rate: {pass_rate}")
        print(f"avg input token: {avg_input_tokens}")
        print(f"avg output token: {avg_output_tokens}")
        print(f"avg problem cost: {avg_input_tokens * input_token_cost + avg_output_tokens * output_token_cost}")
        print(f"fitness: {sum(fitness_list) / len(fitness_list)}")

    elif args.method == "greedy":
        max_trys = args.greedy_search_iterations * args.evolution_iterations # to compare fairly
        input_tokens_total = 0
        output_tokens_total = 0
        pass_count = 0
        fitness_list = []
        for i, problem in tqdm(enumerate(data), total=len(data), desc="Running greedy method with model {}".format(args.model)):
            problem_desc = problem["problem_description"]
            examples = problem["examples"]
            test_examples = problem["test_examples"]  # true test_cases
            rerun = True
            for j in range(4):
                if rerun:
                    try:
                        res, input_tokens, output_tokens, fitness = query_greedy(problem_desc=problem_desc, samples=examples, test_samples=test_examples, max_trys=max_trys, model=args.model)
                        pass_count += res
                        input_tokens_total += input_tokens
                        output_tokens_total += output_tokens
                        fitness_list.append(fitness)
                    except Exception as e:
                        print(e)
                if j == 3 and rerun:
                    fitness_list.append(0)
                    input_tokens_total += int(input_tokens_total / (i+1))
                    output_tokens_total += int(output_tokens_total / (i+1))

        pass_rate = pass_count / len(data)
        avg_input_tokens = input_tokens_total / len(data)
        avg_output_tokens = output_tokens_total / len(data)
        print(f"pass_rate: {pass_rate}")
        print(f"avg input token: {avg_input_tokens}")
        print(f"avg output token: {avg_output_tokens}")
        print(f"avg problem cost: {avg_input_tokens * input_token_cost + avg_output_tokens * output_token_cost}")
        print(f"fitness: {sum(fitness_list) / len(fitness_list)}")
    elif args.method == "mapcoder":
        pass_count = 0
        input_tokens_total = 0
        output_tokens_total = 0
        fitness_list = []
        for i, problem in tqdm(enumerate(data), total=len(data),
                               desc="Running mapcoder with model {}".format(args.model)):
            problem_desc = problem["problem_description"]
            examples = problem["examples"]
            test_examples = problem["test_examples"]  # true test_cases
            rerun = True
            for j in range(4):
                if rerun:
                    try:
                        success, input_tokens, output_tokens, fitness = query_mapcoder(problem_desc=problem_desc, samples=examples,
                                                                                   test_samples=test_examples, k_sample=3,
                                                                                   greedy_search_iteration=args.greedy_search_iterations,
                                                                                   model=args.model)
                        rerun = False
                        pass_count += success
                        fitness_list.append(fitness)
                        input_tokens_total += input_tokens
                        output_tokens_total += output_tokens
                    except Exception as e:
                        print(e)
                if j == 3 and rerun:
                    fitness_list.append(0)
                    input_tokens_total += int(input_tokens_total / (i+1))
                    output_tokens_total += int(output_tokens_total / (i+1))
        pass_rate = pass_count / len(data)
        avg_input_tokens = input_tokens_total / len(data)
        avg_output_tokens = output_tokens_total / len(data)
        print(f"pass_rate: {pass_rate}")
        print(f"avg input token: {avg_input_tokens}")
        print(f"avg output token: {avg_output_tokens}")
        print(f"avg problem cost: {avg_input_tokens * input_token_cost + avg_output_tokens * output_token_cost}")
        print(f"fitness: {sum(fitness_list) / len(fitness_list)}")
    elif args.method == "cot":
        max_trys = args.greedy_search_iterations * args.evolution_iterations
        for problem in tqdm(data):
            pass #todo：添加cot baseline, 用cot测多次，只要在示例中通过则submit

if __name__ == '__main__':
    main()