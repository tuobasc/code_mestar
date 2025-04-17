from planner import Planner
from coder import Coder

def query_code_master(problem_desc, samples, test_samples=None, counterfactual_thinking=False, k_sample=3, greedy_search_iterations=3, evolution_iterations=2):
    if counterfactual_thinking:
        notes = ""
    else:
        notes = ""
    # Todo: remake the samples structures
    planner = Planner()
    plans, notes = planner.planning(problem_desc, samples, notes, k_sample)
    planner.plans = sorted(plans, key=lambda plan: plan["confidence"], reverse=True)
    planner.print_plans()
    coder = Coder()
    print("Logs: Try to solve the problem...")
    code = coder.writing(problem_desc, planner.plans[0]["plan"], samples, notes)
    print("Logs: Code\n", code)
    true_res, run_res, pass_count = coder.run(code, samples)
    if pass_count == len(true_res):
        """SUBMIT"""
        print("Logs: Pass through sample cases!")
        total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts
        total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts
        if test_samples:
            print("Logs: Submit the code...")
            true_res_test, run_res_test, pass_count_test = coder.run(code, test_samples)
            if pass_count_test == len(true_res_test):
                print("Logs: Pass through all test cases!")
                return 1, total_tokens_in, total_tokens_out
            else:
                print(f"Logs: Fail to pass test cases! Fitness = {pass_count_test / len(true_res_test)}")
                return 0, total_tokens_in, total_tokens_out
        else:
            print("Warning: No test samples!")
            return 1, total_tokens_in, total_tokens_out
    else:
        unfitness = 1 - pass_count / len(true_res) # minimize unfitness
        # Todo: debug
        """DEBUG with greedy search"""
        print("Logs: Fail to pass the sample cases! Enter DEBUG mode...")




if __name__ == '__main__':
    problem_description = """You are given two integers l and r represented as strings, and an integer b. Return the number of integers within the closed interval [l, r] that have digits in non-decreasing order when represented in base b.
An integer is said to have non-decreasing digits if, when read from left to right (from the most significant digit to the least significant digit), each digit is greater than or equal to the preceding digit.
Since the answer may be very large, return the result modulo 10⁹ + 7.

Constraints:
1 <= l.length <= r.length <= 100
2 <= b <= 10
l and r consist only of digits (0-9).
The numerical value represented by l is less than or equal to that represented by r.
l and r do not contain any leading zeros.
    """

    examples = [{"input": "countNumbers(l='23', r='28', b=8)",
                 "output": "3",
                 "explanation": "The numbers from 23 to 28, when converted to base 8, are: 27, 30, 31, 32, 33, and 34. "
                                "Among these, the numbers 27, 33, and 34 have non-decreasing digits. Therefore, the output is 3."}]

    test_examples = [{"input": "countNumbers(l='2', r='7', b=2)",
                      "output": "2",
                      "explanation": "The numbers from 2 to 7, when converted to base 2, are: 10, 11, 100, 101, 110, and 111. "
                                     "Among these, the numbers 11 and 111 have non-decreasing digits. Therefore, the output is 2."}]

    query_code_master(problem_desc=problem_description, samples=examples, test_samples=test_examples, counterfactual_thinking=False)