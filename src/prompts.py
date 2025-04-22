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

planner_evolution_planning_prompt = """You are an expert in algorithms and data structures.
Given a competitive programming problem and a not working plan from beginner, please give a different plan to solve the problem. 
You can make a new plan with a different method and strategy, or make a more effective plan.
## Problem: 
{problem_desc} 
## Original Plan:
{base_plan}
## Sample Input/Outputs (if any): 
{samples} 

## Notes: 
{notes}

Your response must follow the following json format:
```json
{{
    'new_plan': "a detailed new plan to solve the problem",
}}
```
"""

coder_prompt = """You are an expert in algorithms and coding.
Given a competitive programming problem, please generate Python code to solve the problem.

## Problem: 
{problem_desc} 
## Plan:
{plan}
## Sample Input/Outputs (if any): 
We will test your solution through the following function call (if any).
{samples} 
## Notes:
{notes}
Please follow the plan step by step and realize the code. No need to include test code.
Please make sure your code complies with the function call method (if any).

Your response must follow the following format:
```python
# your code here
```
"""

debugger_debug_prompt = """You are an expert in algorithms and coding.
Here is a competitive programming problem, along with the plan (an explanation about problem-solving ideas) and the corresponding code. 
But the generated code cannot pass some test cases. Please find the error, modify the original plan and give the correct code.
## Problem: 
{problem_desc} 
## Original Plan:
{plan}
## Corresponding Code:
{code}
## Test Cases: 
{error_samples}

## Notes: The result validation program will consider both "correct answer" and ["correct answer"] as the correct answer.

Your response must follow the following json format:
```json
{{
    "error": "The errors in the original plan or original code.", 
    "revised_plan": "Give a correct plan to solve the problem.",
    "revised_code": "Give the correct code based on the revised plan.",
}}
"""

debugger_optimization_prompt = """You are an expert in algorithms and coding.
Here is a competitive programming problem, along with the plan (an explanation about problem-solving ideas) and the corresponding code. 
But the generated method are not good enough. Please modify the original plan and give the corresponding code.
## Problem: 
{problem_desc} 
## Original Plan:
{plan}
## Corresponding Code:
{code}

```json
{{
    "ideas": "The ideas to improve the original plan", 
    "revised_plan": "Give a better plan to solve the problem.",
    "revised_code": "Give the better code based on the revised plan.",
}}
"""

thinker_understand_prompt = """You are an expert in algorithms and coding.
Given a competitive programming problem and some test cases, please explain how to get the output from the input. 
## Problem: 
{problem_desc} 
## Test Cases Input(with function call)/Outputs: 
{samples}

Your response must follow the following json format:
```json
[
    {{
        "case_id": "the case id and counting starts form 0",
        "input": "the input of the test case", 
        "output": "the output of the test case", 
        "explanation": "the explanation about how to get the output of from the input in this test case",
    }},
]
"""

thinker_counter_prompt = """You are an expert in algorithms and coding.
Here is a competitive programming problem along with its test cases, but these test cases only cover partial or general scenarios of the problem. 
Please consider the edge cases, i.e., special scenarios, and create new test cases. 
Additionally, for correctly handling these cases, what should we pay attention to during coding?

## Problem: 
{problem_desc} 
## Test Cases Input(with function call)/Outputs: 
{samples}

Your response must follow the following json format:
[
    {{
        "new_case_id": "the case id and counting starts form 0",
        "input": "the input of the test case, must be a function call", 
        "output": "the expected output of the test case",
        "explanation": "the explanation about how to get the output of from the input in this test case",
        "notes": "some general notes or hints about how to correctly handle such cases",
    }},
]
"""

thinker_normal_prompt = """You are an expert in algorithms and coding.
Here is a competitive programming problem along with its test cases (if any). 
Please consider some specific cases or scenarios, and explain what general strategy can we take to effectively handle these cases or scenarios. 

## Problem: 
{problem_desc} 
## Test Cases Input(with function call)/Outputs (if any): 
{samples}

Your response must follow the following json format:
[
    {{
        "case_id": "The id for different cases and scenarios. Counting starts form 0.",
        "specific_case": "The specific case or scenario.",
        "strategy": "The explanation about what general strategy can we take to effectively handle such cases or scenarios.",
    }},
]
"""

mapcoder_retrieval_prompt = """
Given a problem, provide relevant problems then identify the algorithm behind it and also explain the tutorial of the algorithm. 
# Problem:
{problem_desc}
# Exemplars:
Recall k relevant and distinct problems (different from problem mentioned above). For each problem, 
1. describe it
2. generate python code step by step to solve that problem
3. finally generate a planning to solve that problem
# Algorithm:
----------------
Important:
Your response must follow the following xml format:
<root>
    <problem>
        # Recall k relevant and distinct problems (different from problem mentioned above). Write each problem in the following format.
        <description> # Describe the problem. </description>
        <code> # Let's think step by step to solve this problem. </code>
        <planning> # Planning to solve this problem. </planning>
    </problem>
    # similarly add more problems here...
    <algorithm>
        # Identify the algorithm (Brute-force, Dynamic Programming, Divide-and-conquer, Greedy, Backtracking, Recursive, Binary search, 
        and so on) that needs to be used to solve the original problem.
        # Write a useful tutorial about the above mentioned algorithms. Provide a high level generic tutorial for solving this types 
        of problem. Do not generate code.
    </algorithm>
</root>
"""

mapcoder_planning_prompt = """
Given a competitive programming problem, generate a concrete planning to solve the problem.
## Problem: {description}
## Planning: {plans}
## Relevant Algorithm to solve the next problem:
{algorithm}

# Problem to be solved: 
{problem_desc}
# Sample Input/Outputs: 
{examples}

----------------
Important: You should give only the planning to solve the problem. Do not add extra explanation or words.

Your response must follow the following json format:
```json
{{
    'plan': "a detailed new plan to solve the problem",
}}
```
"""

mapcoder_confidence_generation_prompt = """
Given a competitive programming problem and a plan to solve the problem tell whether the plan is correct to solve this problem.

# Problem: {problem_desc}
# Planning: {plan}

----------------
Important: Your response must follow the following json format:
```json
{{
    "explanation": "Discuss whether the given competitive programming problem is solvable by using the above mentioned planning",
    "confidence": "Confidence score regarding the solvability of the problem. Must be an integer between 0 and 100."
}}
```
"""

mapcoder_coding_prompt = """
Given a competitive programming problem generate Python code to solve the problem.

## Relevant Algorithm to solve the next problem:
{algorithm}
## Problem to be solved:
{problem_desc}
## Planning: 
{plan}
## Sample Input/Outputs: 
{examples}
## Let's think step by step.

------------
Important: Your response must follow the following format:
```python
# your code here
```
"""

mapcoder_debugging_prompt = """
Given a competitive programming problem you have generated code to solve the problem. 
But the generated code cannot pass sample test cases. Improve your code to solve the problem correctly.

## Relevant Algorithm to solve the next problem:
{algorithm}
## Problem to be solved:
{problem_desc}
## Planning: 
{plan}
## Code: 
{code}
## Modified Planning:
## Let's think step by step to modify code for solving this problem.

----------------
Important: Your response must follow the following format:

```python
# your code here
```
"""