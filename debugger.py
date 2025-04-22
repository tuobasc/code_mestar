from src.prompts import debugger_debug_prompt, debugger_optimization_prompt
from src.utils import error_sample_decoder, request, parser_json

class Debugger:
    def __init__(self):
        self.input_tokens_total = 0
        self.output_tokens_total = 0

    def debug(self, problem_desc, plan, code, error_samples=None, model="gpt-4o-mini"):
        if error_samples:
            error_info = error_sample_decoder(error_samples)
            debugger_debug_query = debugger_debug_prompt.format(problem_desc=problem_desc, plan=plan, code=code,
                                                                error_samples=error_info)
        else:
            debugger_debug_query = debugger_optimization_prompt.format(problem_desc=problem_desc, plan=plan, code=code)
        res, input_tokens, output_tokens = request(debugger_debug_query, model=model)
        self.input_tokens_total += input_tokens
        self.output_tokens_total += output_tokens
        evolved = parser_json(res)
        return evolved["revised_plan"], evolved["revised_code"]
