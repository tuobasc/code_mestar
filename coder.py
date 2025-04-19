from src.prompts import coder_prompt
from src.utils import request, parser_codes, sample_decoder
from nbconvert.preprocessors import ExecutePreprocessor
import ast
import traceback
import multiprocessing
import nbformat
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Coder:
    def __init__(self):
        self.input_tokens_counts = 0
        self.output_tokens_counts = 0

    def writing(self, problem_desc, plan, samples, additional_samples=None, notes=""):
        if additional_samples:
            samples_info = sample_decoder(samples + additional_samples)
        else:
            samples_info = sample_decoder(samples)
        coder_query = coder_prompt.format(problem_desc=problem_desc, plan=plan, samples=samples_info, notes=notes)
        code, input_tokens, output_tokens = request(coder_query)
        self.input_tokens_counts += input_tokens
        self.output_tokens_counts += output_tokens
        code = parser_codes(code)
        return code

    def run(self, code, samples, verbose=False):
        test_cases_main = [sample["input"] for sample in samples]
        test_cases_res = [sample["output"] for sample in samples]
        print("test_cases_main", test_cases_main)
        print("test_cases_res", test_cases_res)

        nb = nbformat.v4.new_notebook()
        code = "from typing import List, Tuple\n" + code
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

    def robust_run(self, code: str, samples: list[dict], timeout_sec: float = 10.0, verbose=False):
        """
        code    : a string defining your function, e.g.
                  "def add(a, b):\n    return a + b"
        samples : a list of {"input": "add(1,2)", "output": "3"}
        timeout_sec : max seconds per test call

        Returns: list of (passed: bool, expected, actual, error_msg_or_None)
        """
        # 1) Compile & exec the user code once
        namespace: dict = {}
        try:
            compiled = compile(code, "<user_code>", "exec")
            exec(compiled, namespace)
        except Exception:
            tb = traceback.format_exc()
            raise RuntimeError(f"Error defining your function:\n{tb}")

        results = []

        def target(expr, return_dict):
            """Helper to eval a single expression under time limit."""
            try:
                # Evaluate the call; if it returns None, we record None
                val = eval(expr, namespace)
                return_dict["result"] = val
                return_dict["error"] = None
            except Exception as e:
                return_dict["result"] = None
                return_dict["error"] = traceback.format_exc()

        for sample in samples:
            inp = sample["input"].strip()
            exp_txt = sample["output"].strip()

            # Try to parse expected literal:  "123" -> 123, "[1,2]" -> [1,2], etc.
            try:
                expected = ast.literal_eval(exp_txt)
            except Exception:
                expected = exp_txt

            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            p = multiprocessing.Process(target=target, args=(inp, return_dict))
            p.start()
            p.join(timeout_sec)
            if p.is_alive():
                p.terminate()
                actual = None
                error = f"Timed out after {timeout_sec}s"
            else:
                actual = return_dict.get("result", None)
                error = return_dict.get("error", None)

            # Compare
            passed = False
            if error is None:
                # exact match or numeric tolerance
                if actual == expected:
                    passed = True
                else:
                    try:
                        if (isinstance(actual, (int, float)) and
                                abs(actual - expected) < 1e-6):
                            passed = True
                    except Exception:
                        pass

            results.append((
                passed,
                expected,
                actual,
                error
            ))

            if verbose:
                print(f">>> {inp}")
                if error:
                    print("   ERROR:", error)
                else:
                    print("   got", actual, "| expected", expected,
                          "|", "PASS" if passed else "FAIL")

        return results