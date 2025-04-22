import os
import re
import random
import json
from coder import Coder
from src.utils import load_jsonl, identify
from tqdm import tqdm

def load_dataset(file_path, split_test_ratio=0.95):
    datas = load_jsonl(file_path)
    problems = []
    filename = os.path.basename(file_path)

    names = []
    for data in datas:
        if filename == 'HumanEvalET.jsonl':
            problem_description = data.get('prompt', '')
            raw_cases = data.get('test_case_list', [])
            split_sentence = problem_description.split('\n')
            definition = [s for s in split_sentence if "def" in s]
            ground_truth = definition[0] + "\n" + data["canonical_solution"]
            splitter = _split_humanEval_test_case

        elif filename == 'MBPP_ET.jsonl':
            problem_description = data.get('text', '')
            raw_cases = data.get('test_list', [])
            ground_truth = data["code"]
            splitter = _split_MBPP_test_case

        elif filename in ('APPS_selected150.jsonl', 'CodeContest.jsonl'):
            if data["name"] not in names:
                names.append(data["name"])
            else:
                continue

            problem_description = data.get('description', '')
            raw_cases = data.get('sample_io', []) + data.get('test_list', [])
            if any("\\n" in str(case["output"]) for case in raw_cases):
                continue

            correct_cases = []
            function_name = data.get('starter_code', '')
            if function_name:
                function_name = function_name.strip()[4:].split('(')[0]
            else:
                function_name = "problem_solution"
            for case in raw_cases:
                case_dict = dict()
                if identify(case["input"]):
                    case_dict['input'] = f"{function_name}(" + case['input'] + ")"
                else:
                    if "\n" in case['input']:
                        if function_name in ["problem_solution", ""]:
                            if str(data["name"]) in ["2104", "2199", "2037", "2174"]:
                                case_dict['input'] = function_name + "(\"\"\"" + case["input"] + "\"\"\")"
                            else:
                                case_dict['input'] = function_name + "(" + str(case['input'].split("\n")) + ")"
                        elif str(data["name"]) in ["4344", "3856", "3978", "4262", "3155", "1643", "1627", "1642",
                                                   "1648", "3045", "3741", "1621", "1658", "1665", "3478"]:
                            case_dict['input'] = function_name + "(" + ", ".join(case['input'].split("\n")) + ")"
                        else:
                            case_dict['input'] = function_name + "(\"" + "\",\"".join(case['input'].split("\n")) + "\")"
                    else:
                        if str(data["name"]) in ["4335"]:
                            case_dict['input'] = f"{function_name}(" + case['input'] + ")"
                        else:
                            case_dict['input'] = f"{function_name}(\"" + case['input'] + "\")"
                case_dict['output'] = str(case['output'])
                correct_cases.append(case_dict)
            raw_cases = correct_cases
            # print("Name:", data["name"])
            # print("Starter code:", data["starter_code"])
            # print("raw_cases:", raw_cases)
            # print("---------------------")
            ground_truth = None
            splitter = None

        else:
            raise ValueError(f"Unrecognized file: {filename}")

        all_examples = []
        if splitter:
            for tc in raw_cases:
                inp, out = splitter(tc)
                all_examples.append({"input": inp, "output": out})
        else:
            all_examples = raw_cases.copy()

        train_examples, test_examples = _split_examples(all_examples, test_size=split_test_ratio)
        # print(train_examples[0])
        # print(test_examples[0])
        problems.append({
            "problem_description": problem_description,
            "examples": train_examples,
            "test_examples": test_examples,
            "ground_truth": ground_truth
        })

    return problems


def _split_humanEval_test_case(test_case):
    test = test_case.strip()
    if test.startswith("assert "):
        test = test[len("assert "):]

    # 各种匹配模式
    type1_pattern = re.compile(r"abs\w+\((.*?)\) - (.*?)\) <", re.DOTALL)
    type2_pattern = re.compile(r"\((\w+\((.*)\)) == (.*)\)(?:,\s*.*)?", re.DOTALL)
    type3_pattern = re.compile(r"(\w+\(.*\))\s*==\s*(.*)", re.DOTALL)
    type4_pattern = re.compile(r"(\w+\(.*\))\s+is\s+(True|False)", re.DOTALL)
    type5_pattern = re.compile(r"not\s+(\w+)\((.*)\)", re.DOTALL)
    type6_pattern = re.compile(r"(\w+)\((.*)\)", re.DOTALL)

    # Type 1: abs(func_call(...) - expected) < tol
    m1 = type1_pattern.search(test)
    if m1:
        func_call = m1.group(1).strip()
        output = m1.group(2).strip()
        return func_call, output

    # Type 2: (func_call(...) == expected), 'extra'
    m2 = type2_pattern.search(test)
    if m2:
        func_call = m2.group(1).strip()
        output = m2.group(3).strip()
        return func_call, output

    # Type 3: func_call(...) == expected
    # Type 4: func_call(...) is True/False
    m3 = type3_pattern.search(test)
    m4 = type4_pattern.search(test)
    m34 = m3 or m4
    if m34:
        func_call = m34.group(1).strip()
        output = m34.group(2).strip()
        return func_call, output

    # Type 5: not func_call(...)
    m5 = type5_pattern.search(test)
    if m5:
        fname = m5.group(1).strip()
        args = m5.group(2).strip()
        func_call = f"{fname}({args})"
        return func_call, "False"

    # Type 6: func_call(...)
    m6 = type6_pattern.search(test)
    if m6:
        fname = m6.group(1).strip()
        args = m6.group(2).strip()
        func_call = f"{fname}({args})"
        return func_call, "True"

    raise ValueError(f"Invalid test case format: {test_case}")


def _split_MBPP_test_case(test_case):
    test = test_case.strip()
    if test.startswith("assert "):
        test = test[len("assert "):]

    # Type 1: func_call(...) == expected
    type1_pattern = re.compile(r"(\w+\s*\(.*\))\s*==\s*(.*)", re.DOTALL)
    m1 = type1_pattern.search(test)
    if m1:
        func_call = m1.group(1).strip()
        output = m1.group(2).strip()
        return func_call, output

    # Type 2: abs(func_call(...) - expected) < tol
    type2_pattern = re.compile(r"abs\w+\((.*?)\) - (.*?)\) <", re.DOTALL)
    m2 = type2_pattern.search(test)
    if m2:
        func_call = m2.group(1).strip()
        output = m2.group(2).strip()
        return func_call, output

    raise ValueError(f"Invalid test case format: {test_case}")


def _split_examples(all_examples, test_size=0.2, seed=42):
    split_at = int(len(all_examples) * (1 - test_size))
    split_at = split_at if split_at > 0 else 1
    random.seed(seed)
    examples = all_examples[:]  # copy
    random.shuffle(examples)
    return examples[:split_at], examples[split_at:]

if __name__ == '__main__':
    filepath = 'HumanEvalET.jsonl'
    saved_filepath = "HumanEvalET_preprocessed.json"
    split_test_ratio = 0.9

    problems = load_dataset(f"data/{filepath}", split_test_ratio=split_test_ratio)

    # self-checking, please do not delete
    coder = Coder()
    pass_count_pro = 0
    good_problems = []
    for _, problem in tqdm(enumerate(problems), total=len(problems), desc="Self-checking"):
        if len(problem["problem_description"].split(" ")) >= 100000:
            continue
        total_samples = problem["examples"] + problem["test_examples"]
        # print(problem["ground_truth"])
        test_cases_res, exec_res, pass_count = coder.run(problem["ground_truth"], total_samples, verbose=True)
        good_samples = []
        for i in range(len(test_cases_res)):
            t_res = test_cases_res[i]
            r_res = exec_res[i]
            # print(t_res)
            # print(r_res)
            if t_res == r_res:
                # print("get here")
                good_samples.append(total_samples[i])
                # print(good_samples)
            else:
                try:
                    if abs(float(t_res) - float(r_res)) < 1e-6:
                        # print("get here")
                        good_samples.append(total_samples[i])
                except ValueError:
                    pass
        good_problem = {"problem_description": problem["problem_description"], "ground truth": problem["ground_truth"], "instances": good_samples}
        print(good_samples)
        good_problems.append(good_problem)
    # print(pass_count_pro)
    with open(f"data/{saved_filepath}", "w") as f:
        json.dump(good_problems, f, indent=4)