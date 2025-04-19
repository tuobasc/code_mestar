from src.prompts import planner_prompt, planner_confidence_prompt
from src.utils import request, parser_json, sample_decoder


class Planner:
    def __init__(self):
        self.plans = []
        self.input_tokens_counts = 0
        self.output_tokens_counts = 0

    def planning(self, problem_desc, samples, additional_samples=None, notes="", k_sample=5):
        knowledge_base = []
        early_stopping_control = False
        temperature_control = 0
        input_tokens_total = 0
        output_tokens_total = 0
        trys = 0

        if additional_samples:
            samples_info = sample_decoder(samples + additional_samples)
        else:
            samples_info = sample_decoder(samples)

        while not early_stopping_control and trys < k_sample:
            planner_query = planner_prompt.format(problem_desc=problem_desc, samples=samples_info, notes=notes)
            res, input_tokens, output_tokens = request(planner_query, temperature=temperature_control)
            input_tokens_total += input_tokens
            output_tokens_total += output_tokens
            plan = parser_json(res)["plan"]
            confidence_query = planner_confidence_prompt.format(problem_desc=problem_desc, plan=plan, notes=notes)
            res, input_tokens, output_tokens = request(confidence_query, temperature=temperature_control)
            confidence = parser_json(res)["confidence"]

            if confidence == 2:
                early_stopping_control = True
                print("Log: Find the adequate plan.")

            # update knowledge_base
            plan_info = {"plan": plan, "confidence": confidence, "temperature": temperature_control}
            knowledge_base.append(plan_info)

            temperature_control += 0.2
            if temperature_control > 0.81:
                temperature_control = 0.8
            trys += 1
        self.input_tokens_counts += input_tokens_total
        self.output_tokens_counts += output_tokens_total
        return knowledge_base

    def print_plans(self):
        print("Log: Plans")
        for i, plan in enumerate(self.plans):
            print("Plan id: ", i)
            print("plan_details: \n", plan["plan"])
            print("plan_confidence: ", plan["confidence"])
            print("--------------------------------------")