import json
from google_play_scraper import app
from datetime import datetime
from time import sleep

# 输入 JSON 文件（包含所有 appId 的搜索结果）
INPUT_JSON = "apps_with_appId.json"
# 输出 JSON 文件路径（成功抓取）
OUTPUT_JSON = "app_details2.json"
# 输出 JSON 文件路径（抓取失败）
FAILED_JSON = "apps_failed2.json"


def fetch_app_details(app_id: str, csv_title='', lang='en', country='us') -> dict:
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

        # 保留 CSV 中的 title 信息
        result['csv_title'] = csv_title

        return result
    except Exception as e:
        print(f"[ERROR] Failed to fetch {app_id}: {e}")
        return {"appId": app_id, "csv_title": csv_title, "error": str(e)}


def main():
    # 读取 JSON 文件
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        search_results = json.load(f)

    all_app_details = []
    failed_apps = []

    for idx, (title, data) in enumerate(search_results.items(), 1):
        app_id = data.get('appId') if data else None
        if not app_id:
            # 没有 appId 也算失败，直接保存
            print(f"[WARN] {idx}/{len(search_results)} '{title}' 没有 appId")
            failed_apps.append({"appId": None, "csv_title": title, "error": "No appId in source JSON"})
            continue

        print(f"[INFO] Fetching {idx}/{len(search_results)}: {title} ({app_id})")
        details = fetch_app_details(app_id, csv_title=title)

        if 'error' in details:
            failed_apps.append(details)
        else:
            all_app_details.append(details)

        sleep(1)  # 避免请求过快

    # 保存成功抓取的应用详情
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_app_details, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Saved details for {len(all_app_details)} apps to {OUTPUT_JSON}")

    # 保存抓取失败的应用
    with open(FAILED_JSON, "w", encoding="utf-8") as f:
        json.dump(failed_apps, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Saved {len(failed_apps)} failed apps to {FAILED_JSON}")


if __name__ == "__main__":
    main()
