import csv
import json
from google_play_scraper import search
import time

# 输入 CSV 文件名
INPUT_CSV = "target_unmatched_only.csv"
# 输出 JSON 文件名
OUTPUT_JSON = "apps_with_appId.json"
# 输出搜索失败 APP 的 JSON 文件
FAILED_JSON = "apps_search_failed.json"


def read_titles_from_csv(csv_file):
    """
    读取 CSV 文件中的 title_target 列
    返回列表
    """
    titles = []
    with open(csv_file, newline='', encoding='utf-8-sig') as f:  # 用 utf-8-sig 处理 BOM
        reader = csv.DictReader(f)
        print("CSV 字段名:", reader.fieldnames)  # 调试输出
        for row in reader:
            if 'title_target' in row:
                title = row['title_target'].strip()
                if title:
                    titles.append(title)
    return titles


def search_appId_for_titles(titles, lang='en', country='us', n_hits=3, sleep_sec=1):
    """
    根据 APP title 列表搜索 Google Play，获取 appId
    返回字典 {title: {appId, title, ...}}
    并返回搜索失败的 title 列表
    """
    results_dict = {}
    failed_titles = []

    for idx, title in enumerate(titles, 1):
        try:
            search_results = search(title, lang=lang, country=country, n_hits=n_hits)

            if search_results is None or len(search_results) == 0:
                results_dict[title] = None
                failed_titles.append(title)
                print(f"{idx}/{len(titles)} '{title}' 未找到应用")
                time.sleep(sleep_sec)
                continue

            best_match = search_results[0]
            app_id = best_match.get('appId')
            if app_id:
                results_dict[title] = {
                    'appId': app_id,
                    'title_found': best_match.get('title'),
                    'score': best_match.get('score'),
                    'url': f"https://play.google.com/store/apps/details?id={app_id}"
                }
                print(f"{idx}/{len(titles)} '{title}' 搜索成功: {app_id}")
            else:
                results_dict[title] = None
                failed_titles.append(title)
                print(f"{idx}/{len(titles)} '{title}' 搜索失败: 搜索结果中无 appId")
            time.sleep(sleep_sec)

        except Exception as e:
            print(f"{idx}/{len(titles)} 搜索 '{title}' 出错: {e}")
            results_dict[title] = None
            failed_titles.append(title)
            time.sleep(sleep_sec * 2)  # 出错时多等待

    return results_dict, failed_titles


def save_to_json(data, json_file):
    """
    保存数据为 JSON 文件
    """
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles = read_titles_from_csv(INPUT_CSV)
    print(f"共读取 {len(titles)} 个 APP title")

    appId_data, failed_titles = search_appId_for_titles(titles)

    save_to_json(appId_data, OUTPUT_JSON)
    print(f"搜索结果已保存到 {OUTPUT_JSON}")

    if failed_titles:
        print(f"共有 {len(failed_titles)} 个 APP 搜索失败，已保存到 {FAILED_JSON}")
        save_to_json(failed_titles, FAILED_JSON)
    else:
        print("所有 APP 搜索成功，没有失败记录。")


if __name__ == "__main__":
    main()
