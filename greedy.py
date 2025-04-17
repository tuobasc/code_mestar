from coder import Coder
from src.utils import request, parser_codes

greedy_query_prompt = """You are an expert in algorithms and data structures.
Given a competitive programming problem, please generate a python code to solve the problem.
## Problem: 
{problem_desc} 
## Sample Input/Outputs: 
We will test your code with the following examples.
{samples} 
Please follow the plan step by step and realize the code. No need to include test code.

Your response must follow the following format:
```python
# your code here
```
"""

def query_greedy(problem_desc, samples, test_samples=None, max_trys=9, model="gpt-4o-mini"):
    coder = Coder()
    query = greedy_query_prompt.format(problem_desc=problem_desc, samples=samples)
    input_tokens_total = 0
    output_tokens_total = 0
    for _ in range(max_trys):
        res, input_tokens, output_tokens = request(query, model=model)
        input_tokens_total += input_tokens
        output_tokens_total += output_tokens
        code = parser_codes(res)
        test_cases_res, exec_res, pass_count = coder.run(code, samples) # 在部分测试用例上可以通过则submit
        if pass_count == len(test_cases_res):
            # submit
            if test_samples:
                test_cases_res, exec_res, pass_count = coder.run(code, test_samples)
                if pass_count == len(test_cases_res):
                    # pass the question
                    return 1, input_tokens_total, output_tokens_total
                else:
                    return 0, input_tokens_total, output_tokens_total # fail to pass
            else:
                print("No test samples.")
                print("######## Codes:")
                print(code)
                break

    return 0, input_tokens_total, output_tokens_total # fail to pass even examples