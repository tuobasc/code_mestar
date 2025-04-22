### WorkFlow
Step0: Prepare. Counterfactual Thinker -> [insights]  
Step1: Planner -> [plan, confidence], select plan with high confidence  
Step2: Coder -> [code]  
Step3.1:  
if fail -> enter greedy search[better_plan, better_insights] -> better_insights  
if success -> jump, mission success  
Step3.2:  
if greedy search fail, enter evolution [different plan], enter Step1  
if get max_retry, jump, mission fail