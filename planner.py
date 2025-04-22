from src.prompts import (planner_prompt, planner_confidence_prompt, planner_evolution_planning_prompt, mapcoder_retrieval_prompt,
                         mapcoder_planning_prompt, mapcoder_confidence_generation_prompt)
from src.utils import request, parser_json, sample_decoder, extract_problem_and_algorithm


class Planner:
    def __init__(self):
        self.plans = []
        self.input_tokens_counts = 0
        self.output_tokens_counts = 0

    def planning(self, problem_desc, base_plan, samples=None, additional_samples=None, notes="", k_sample=3, model="gpt-4o-mini", warm_up_degree=0.2):
        knowledge_base = []
        early_stopping_control = False
        temperature_control = 0
        input_tokens_total = 0
        output_tokens_total = 0
        trys = 0

        if samples and additional_samples:
            samples_info = sample_decoder(samples + additional_samples)
        elif samples:
            samples_info = sample_decoder(samples)
        else:
            samples_info = ""


        while not early_stopping_control and trys < k_sample:
            if base_plan:
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

    def mapcoder_planning(self, problem_desc, samples=None, k_sample=3, model="gpt-4o-mini"):
        mapcoder_retrieval_query = mapcoder_retrieval_prompt.format(problem_desc=problem_desc)
        xml_res, input_tokens, output_tokens = request(mapcoder_retrieval_query, model=model)
        self.input_tokens_counts += input_tokens
        self.output_tokens_counts += output_tokens
        probs_algos = extract_problem_and_algorithm(xml_res)
        retrieval_probs = "\n".join(probs_algos["problem_descriptions"])
        retrieval_plans = "\n".join(probs_algos["problem_plans"])
        algorithm = probs_algos["algorithm"]
        if samples:
            samples_info = sample_decoder(samples)
        else:
            samples_info = ""

        local_plans = []
        for _ in range(k_sample):
            mapcoder_planning_query = mapcoder_planning_prompt.format(description=retrieval_probs, plans=retrieval_plans,
                                                  algorithm=algorithm, problem_desc=problem_desc, examples=samples_info)

            res, input_tokens, output_tokens = request(mapcoder_planning_query, model=model)
            self.input_tokens_counts += input_tokens
            self.output_tokens_counts += output_tokens
            plan = parser_json(res)["plan"]
            mapcoder_confidence_query = mapcoder_confidence_generation_prompt.format(problem_desc=problem_desc, plan=plan)
            res, input_tokens, output_tokens = request(mapcoder_confidence_query, model=model)
            self.input_tokens_counts += input_tokens
            self.output_tokens_counts += output_tokens
            confidence = int(parser_json(res)["confidence"])
            local_plans.append([plan, confidence])

        local_plans = sorted(local_plans, key=lambda x: x[1], reverse=True)
        return local_plans, algorithm