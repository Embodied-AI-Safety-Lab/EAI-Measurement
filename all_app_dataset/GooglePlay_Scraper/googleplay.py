import pandas as pd
import json
from google_play_scraper import app
from datetime import datetime
from time import sleep

# 输入 CSV 文件路径
CSV_FILE = "target_matched_only.csv"
# 输出 JSON 文件路径
OUTPUT_JSON = "app_details.json"

def fetch_app_details(app_id: str, lang='en', country='us') -> dict:
    """
    获取 Google Play 应用的所有字段信息，并处理时间字段
    """
    try:
        result = app(app_id, lang=lang, country=country)

        # 处理更新时间：将 Unix 时间戳转换为可读日期
        if 'updated' in result and isinstance(result['updated'], int):
            result['updatedDate'] = datetime.fromtimestamp(result['updated']).strftime('%Y-%m-%d %H:%M:%S')
        else:
            result['updatedDate'] = None

        # 处理发布日期
        if 'released' in result and isinstance(result['released'], str):
            result['releasedDate'] = result['released']
        else:
            result['releasedDate'] = None

        return result
    except Exception as e:
        print(f"[ERROR] Failed to fetch {app_id}: {e}")
        return {"appId": app_id, "error": str(e)}

def main():
    # 读取 CSV 文件
    df = pd.read_csv(CSV_FILE)
    print(f"[INFO] {len(df)} apps loaded from {CSV_FILE}")

    all_app_details = []

    for idx, row in df.iterrows():
        pkg_name = row['pkg_name']
        title = row.get('title', '')
        print(f"[INFO] Fetching {idx+1}/{len(df)}: {title} ({pkg_name})")

        details = fetch_app_details(pkg_name)
        # 可以保留 CSV 的 title 信息
        details['csv_title'] = title

        all_app_details.append(details)

        # 建议加点延时，防止请求过快被封
        sleep(1)

    # 保存为 JSON 文件
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_app_details, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Saved details for {len(all_app_details)} apps to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
