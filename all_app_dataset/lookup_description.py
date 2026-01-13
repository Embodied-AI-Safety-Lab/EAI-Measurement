import csv
import time
import requests
import sys

# ======================================================
# 1. 配置
# ======================================================

INPUT_FILE = "embodied_intelligence_app_filtered.csv"
OUTPUT_FILE = "embodied_intelligence_app_with_description.csv"

LOOKUP_URL = "https://itunes.apple.com/lookup"

HEADERS = {
    "User-Agent": "Embodied-Intelligence-Academic-Lookup/1.0"
}

BATCH_SIZE = 20            # Apple 官方可接受
RATE_LIMIT_SECONDS = 2.5   # 保守限流（≈ 24 req/min）

# ======================================================
# 2. Lookup API
# ======================================================

def lookup_by_track_ids(track_ids):
    params = {
        "id": ",".join(track_ids),
        "entity": "software"
    }
    r = requests.get(
        LOOKUP_URL,
        params=params,
        headers=HEADERS,
        timeout=20
    )
    r.raise_for_status()
    return r.json().get("results", [])

# ======================================================
# 3. 主流程
# ======================================================

def enrich_with_description():
    # ---------- 读取 Search 阶段结果 ----------
    with open(
        INPUT_FILE,
        newline="",
        encoding="utf-8",
        errors="ignore"
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} apps from search stage")

    # trackId -> 原始行（保留 country 等信息）
    base_info = {}
    track_ids = []

    for row in rows:
        tid = row.get("trackId")
        if tid:
            base_info[tid] = row
            track_ids.append(tid)

    print(f"Valid trackIds: {len(track_ids)}")

    enriched = []
    failed = 0

    # ---------- 批量 Lookup ----------
    for i in range(0, len(track_ids), BATCH_SIZE):
        batch = track_ids[i:i + BATCH_SIZE]

        try:
            results = lookup_by_track_ids(batch)

            # Lookup 返回的是一个 list，需要按 trackId 对齐
            for item in results:
                tid = str(item.get("trackId"))
                if tid not in base_info:
                    continue

                base = base_info[tid]

                enriched.append({
                    # ---- 原始字段 ----
                    "trackId": tid,
                    "bundleId": base.get("bundleId"),
                    "trackName": base.get("trackName"),
                    "sellerName": base.get("sellerName"),
                    "primaryGenre": base.get("primaryGenre"),
                    "country": base.get("country"),

                    # ---- Lookup 扩展字段 ----
                    "genres": ";".join(item.get("genres", [])),
                    "description": item.get("description"),
                    "version": item.get("version"),
                    "releaseNotes": item.get("releaseNotes"),
                    "supportedDevices": ";".join(item.get("supportedDevices", [])),
                    "minimumOsVersion": item.get("minimumOsVersion"),
                    "languages": ";".join(item.get("languageCodesISO2A", [])),
                })

            print(f"Lookup {i + 1}–{i + len(batch)} OK")

            time.sleep(RATE_LIMIT_SECONDS)

        except Exception as e:
            failed += len(batch)
            print(f"[ERROR] Batch {i}-{i+len(batch)}: {e}", file=sys.stderr)
            time.sleep(10)

    # ---------- 保存 ----------
    if not enriched:
        print("No data enriched, abort.")
        return

    fieldnames = enriched[0].keys()

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in enriched:
            writer.writerow(row)

    print("\n=== Lookup Summary ===")
    print(f"Input apps      : {len(track_ids)}")
    print(f"Enriched apps   : {len(enriched)}")
    print(f"Failed lookups  : {failed}")
    print(f"Saved to        : {OUTPUT_FILE}")

# ======================================================
# 4. Entry
# ======================================================

if __name__ == "__main__":
    enrich_with_description()

