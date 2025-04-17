import os
import re
import random

from src.utils import load_jsonl, sample_encoder

# Todo: ablation, 这里划分比例修改一下, 比如 0.8, 0.9, 0.95是否会对方法产生影响
def load_dataset(file_path, split_test_ratio=0.9):
    datas = load_jsonl(file_path)
    problems = []
    filename = os.path.basename(file_path)

    for data in datas:
        if filename == 'HumanEvalET.jsonl':
            problem_description = data.get('prompt', '')
            raw_cases = data.get('test_case_list', [])
            splitter = _split_humanEval_test_case

        elif filename == 'MBPP_ET.jsonl':
            problem_description = data.get('text', '')
            raw_cases = data.get('test_list', [])
            splitter = _split_MBPP_test_case

        elif filename in ('APPS_selected150.jsonl', 'CodeContest.jsonl'):
            problem_description = data.get('description', '')
            raw_cases = data.get('sample_io', []) + data.get('test_list', [])
            splitter = None

        else:
            raise ValueError(f"Unrecognized file: {filename}")

        all_examples = []
        if splitter:
            # need to parse each raw string case
            for tc in raw_cases:
                inp, out = splitter(tc)
                all_examples.append({"input": inp, "output": out})
        else:
            # already paired
            all_examples = raw_cases.copy()

        train_examples, test_examples = _split_examples(all_examples, test_size=split_test_ratio)
        problems.append({
            "problem_description": problem_description,
            "examples": train_examples,
            "test_examples": test_examples
        })

    return problems


def _split_humanEval_test_case(test_case):
    input_str, output = None, None

    test_case = test_case.strip()
    # Remove the 'assert ' prefix if present.
    if test_case.startswith("assert "):
        test_case = test_case[len("assert "):]

    # abs(function_call(params) - expected) < tolerance
    type1_pattern = re.compile(r"abs\w+\((.*?)\) - (.*?)\) <", re.DOTALL)
    # (func(params) == expected), 'extra'
    type2_pattern = re.compile(r"\((\w+\((.*)\)) == (.*)\)(?:,\s*.*)?", re.DOTALL)
    # function_name(params) == expected
    type3_pattern = re.compile(r"(\w+\(.*\))\s*==\s*(.*)", re.DOTALL)
    # function_call(params) is True/False
    type4_pattern = re.compile(r"(\w+\(.*\))\s+is\s+(True|False)", re.DOTALL)
    # not function_call(params)
    type5_pattern = re.compile(r"not\s+(\w+)\((.*)\)", re.DOTALL)
    # function_call(params)
    type6_pattern = re.compile(r"(\w+)\((.*)\)", re.DOTALL)

    # Type 1 abs(function_call(params) - expected) < tolerance
    type1_match = type1_pattern.search(test_case)
    if type1_match:
        # Extract function call and expected output (direct comparison)
        input_str = type1_match.group(1).strip()  # The function call part
        output = type1_match.group(2).strip()  # The expected output
        return input_str, output

    # Type 2 (func(params) == expected), 'extra'
    type2_match = type2_pattern.search(test_case)
    if type2_match:
        # Extract input function call and comparison operator
        input_str = type2_match.group(2).strip()  # The function call part
        output = type2_match.group(3).strip()  # The expected output
        return input_str, output

    # Type 3 function_name(params) == expected
    # Type 4 function_call(params) is True/False
    type3or4_match = type3_pattern.search(test_case) if type3_pattern.search(test_case) else type4_pattern.search(
        test_case)
    if type3or4_match:
        func_call = type3or4_match.group(1).strip()
        output = type3or4_match.group(2).strip()
        inner_match = re.match(r"\w+\((.*)\)", func_call)
        if inner_match:
            input_str = inner_match.group(1).strip()
        else:
            input_str = func_call
        return input_str, output

    # Type 5 not function_call(params)
    type5_match = type5_pattern.search(test_case)
    if type5_match:
        input_str = type5_match.group(2).strip()
        output = "False"
        return input_str, output

    # Type 6 function_call(params)
    type6_match = type6_pattern.search(test_case)
    if type6_match:
        input_str = type6_match.group(2).strip()
        output = "True"
        return input_str, output

    # If no valid match found, raise an error
    if input_str is None or output is None:
        raise ValueError(f"Invalid test case format: {test_case}")

    return input_str, output


def _split_MBPP_test_case(test_case):
    input_str, output = None, None

    test_case = test_case.strip()
    # Remove the 'assert ' prefix if present.
    if test_case.startswith("assert "):
        test_case = test_case[len("assert "):]

    # function_name(params) == expected
    type1_pattern = re.compile(r"(\w+\s*\(.*\))\s*==\s*(.*)", re.DOTALL)
    type1_match = type1_pattern.search(test_case)
    if type1_match:
        func_call = type1_match.group(1).strip()
        output = type1_match.group(2).strip()
        inner_match = re.match(r"\w+\((.*)\)", func_call)
        if inner_match:
            input_str = inner_match.group(1).strip()
        else:
            input_str = func_call
        return input_str, output

    # abs(function_call(params) - expected) < tolerance
    type2_pattern = re.compile(r"abs\w+\((.*?)\) - (.*?)\) <", re.DOTALL)
    type2_match = type2_pattern.search(test_case)
    if type2_match:
        # Extract function call and expected output (direct comparison)
        input_str = type2_match.group(1).strip()  # The function call part
        output = type2_match.group(2).strip()  # The expected output
        return input_str, output

    if input_str is None or output is None:
        raise ValueError(f"Invalid test case format: {test_case}")

    return input_str, output


def _split_examples(all_examples, test_size=0.2, seed=42):
    """Shuffle and split examples into train and test."""
    random.seed(seed)
    examples = all_examples[:]  # copy
    random.shuffle(examples)
    split_at = int(len(examples) * (1 - test_size))
    return examples[:split_at], examples[split_at:]


if __name__ == '__main__':
    filepath = 'HumanEvalET.jsonl'

    if filepath == 'HumanEvalET.jsonl':
        # try split humanEval test case
        # Type 1
        print(_split_humanEval_test_case(
            "assert abs(mean_absolute_deviation([1.072, 7.932, 1.603]) - 2.930888888888889) < 1e-6"))
        print(_split_humanEval_test_case("assert abs(mean_absolute_deviation([1.0, 2.0, 3.0]) - 2.0/3.0) < 1e-6"))
        # Type 2
        print(_split_humanEval_test_case("assert string_xor('9899538', '0376864') == '1111111'"))
        print(_split_humanEval_test_case('assert has_close_elements([4.88, 7.89, 3.67, 5.68, 4.88], 2.06) == True'))
        print(_split_humanEval_test_case(
            "assert separate_paren_groups(\"(()())(()())(())\") == ['(()())', '(()())', '(())']"))
        print(_split_humanEval_test_case("assert truncate_number(3.952) == 0.952"))
        print(_split_humanEval_test_case("assert is_simple_power(1, 1)==True"))
        print(_split_humanEval_test_case("assert (find_max([\"aaaaaaa\", \"bb\", \"cc\"]) == \"aaaaaaa\"), 't3'"))
        print(_split_humanEval_test_case("assert generate_integers(130, 1) == [2, 4, 6, 8]"))
        print(_split_humanEval_test_case("assert string_to_md5(\"WGCJWEUA\") == '00e78877b3373720890110d1b297d370'"))
        # Type 3
        print(_split_humanEval_test_case("assert not candidate(\"<<<><>>>>\")"))
        print(_split_humanEval_test_case("assert candidate(\"<><><<<><><>><>><<><><<>>>\")"))
        # Type 4
        print(_split_humanEval_test_case("assert candidate([3], 5) is True"))
        print(_split_humanEval_test_case("assert candidate([1, 2], 5) is False"))

        # try load HumanEvalET.jsonl
        problems = load_dataset("data/HumanEvalET.jsonl")
        print(problems.pop())

    if filepath == 'MBPP_ET.jsonl':
        # Type 1
        print(_split_MBPP_test_case("is_Diff (12345) == False"))
        print(_split_MBPP_test_case("change_date_format(\"2-:9|&#>5\")  == \"-:9|&#>5\""))

        problems = load_dataset("data/MBPP_ET.jsonl")
        print(problems.pop())

    if filepath == 'APPS_selected150.jsonl':
        problems = load_dataset("data/APPS_selected150.jsonl")
        print(problems.pop())

    if filepath == 'CodeContest.jsonl':
        problems = load_dataset("data/CodeContest.jsonl")
        print(problems.pop())

