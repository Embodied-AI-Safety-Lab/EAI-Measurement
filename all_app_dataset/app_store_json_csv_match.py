import pandas as pd
import json

# ========= 1. 文件路径 =========
csv_path = "embodied_intelligence_app_candidates.csv"
json_path = "GooglePlay_Scraper/apps_failed2.json"

matched_csv_path = "app_store_json_csv_matched_apps.csv"
unmatched_csv_path = "app_store_json_csv_unmatched_apps.csv"

# ========= 2. 读取 CSV =========
df_csv = pd.read_csv(csv_path, encoding="gbk")

# CSV 中 APP 名称字段（根据你的实际字段名修改）
csv_app_col = "trackName"

# ========= 3. 读取 JSON =========
with open(json_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)

# JSON 中 APP 名称字段（根据你的实际字段名修改）
json_app_col = "csv_title"

# 提取 JSON 中的 APP name 列表
json_apps = {item[json_app_col] for item in json_data if json_app_col in item}

# ========= 4. 匹配：CSV ∩ JSON =========
matched_df = df_csv[df_csv[csv_app_col].isin(json_apps)]

# 保存匹配到的 CSV（表头保持不变）
matched_df.to_csv(matched_csv_path, index=False, encoding="utf-8-sig")

# ========= 5. 未匹配：JSON - CSV =========
csv_apps = set(df_csv[csv_app_col].dropna())

unmatched_apps = sorted(json_apps - csv_apps)

# 只保存 APP title/name
unmatched_df = pd.DataFrame(unmatched_apps, columns=["app_title"])

unmatched_df.to_csv(unmatched_csv_path, index=False, encoding="utf-8-sig")

print("处理完成：")
print(f"- 匹配到的 APP 已保存到 {matched_csv_path}")
print(f"- 未匹配到的 APP 已保存到 {unmatched_csv_path}")
