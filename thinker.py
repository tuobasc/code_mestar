from src.prompts import thinker_understand_prompt, thinker_normal_prompt, thinker_counter_prompt
from src.utils import request, parser_json, sample_decoder

class Thinker:
    def __init__(self, thinking_method="normal"):
        self.input_tokens_total = 0
        self.output_tokens_total = 0
        self.thinking_method = thinking_method
        assert self.thinking_method in ["normal", "counterfactual"], "Unknown thinking method"

    def understand(self, problem_desc, samples, model="gpt-4o-mini"):
        if not samples:
            return samples

        sample_info = sample_decoder(samples)
        thinker_understand_query = thinker_understand_prompt.format(problem_desc=problem_desc, samples=sample_info)
        res, input_tokens, output_tokens = request(thinker_understand_query, model=model)
        thoughts = parser_json(res)
        self.input_tokens_total += input_tokens
        self.output_tokens_total += output_tokens
        good_samples = []
        for sample, thought in zip(samples, thoughts):
            good_sample = dict()
            good_sample["input"] = sample["input"]
            good_sample["output"] = sample["output"]
            good_sample["explanation"] = thought["explanation"]
            good_samples.append(good_sample)

        return good_samples

    def specific_thinking(self, problem_desc, samples=None, model="gpt-4o-mini"):
        if samples:
            sample_info = sample_decoder(samples)
        else:
            sample_info = ""
        if self.thinking_method == "normal":
            thinker_thinking_query = thinker_normal_prompt.format(problem_desc=problem_desc, samples=sample_info)
            res, input_tokens, output_tokens = request(thinker_thinking_query, model=model)
            thoughts = parser_json(res)
            notes_list = []
            for thought in thoughts:
                notes_list.append(thought["strategy"])
            self.input_tokens_total += input_tokens
            self.output_tokens_total += output_tokens
            return [], "\n".join(notes_list)
        elif self.thinking_method == "counterfactual":
            thinker_thinking_query = thinker_counter_prompt.format(problem_desc=problem_desc, samples=sample_info)
            res, input_tokens, output_tokens = request(thinker_thinking_query, model=model)
            thoughts = parser_json(res)
            notes_list = []
            additional_samples = []
            for thought in thoughts:
                additional_sample = dict()
                additional_sample["input"] = thought["input"]
                additional_sample["output"] = thought["output"]
                additional_sample["explanation"] = thought["explanation"]
                notes_list.append(thought["notes"])
                additional_samples.append(additional_sample)
            self.input_tokens_total += input_tokens
            self.output_tokens_total += output_tokens
            return additional_samples, "\n".join(notes_list)
        else:
            return [], ""