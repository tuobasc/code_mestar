import json
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="7aecff8ad2084786a614da48e51f092d",
    api_version="2024-10-21",
    azure_endpoint="https://hkust.azure-api.net"
)

def request(content, temperature=0, model="gpt-4o-mini"):
    res = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "user", "content": content},
        ],
        temperature=temperature,
    )
    return res.choices[0].message.content, res.usage.prompt_tokens, res.usage.completion_tokens

def load_jsonl(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data

def parser_json(string):
    start_index = string.find("```json") + 7
    end_index = string.rfind("```")
    if start_index == -1 or end_index == -1:
        print("Warning: Fail to follow instruction")
        return ""
    json_str = string[start_index:end_index].strip()
    json_str = json.loads(json_str)
    return json_str

def parser_codes(string):
    start_index = string.find("```python") + 9
    end_index = string.rfind("```")
    if start_index == -1 or end_index == -1:
        print("Warning: Fail to follow instruction")
        return ""
    python_str = string[start_index:end_index].strip()
    return python_str

def sample_decoder(samples):
    samples_info_list = []
    for i, sample in enumerate(samples):
        samples_info_list.append(f"#### Case{i}")
        samples_info_list.append(f"assert {sample["input"]} == {sample['output']}")
        if 'explanation' in sample.keys():
            samples_info_list.append(f"Explanation: {sample['explanation']}")
    sample_info = "\n".join(samples_info_list)
    return sample_info