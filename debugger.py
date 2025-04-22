from src.prompts import debugger_debug_prompt, debugger_optimization_prompt, mapcoder_debugging_prompt
from src.utils import error_sample_decoder, request, parser_json, parser_codes


class Debugger:
    def __init__(self):
        self.input_tokens_total = 0
        self.output_tokens_total = 0

    def debug(self, problem_desc, plan, code, temperature=0, error_samples=None, model="gpt-4o-mini"):
        if error_samples:
            error_info = error_sample_decoder(error_samples)
            debugger_debug_query = debugger_debug_prompt.format(problem_desc=problem_desc, plan=plan, code=code,
                                                                error_samples=error_info)
        else:
            debugger_debug_query = debugger_optimization_prompt.format(problem_desc=problem_desc, plan=plan, code=code)

        rerun = True
        for _ in range(4):
            if rerun:
                try:
                    res, input_tokens, output_tokens = request(debugger_debug_query, temperature=temperature, model=model)
                    self.input_tokens_total += input_tokens
                    self.output_tokens_total += output_tokens
                    evolved = parser_json(res)
                    rerun = False
                    return evolved["revised_plan"], evolved["revised_code"]
                except Exception as e:
                    print(e)

        return "", ""



    def mapcoder_debug(self, algorithm, problem_desc, plan, code, temperature=0, model="gpt-4o-mini"):
        mapcoder_debugging_query = mapcoder_debugging_prompt.format(algorithm=algorithm, problem_desc=problem_desc, plan=plan, code=code)
        res, input_tokens, output_tokens = request(mapcoder_debugging_query, temperature=temperature, model=model)
        self.input_tokens_total += input_tokens
        self.output_tokens_total += output_tokens
        code = parser_codes(res)
        return code