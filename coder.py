from src.prompts import coder_prompt
from src.utils import request, parser_codes, sample_decoder
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Coder:
    def __init__(self):
        self.input_tokens_counts = 0
        self.output_tokens_counts = 0

    def writing(self, problem_desc, plan, samples, notes=""):
        samples_info = sample_decoder(samples)
        coder_query = coder_prompt.format(problem_desc=problem_desc, plan=plan, samples=samples_info, notes=notes)
        code, input_tokens, output_tokens = request(coder_query)
        self.input_tokens_counts += input_tokens
        self.output_tokens_counts += output_tokens
        code = parser_codes(code)
        return code

    def run(self, code, samples, verbose=False):
        # Todo: 如果是开放式问题，例如CO，这里需要设计另一种test_case paradigm. 或者用另一个run函数
        test_cases_main = [sample["input"] for sample in samples]
        test_cases_res = [sample["output"] for sample in samples]
        print("test_cases_main", test_cases_main)
        print("test_cases_res", test_cases_res)

        nb = nbformat.v4.new_notebook()
        code_cell_function = nbformat.v4.new_code_cell(code)
        nb.cells.append(code_cell_function)

        # 记录 test cell 的下标，以便后面提取输出
        test_cell_indices = []

        for test in test_cases_main:
            code_cell_test = nbformat.v4.new_code_cell(test)
            test_cell_indices.append(len(nb.cells))  # 当前 test cell 的索引
            nb.cells.append(code_cell_test)

        ep = ExecutePreprocessor(kernel_name="python3", allow_errors=True)

        try:
            ep.preprocess(nb, {})  # 执行 notebook
        except Exception as e:
            print("执行 Notebook 过程中出现错误：", e)

        # 提取 test cell 的执行输出
        exec_res = []
        for idx in test_cell_indices:
            cell = nb.cells[idx]
            output_text = ""
            for output in cell.get("outputs", []):
                if output.output_type == "stream":
                    output_text += output.get("text", "")
                elif output.output_type == "execute_result":
                    output_text += output.get("data", {}).get("text/plain", "")
                elif output.output_type == "error":
                    tb = output.get("traceback", [])
                    if tb:
                        output_text += tb[-1]
            exec_res.append(output_text.strip())

        if verbose:
            print("Logs: Test cases")
            print("True: ", test_cases_res)
            print("Running: ", exec_res)
        pass_count = 0
        for t_res, r_res in zip(test_cases_res, exec_res):
            if t_res == r_res:
                pass_count += 1
            else:
                try:
                    if abs(float(t_res) - float(r_res)) < 1e-6:
                        pass_count += 1
                except Exception as e:
                    pass

        return test_cases_res, exec_res, pass_count