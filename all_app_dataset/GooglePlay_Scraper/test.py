import json

# JSON 文件路径
file_path = "app_details2.json"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # 如果是列表类型，统计长度
        if isinstance(data, list):
            print(f"文件中共有 {len(data)} 条记录")
        else:
            print("JSON 文件不是列表类型，无法统计条目数量")
except Exception as e:
    print(f"读取文件出错: {e}")
