import json
import pandas as pd

# ================== 文件路径 ==================
EXCEL_PATH = "all_app.xlsx"     # 输入 Excel
JSON_PATH = "../GooglePlay_Scraper/app_details.json"  # JSON 文件
OUTPUT_PATH = "output.xlsx"     # 输出 Excel

# ================== 读取 Excel ==================
df = pd.read_excel(EXCEL_PATH)

# ================== 强制列类型 ==================
TEXT_COLUMNS = [
    "description",
    "released",
    "lastUpdatedOn",
    "url",
    "version"
]

for col in TEXT_COLUMNS:
    if col in df.columns:
        df[col] = df[col].astype("object")

# ================== 读取 JSON ==================
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

apps = data if isinstance(data, list) else [data]

# ================== 构建 title 映射 ==================
app_map = {
    app["title"]: app
    for app in apps
    if isinstance(app, dict) and "title" in app
}

# ================== 字段映射 ==================
FIELD_MAP = {
    "description": "description",
    "realInstalls": "realInstalls",
    "score": "score",
    "ratings": "ratings",
    "reviews": "reviews",
    "released": "released",
    "lastUpdatedOn": "lastUpdatedOn",
    "url": "url",
    "version": "version",
}

# ================== 填充数据 + 计数 ==================
matched_count = 0

for idx, row in df.iterrows():
    title = str(row.get("title")).strip()

    if title in app_map:
        matched_count += 1
        app = app_map[title]
        for excel_col, json_key in FIELD_MAP.items():
            if excel_col in df.columns:
                df.at[idx, excel_col] = app.get(json_key)

# ================== 保存 ==================
df.to_excel(OUTPUT_PATH, index=False)

print(f"处理完成：已生成 {OUTPUT_PATH}")
print(f"成功匹配并填充的条目数：{matched_count}")
