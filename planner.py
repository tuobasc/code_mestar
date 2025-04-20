from src.prompts import planner_prompt, planner_confidence_prompt, planner_evolution_planning_prompt
from src.utils import request, parser_json, sample_decoder


class Planner:
    def __init__(self):
        self.plans = []
        self.input_tokens_counts = 0
        self.output_tokens_counts = 0

    def planning(self, problem_desc, base_plans, samples, additional_samples=None, notes="", k_sample=5, model="gpt-4o-mini", warm_up_degree=0.2):
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
            if len(base_plans) > 0:
                base_plan = base_plans[0]["plan"]
                planner_query = planner_evolution_planning_prompt.format(problem_desc=problem_desc, base_plan=base_plan, samples=samples_info, notes=notes)
                res, input_tokens, output_tokens = request(planner_query, temperature=temperature_control, model=model)
                plan = parser_json(res)["new_plan"]
            else:
                planner_query = planner_prompt.format(problem_desc=problem_desc, samples=samples_info, notes=notes)
                res, input_tokens, output_tokens = request(planner_query, temperature=temperature_control, model=model)
                plan = parser_json(res)["plan"]
            input_tokens_total += input_tokens
            output_tokens_total += output_tokens
            confidence_query = planner_confidence_prompt.format(problem_desc=problem_desc, plan=plan, notes=notes)
            res, input_tokens, output_tokens = request(confidence_query, temperature=temperature_control, model=model)
            confidence = parser_json(res)["confidence"]

            if confidence == 2:
                early_stopping_control = True
                print("Log: Find the adequate plan.")

            # update knowledge_base
            plan_info = {"plan": plan, "confidence": confidence, "temperature": temperature_control}
            knowledge_base.append(plan_info)

            temperature_control += warm_up_degree
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