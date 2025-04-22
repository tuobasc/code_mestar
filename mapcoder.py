from coder import Coder
from debugger import Debugger
from planner import Planner
from src.utils import extract_problem_and_algorithm

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


def query_mapcoder(problem_desc, samples=None, test_samples=None, k_sample=3, model="gpt-4o-mini", greedy_search_iteration=3, optimization=False, verbose=False):
    planner = Planner()
    plans, algorithm = planner.mapcoder_planning(problem_desc, samples, k_sample, model)
    coder = Coder()
    debugger = Debugger()
    for plan in plans:
        if verbose:
            print("selected plan: ", plan[0])
            print("confidence: ", plan[1])
        code = coder.mapcoder_writing(algorithm, problem_desc, samples, model)
        if optimization:
            fast_tsp_run(code)
        else:
            sim_cases_res, run_res, pass_count = coder.run(code, samples)
            if pass_count == len(sim_cases_res):
                # submit
                if test_samples:
                    total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + debugger.input_tokens_total
                    total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + debugger.output_tokens_total
                    success, fitness = submit(coder, code, test_samples, verbose=verbose)
                    return success, total_tokens_in, total_tokens_out, fitness
                else:
                    total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + debugger.input_tokens_total
                    total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + debugger.output_tokens_total
                    return 1, total_tokens_in, total_tokens_out, 1
            else:
                # DEBUG
                for j in range(greedy_search_iteration):
                    evo_code = code
                    revised_code = debugger.mapcoder_debug(algorithm, problem_desc, plan, evo_code, temperature=0.2, model="gpt-4o-mini")
                    if verbose:
                        print("debug{j}, revised code: \n", revised_code)
                    sim_cases_res, run_res, pass_count = coder.run(revised_code, samples)
                    if pass_count == len(sim_cases_res):
                        # SUBMIT
                        if test_samples:
                            total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + debugger.input_tokens_total
                            total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + debugger.output_tokens_total
                            success, fitness = submit(coder, revised_code, test_samples, verbose=verbose)
                            return success, total_tokens_in, total_tokens_out, fitness
                        else:
                            total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + debugger.input_tokens_total
                            total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + debugger.output_tokens_total
                            return 1, total_tokens_in, total_tokens_out, 1
                    else:
                        evo_code = revised_code
    total_tokens_in = planner.input_tokens_counts + coder.input_tokens_counts + debugger.input_tokens_total
    total_tokens_out = planner.output_tokens_counts + coder.output_tokens_counts + debugger.output_tokens_total
    return 0, total_tokens_in, total_tokens_out, 0

# 示例用法
if __name__ == "__main__":
    xml_example = """
    balabala
    <root>
        <problem>
            <description>计算斐波那契数列第n项的值</description>
            <code>...</code>
            <planning>1. 确定递归基 2. 分解问题 3. 合并结果</planning>
        </problem>
        <problem>
            <description>查找数组中的最大值</description>
            <code>...</code>
            <planning>1. 遍历数组 2. 比较元素 3. 更新最大值</planning>
        </problem>
        <algorithm>
            动态规划适用于具有重叠子问题和最优子结构的问题。
            关键步骤包括：定义状态、状态转移方程、初始化及计算顺序。
        </algorithm>
    </root>
    """
    result = extract_problem_and_algorithm(xml_example)
    print(result)