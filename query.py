from thinker import Thinker
from planner import Planner
from coder import Coder
from debugger import Debugger

def submit(coder, code, test_samples, verbose):
    print("Logs: Submit the code...")
    true_res_test, run_res_test, pass_count_test = coder.run(code, test_samples, verbose=verbose)
    fitness = pass_count_test / len(true_res_test)
    if pass_count_test == len(true_res_test):
        print("Logs: Pass through all test cases!")
        return 1, fitness
    else:
        print(f"Logs: Fail to pass test cases! Fitness = {pass_count_test / len(true_res_test)}")
        return 0, fitness

def query_code_master(problem_desc, samples=None, test_samples=None, counterfactual_thinking=False, k_sample=3,
                      greedy_search_iterations=3, evolution_iterations=3, model="gpt-4o-mini", optimization=False, verbose=True):
    if counterfactual_thinking:
        thinker = Thinker(thinking_method="counterfactual")
    else:
        thinker = Thinker(thinking_method="normal")
    planner = Planner()
    coder = Coder()
    debugger = Debugger()

    if samples:
        good_samples = thinker.understand(problem_desc, samples, model=model)
    else:
        good_samples = None
    additional_samples, notes = thinker.specific_thinking(problem_desc, good_samples, model=model)
    base_plan = ""
    base_score = 0
    base_code = ""
    # additional_samples = None
    notes = ""
    good_samples = samples
    for i in range(evolution_iterations):
        # print(base_plan)
        if i > 0:
            if verbose:
                print("Logs: Resetting the understanding.")
            # base_plan = ""
            # good_samples = samples
            # additional_samples = None
            # notes = ""
        plans = planner.planning(problem_desc, base_plan, good_samples, additional_samples, notes, k_sample, model=model)
        planner.plans = sorted(plans, key=lambda plan: plan["confidence"], reverse=True)
        if verbose:
            planner.print_plans()
            print("Logs: Try to solve the problem...")
        code = coder.writing(problem_desc, planner.plans[0]["plan"], good_samples, additional_samples, notes, model=model)
        if verbose:
            print("Logs: Code\n", code)
        if optimization:
            try:
                fitness = coder.fast_tsp_run(code)
            except Exception as e:
                print("fast_tsp_run error: ", e)
                fitness = 0
            print(f"evo{i}, base, fitness: {fitness}")
            if fitness > base_score or not base_plan:
                base_score = fitness
                base_plan = planner.plans[0]["plan"]
                base_code = code
            for j in range(greedy_search_iterations):
                revised_plan, revised_code = debugger.debug(problem_desc=problem_desc, plan=base_plan, code=base_code, temperature=0.2, model=model)
                print(revised_code)
                if not revised_code:
                    continue
                try:
                    revised_fitness = coder.fast_tsp_run(revised_code)
                except Exception as e:
                    print("fast_tsp_run error: ", e)
                    revised_fitness = 0
                print(f"evo{i}, search{j}, fitness: {revised_fitness}")
                if revised_fitness > base_score:
                    base_score = fitness
                    base_plan = revised_plan
                    base_code = revised_code
        else:
            true_res, run_res, pass_count = coder.run(code, good_samples, verbose=verbose)
            if pass_count == len(true_res):
                """SUBMIT"""
                print("Logs: Pass through sample cases!")
                total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + thinker.input_tokens_total + debugger.input_tokens_total
                total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + thinker.output_tokens_total + debugger.output_tokens_total

                if test_samples:
                    success, fitness = submit(coder, code, test_samples, verbose=verbose)
                    return success, total_tokens_in, total_tokens_out, fitness
                else:
                    print("Warning: No test samples!")
                    return 1, total_tokens_in, total_tokens_out, 1
            else:
                local_plans = []
                unfitness = 1 - pass_count / len(true_res) # minimize unfitness
                print("Logs: unfitness", unfitness)
                """DEBUG with greedy search"""
                print("Logs: Fail to pass the sample cases! Enter DEBUG mode...")
                unfit_problems = []
                for j in range(len(good_samples)):
                    t_res = true_res[j]
                    r_res = run_res[j]
                    unfit_problems.append({"input": good_samples[j]["input"], "output": t_res, "program_output": r_res})

                if unfitness < base_score or not base_plan:
                    base_score = unfitness
                    base_plan = planner.plans[0]["plan"]
                    base_code = code
                if verbose:
                    print("unfit_problems:", unfit_problems)
                evo_plan = planner.plans[0]["plan"] # set the plan to be evolved
                local_plans.append({"plan": evo_plan, "unfitness": unfitness})
                evo_code = code # set the code to be evolved
                for j in range(greedy_search_iterations):
                    # print("try to debugging....")
                    evo_plan, evo_code = debugger.debug(problem_desc=problem_desc, plan=evo_plan, code=evo_code, error_samples=unfit_problems, model=model)
                    print(f"evo{i}_search{j}_code:\n", evo_code)
                    if len(evo_code) == 0:
                        continue
                    true_res, run_res, pass_count = coder.run(evo_code, good_samples, verbose=verbose)

                    if pass_count == len(true_res):
                        """SUBMIT"""
                        print("Logs: Pass through sample cases!")
                        total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + thinker.input_tokens_total + debugger.input_tokens_total
                        total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + thinker.output_tokens_total + debugger.output_tokens_total
                        if test_samples:
                            success, fitness = submit(coder, evo_code, test_samples, verbose=verbose)
                            return success, total_tokens_in, total_tokens_out, fitness
                        else:
                            print("Warning: No test samples!")
                            return 1, total_tokens_in, total_tokens_out
                    else:
                        unfitness = 1 - pass_count / len(true_res)
                        local_plans.append({"plan": evo_plan, "unfitness": unfitness})
                # If still fail, enter evolution, update base plan
                local_plans = sorted(local_plans, key=lambda plan: plan["unfitness"])
                base_plan = local_plans[0]["plan"] if local_plans[0]["unfitness"] < base_score else base_plan
                base_score = local_plans[0]["unfitness"] if local_plans[0]["unfitness"] < base_score else base_score
                base_code = local_plans[0]["plan"] if local_plans[0]["unfitness"] < base_score else base_code


    print(base_plan)
    total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + thinker.input_tokens_total + debugger.input_tokens_total
    total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + thinker.output_tokens_total + debugger.output_tokens_total
    return 0, total_tokens_in, total_tokens_out, 0


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