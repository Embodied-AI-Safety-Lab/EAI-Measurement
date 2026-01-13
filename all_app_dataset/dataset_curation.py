import csv

INPUT_FILE = "embodied_intelligence_app_candidates.csv"
OUTPUT_FILE = "embodied_intelligence_app_filtered.csv"

# ======================================================
# 1. 强排除分类（primaryGenre）
# ======================================================

EXCLUDED_GENRES = [
    "Games",
    "Food & Drink",
    "Photo & Video",
    "Travel",
    "News",
    "Music",
    "Books",
    "Shopping",
    "Medical",
    "Finance",
    "Social Networking",
    "Graphics & Design"
]

# ======================================================
# 2. TrackName 强排除关键词（英文）
# 规则：只要包含 → 直接删除
# ======================================================

EXCLUDED_NAME_KEYWORDS_EN = [

    # --- Entertainment / Media ---
    "game", "games", "gaming",
    "music", "song", "radio", "playlist",
    "movie", "film", "cinema", "tv", "show", "drama",
    "video editor", "photo editor", "filter",

    # --- Social / Dating ---
    "chat", "messenger", "dating", "meet",
    "social", "community", "forum", "club",

    # --- Lifestyle / Consumer Services ---
    "shopping", "shop", "mall", "order",
    "delivery", "takeaway",
    "restaurant", "food", "recipe",
    "hotel", "flight", "airline", "trip", "travel",
    "taxi", "ride", "uber", "lyft",

    # --- Sports / Fitness ---
    "sport", "sports",
    "fitness", "workout", "gym", "yoga", "run", "running",

    # --- Education (non-robotics) ---
    "math", "algebra", "geometry",
    "english", "dictionary", "vocabulary",
    "grammar", "language learning",
    "history", "geography", "biology", "chemistry",

    # --- Finance ---
    "bank", "banking",
    "finance", "financial",
    "stock", "stocks", "trading",
    "investment", "crypto", "wallet",

    # --- Medical / Health ---
    "medical", "medicine", "hospital",
    "doctor", "clinic", "patient", "healthcare",
    "pharmacy",

    # --- Generic Consumer Utilities ---
    "weather", "calendar",
    "alarm", "clock",
    "calculator",
    "notebook", "notes", "memo",
    "expense", "budget",

    # --- Beauty / Personal ---
    "beauty", "makeup", "cosmetic",
    "skincare", "hair",

    # --- Events ---
    "wedding", "marriage", "dating"
]

# ======================================================
# 3. TrackName 强排除关键词（中文）
# 规则：只要包含 → 直接删除
# ======================================================

EXCLUDED_NAME_KEYWORDS_ZH = [

    # --- 娱乐 / 内容 ---
    "游戏", "手游", "网游",
    "音乐", "歌曲", "歌单", "电台",
    "影视", "电影", "电视剧", "综艺",

    # --- 社交 / 聊天 ---
    "聊天", "交友", "社交", "约会",
    "社区", "论坛", "群聊", "俱乐部",

    # --- 生活 / 消费 ---
    "购物", "商城", "下单", "订单",
    "外卖", "点餐", "餐厅", "美食",
    "酒店", "机票", "航班",
    "旅行", "旅游", "出行",
    "打车", "顺风车",

    # --- 运动 / 健身 ---
    "运动", "健身", "瑜伽", "跑步", "体育",

    # --- 教育（非机器人） ---
    "数学", "英语", "单词", "词典",
    "语法", "翻译",
    "历史", "地理", "生物", "化学",
    "文言文",

    # --- 金融 ---
    "金融", "理财",
    "股票", "基金", "炒股",
    "数字货币", "钱包",

    # --- 医疗 ---
    "医疗", "医生", "医院", "诊所",
    "药", "健康",

    # --- 工具 / 消费级 ---
    "天气", "日历", "闹钟",
    "计算器", "记账", "备忘录", "笔记",

    # --- 美妆 / 个人 ---
    "美妆", "化妆", "护肤",

    # --- 事件 ---
    "婚礼", "相亲"
]

# ======================================================
# 4. 排除逻辑
# ======================================================

def should_exclude(row):
    # ---- Level 1: Genre ----
    genre = (row.get("primaryGenre") or "").strip()
    if genre in EXCLUDED_GENRES:
        return True

    # ---- Level 2: Track Name ----
    track_name = row.get("trackName") or ""
    track_name_lower = track_name.lower()

    for kw in EXCLUDED_NAME_KEYWORDS_EN:
        if kw in track_name_lower:
            return True

    for kw in EXCLUDED_NAME_KEYWORDS_ZH:
        if kw in track_name:
            return True

    return False

# ======================================================
# 5. 主过滤流程
# ======================================================

def filter_apps():
    with open(
        INPUT_FILE,
        newline="",
        encoding="utf-8",
        errors="ignore"   # <<< 关键修复点
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    kept = []
    removed = 0

    for row in rows:
        if should_exclude(row):
            removed += 1
        else:
            kept.append(row)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in kept:
            writer.writerow(row)

    print("=== Filtering Summary ===")
    print(f"Total input apps : {len(rows)}")
    print(f"Removed apps     : {removed}")
    print(f"Kept apps        : {len(kept)}")
    print(f"Output saved to  : {OUTPUT_FILE}")

# ======================================================
# 6. Entry
# ======================================================

if __name__ == "__main__":
    filter_apps()
