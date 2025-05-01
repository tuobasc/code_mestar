## The project for CSIT 6000R NLP

### Preparation:
Update api key in src/utils and prepare the environment:
```
!pip install nbconvert
!pip install ipykernel
```

### Run Dataset:
```
python main.py --counterfactual_think --verbose --dataset_name "MBPP_ET" --split_test_ratio 0.9 --method "code-master" --model "gpt-4o-mini" --greedy_search_iterations 3 --evolution_iterations 3
```

### Run TSPLIB:
```
python main_tsp.py --method "mapcoder" --model "gpt-4o-mini"
```

### Run Single Problem
Set the `problem_description`, `examples` and `test_examples` in `query.py`.
Call `query_code_master` function