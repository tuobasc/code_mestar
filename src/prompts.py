planner_prompt = """You are an expert in algorithms and data structures.
Given a competitive programming problem, please generate a concrete plan to solve the problem.
## Problem: 
{problem_desc} 
## Sample Input/Outputs: 
{samples} 

## Notes: 
You should give only the planning to solve the problem. Do not add extra explanation or words.
{notes}

Your response must follow the following json format:
```json
{{
    'plan': "a detailed plan to solve the problem",
}}
```
"""

# Todo: 这里试一下去掉from beginner的效果
planner_confidence_prompt = """You are an expert in algorithms and data structures.
Given a competitive programming problem and a rough plan from beginner to solve the problem in python.
Please determine whether the plan is correct to solve this problem.

## Problem: 
{problem_desc} 
## Plan:
{plan}

## Notes:
{notes}

Your response must follow the following json format:
```json
{{
    "discussion": "Discuss whether the given competitive programming problem is solvable by using the above mentioned plan.",
    "confidence": "Confidence level regarding the solvability of the problem. 
                    Level 0 indicates that the plan is unable to solve the problem, even though the problem is solvable; 
                    Level 1 indicates that the plan has the possibility to solve the problem, and can perform well in some test cases.
                    Level 2 indicates that the plan has the great potential to solve the problem, takes various possible scenarios into account, and perform well in most test cases.
                    Confidence level must be an integer from [0, 1, 2].",
}}
```
"""

coder_prompt = """You are an expert in algorithms and coding.
Given a competitive programming problem, please generate Python code to solve the problem.

## Problem: 
{problem_desc} 
## Plan:
{plan}
## Sample Input/Outputs: 
We will test your solution through the following function call.
{samples} 
## Notes:
{notes}
Please follow the plan step by step and realize the code. No need to include test code.
Please make sure your code complies with the function call method.

Your response must follow the following format:
```python
# your code here
```
"""

debugger_prompt = """You are an expert in algorithms and coding.
Given a competitive programming problem, a plan and corresponding python code have been generated to solve the problem. 
But the generated code cannot pass sample test cases. Please find the error, write comments to avoid such issues and modify the original plan.
## Problem: 
{problem_desc} 
## Original Plan:
{plan}
## Corresponding Code:
{code}
## Test Samples with Error: 
{error_samples}

Your response must follow the following json format:
```json
{{
    "error": "The errors in the original plan or original code.", 
    "comments": "Write comments to avoid such errors.", 
    "revised_plan": "Give a correct plan to solve the problem.",
}}
"""
