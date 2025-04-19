import argparse
import json
import os
from preprocess import load_dataset
from tqdm import tqdm
from query import query_code_master
from greedy import query_greedy

parser = argparse.ArgumentParser()
parser.add_argument('--dataset_name', type=str, default="HumanEvalET", help='the name of dataset')
parser.add_argument('--split_test_ratio', type=float, default=0.9, help='the ratio of test instances')
parser.add_argument('--method', type=str, default="greedy", choices=["greedy", "code-master", "cot"],help='the method to use')
parser.add_argument('--model', type=str, default="gpt-4o-mini", choices=["gpt-4o-mini", "deepseek-r1", "gpt-4o"], help='api model')
parser.add_argument('--counterfactual_think', type=int, default=0, help='if think before plan')
parser.add_argument('--greedy_search_iterations', type=int, default=3, help='code master max debug times')
parser.add_argument('--evolution_iterations', type=int, default=3, help='code master max evolution times')

# 解析参数
args = parser.parse_args()

# todo: 查找一下不同model的cost
if args.model == "gpt-4o-mini":
    input_token_cost = 0
    output_token_cost = 0
elif args.model == "deepseek-r1":
    input_token_cost = 0
    output_token_cost = 0
elif args.model == "gpt-4o":
    input_token_cost = 0
    output_token_cost = 0

def main():
    if "HumanEvalET" in args.dataset_name:
        with open("data/HumanEvalET_preprocessed.json", "r") as f:
            problems = json.loads(f)
            data = []
            for problem in problems:
                meta_data = dict()
                meta_data["problem_description"] = problem["problem_description"]
                saved_samples_length = int((1 - args.split_test_ratio) * len(problem["instance"])) if int((1 - args.split_test_ratio) * len(problem["instance"])) else 1
                meta_data["example"] = problem["instance"][:saved_samples_length]
                meta_data["test_examples"] = problem["instance"][saved_samples_length:]
                data.append(meta_data)
    elif "MBPP_ET" in args.dataset_name:
        with open("data/MBPP_ET_preprocessed.json", "r") as f:
            problems = json.loads(f)
            data = []
            for problem in problems:
                meta_data = dict()
                meta_data["problem_description"] = problem["problem_description"]
                saved_samples_length = int((1 - args.split_test_ratio) * len(problem["instance"])) if int(
                    (1 - args.split_test_ratio) * len(problem["instance"])) else 1
                meta_data["example"] = problem["instance"][:saved_samples_length]
                meta_data["test_examples"] = problem["instance"][saved_samples_length:]
                data.append(meta_data)
    elif "APP" in args.dataset_name:
        data = load_dataset(args.dataset_name, args.split_test_ratio)
    else:
        raise RuntimeError

    if args.method == "code-master":
        for problem in tqdm(data):
            problem_desc = problem["problem_description"]
            examples = problem["examples"]
            test_examples = problem["test_examples"] # true test_cases
            query_code_master(problem_desc=problem_desc, samples=examples, test_samples=test_examples,
                              counterfactual_thinking=args.counterfactual_thinking,
                              greedy_search_iterations=args.greedy_search_iterations,
                              evolution_iterations=args.evolution_iterations)
            pass #todo: not finished yet

    elif args.method == "greedy":
        max_trys = args.greedy_search_iterations * args.evolution_iterations # to compare fairly
        input_tokens_total = 0
        output_tokens_total = 0
        pass_count = 0
        for _, problem in tqdm(enumerate(data), total=len(data), desc="Running greedy method with model {}".format(args.model)):
            problem_desc = problem["problem_description"]
            examples = problem["examples"]
            test_examples = problem["test_examples"]  # true test_cases
            res, input_tokens, output_tokens = query_greedy(problem_desc=problem_desc, samples=examples, test_samples=test_examples, max_trys=max_trys, model=args.model)
            pass_count += 1 if res else 0 # todo: 确认一下能不能这样写
            input_tokens_total += input_tokens
            output_tokens_total += output_tokens
        pass_rate = pass_count / len(data)
        avg_input_tokens = input_tokens_total / len(data)
        avg_output_tokens = output_tokens_total / len(data)
        print(f"pass_rate: {pass_rate}.4f")
        print(f"avg input token: {avg_input_tokens}")
        print(f"avg output token: {avg_output_tokens}")
        print(f"avg problem cost: {avg_input_tokens * input_token_cost + avg_output_tokens * output_token_cost}.2f")

    elif args.method == "cot":
        max_trys = args.greedy_search_iterations * args.evolution_iterations
        for problem in tqdm(data):
            pass #todo：添加cot baseline, 用cot测多次，只要在示例中通过则submit

if __name__ == '__main__':
    main()