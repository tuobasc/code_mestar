import json
import ast
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

def save_jsonl(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + "\n")

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

def error_sample_decoder(samples):
    samples_info_list = []
    for i, sample in enumerate(samples):
        samples_info_list.append(f"#### Case{i}")
        samples_info_list.append(f"Input: {sample['input']}")
        samples_info_list.append(f"Expected Output: {sample['output']}")
        if 'explanation' in sample.keys():
            samples_info_list.append(f"Explanation: {sample['explanation']}")
        samples_info_list.append(f"Current Output: {sample['program_output']}")
    return "\n".join(samples_info_list)

def identify(s):
    """
    判断输入字符串 s 是单个数值、列表，还是普通字符串。

    返回格式：(kind, value)
      - kind: 'number'、'list' 或 'string'
    """
    s_stripped = s.strip()
    try:
        val = ast.literal_eval(s_stripped)
    except (ValueError, SyntaxError):
        # 不能被解析为任何字面量
        return False

    # 解析成功，按类型区分
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, list):
        return True

    # 解析为其它 Python 类型（比如 dict、tuple、str 字面量等），
    # 我们均视作普通字符串
    return False