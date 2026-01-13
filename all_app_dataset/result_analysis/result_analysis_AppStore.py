import json
import pandas as pd

# ================== 文件路径 ==================
EXCEL_PATH = "all_app.xlsx"
GP_JSON_PATH = "../GooglePlay_Scraper/app_details.json"      # Google Play JSON
APPSTORE_JSON_PATH = "../app-store-scraper/data/raw/merged_apps2.json"  # App Store JSON
OUTPUT_PATH = "output.xlsx"

# ================== 读取 Excel ==================
df = pd.read_excel(EXCEL_PATH)

# ================== 强制列类型 ==================
TEXT_COLUMNS = ["description", "released", "lastUpdatedOn", "url", "version"]
for col in TEXT_COLUMNS:
    if col in df.columns:
        df[col] = df[col].astype("object")

# ================== 读取 JSON ==================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"JSON 格式不正确: {path}")

gp_apps = load_json(GP_JSON_PATH)
appstore_apps = load_json(APPSTORE_JSON_PATH)

# ================== App Store 字段映射 ==================
def map_appstore_to_excel(app):
    """把 App Store JSON 字段映射为 Excel 列名"""
    return {
        "title": app.get("title"),
        "description": app.get("description"),
        "realInstalls": None,                 # App Store 没有此字段
        "score": app.get("score"),
        "ratings": app.get("reviews"),        # 双列都填
        "reviews": app.get("reviews"),
        "released": app.get("released"),
        "lastUpdatedOn": app.get("updated"),
        "url": app.get("url"),
        "version": app.get("version"),
    }

# ================== 合并所有 app ==================
all_apps = []

# Google Play 原始字段直接使用
for app in gp_apps:
    all_apps.append(app)

# App Store 映射字段
for app in appstore_apps:
    mapped_app = map_appstore_to_excel(app)
    all_apps.append(mapped_app)

# ================== 构建 title 映射 ==================
app_map = {app["title"]: app for app in all_apps if app.get("title")}

# ================== 填充数据 + 计数 ==================
matched_count = 0
for idx, row in df.iterrows():
    title = str(row.get("title")).strip()
    if title in app_map:
        matched_count += 1
        app = app_map[title]
        for col in ["description","realInstalls","score","ratings","reviews","released","lastUpdatedOn","url","version"]:
            if col in df.columns:
                df.at[idx, col] = app.get(col)

# ================== 保存 ==================
df.to_excel(OUTPUT_PATH, index=False)
print(f"处理完成：已生成 {OUTPUT_PATH}")
print(f"成功匹配并填充的条目数：{matched_count}")
