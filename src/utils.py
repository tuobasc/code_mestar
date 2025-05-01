import json
import ast
import xml.etree.ElementTree as ET
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your api key",
    api_version="2024-10-21",
    azure_endpoint="https://hkust.azure-api.net",
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
        samples_info_list.append(f"assert {sample['input']} == {sample['output']}")
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


def get_tsp_length(sequence_file_path="tmp_result.json"):
    import math
    # 读取节点坐标数据
    path_list = find_tsp_files("data/tsplib-master")
    with open(sequence_file_path, "r") as file:
        sequence_lists = json.load(file)

    res = []
    for name in path_list:
        print(name)
        path = "data/tsplib-master/" + name
        with open(path, "r") as file:
            node_data = json.load(file)

        # 读取节点顺序
        sequence_list = sequence_lists[name.split(".")[0]]

        # 初始化路径长度
        total_length = 0.0

        # 遍历节点顺序，计算路径长度
        for i in range(len(sequence_list)):
            # 当前节点
            current_node = sequence_list[i]
            # 下一个节点（如果是最后一个节点，则回到第一个节点）
            next_node = sequence_list[(i + 1) % len(sequence_list)]

            # 获取当前节点和下一个节点的坐标
            x1, y1 = node_data[current_node]
            x2, y2 = node_data[next_node]

            # 计算欧式距离并累加到总长度
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            total_length += distance

        with open("data/tsplib-master/solutions.json", "r") as f:
            solutions = json.load(f)

        baseline_solution = solutions[name.split(".")[0]]
        # print("baseline_solution: ", baseline_solution)
        # print("total_length: ", total_length)
        res.append((baseline_solution - total_length) / baseline_solution)

    return sum(res) / len(res)

def find_tsp_files(directory):
    import os
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if "json" in file and "solution" not in file:
                file_list.append(file)
    return file_list

def get_element_text(element):
    """递归获取元素及其子元素的文本内容"""
    if element is None:
        return ""
    text = element.text or ""
    for child in element:
        text += get_element_text(child)
        if child.tail:
            text += child.tail
    return text.strip()


def extract_problem_and_algorithm(xml_str):
    start_index = xml_str.find("<root>")
    end_index = xml_str.rfind("</root>") + 7
    xml_str = xml_str[start_index:end_index]
    """从XML字符串中提取problem的描述、计划及algorithm内容"""
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return {"problem_descriptions": [],
                "problem_plans": [],
                "algorithm": ""
        }

    # 提取所有problem的描述和计划
    problems = root.findall('problem')
    descriptions = []
    plans = []
    for i, problem in enumerate(problems):
        desc_elem = problem.find('description')
        plan_elem = problem.find('planning')
        descriptions.append(f"Problem id: {i}\n" + get_element_text(desc_elem))
        plans.append(f"Problem id: {i}\n" + get_element_text(plan_elem))

    # 提取algorithm内容
    algorithm_elem = root.find('algorithm')
    algorithm = get_element_text(algorithm_elem)

    return {
        "problem_descriptions": descriptions,
        "problem_plans": plans,
        "algorithm": algorithm
    }