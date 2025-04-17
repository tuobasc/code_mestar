### Notes for modification (compared with MapCoder)

1. 暂时去掉了Retrieval Stage, 直觉上很难评估且不如bootstrap (k sample)
2. 加入了角色扮演，更符合Multi-Agent的设置
3. 自动化生成sample I/O, 更符合现实，但不一定有这个能力？
4. early_stopping
5. feedback, not only test cases, but also instruction
6. benchmark, 可以考虑加上TSPLIB, 可能可以加上leetcode周赛，该场景对性能有要求
7. debugger可能用greedy search就足够, evolution减少幻觉
8. 可能会过拟合，因为只需要解决给出的examples即可

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

### Experiments
初步设想，对于可以select的方案，则允许从n个中submit 1个  
对于没有明确select的方案，则只要能满足sample，就submit，否则一直产生n个，标记为失败。  
即budget有上限，思考无上限，budget设为8似乎足够

#### Reference
MapCoder, CodeTree, EOH, FunSearch, LLMOptimization, PromptOptimization