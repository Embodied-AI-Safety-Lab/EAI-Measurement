import requests
import time
import csv
import sys
from urllib.parse import quote_plus

# =========================
# 1. 全局配置
# =========================

BASE_URL = "https://itunes.apple.com/search"
HEADERS = {
    "User-Agent": "Embodied-Intelligence-Academic-Crawler/1.0"
}

# 官方限制 ~20 次/分钟，这里保守
RATE_LIMIT_SECONDS = 3.5

COUNTRIES = ["us", "cn", "jp", "de", "kr", "fr", "gb"]

OUTPUT_FILE = "embodied_intelligence_app_candidates2.csv"

# =========================
# 2. 具身智能关键词本体（大规模中英文）
# =========================

KEYWORDS = [ # -------- Robotics / Embodiment --------
    "robot", "robotics", "humanoid", "android", "cobot",
    "service robot", "industrial robot", "mobile robot",
    "autonomous robot",

    "机器人", "人形机器人", "服务机器人", "工业机器人",
    "协作机器人", "自主机器人",

    # -------- Mobility --------
    "drone", "uav", "quadcopter", "rover",
    "agv", "amr", "autonomous vehicle",

    "无人机", "无人车", "自动驾驶",
    # -------- Perception --------
    "computer vision", "vision", "camera", "lidar",
    "slam", "mapping", "localization",
    "object detection", "tracking", "pose estimation",

    "计算机视觉", "激光雷达", "SLAM", "定位", "建图",

    # -------- Action / Control --------
    "motion control", "navigation", "path planning",
    "robot arm", "robot hand", "grasp", "manipulation",
    "servo", "actuator", "motor control",

    "运动控制", "机械臂", "机械手", "抓取", "执行器",

    # -------- Intelligence --------
    "artificial intelligence", "ai", "autonomy",
    "reinforcement learning",
    "human robot interaction", "hri",

    "人工智能", "强化学习", "人机交互",

    # -------- Software / Dev --------
    "ros", "ros2", "robot operating system",
    "robot simulation", "gazebo", "webots",

    "机器人操作系统", "机器人仿真",

    # -------- Hardware / Kits --------
    "arduino", "raspberry pi", "jetson",
    "robot kit", "stem robot",

    "嵌入式", "机器人套件", "智能硬件"
                            
    "embodied",

    "人工智能", "具身智能",

    # ---------- Robotics Software / Dev ----------
    "ros", "MagicBot",
    # Chinese / Mixed
    "Unitree", "宇树",
    "AgileX", "松灵",
    "ARX", "方舟无限",
    "Boston Dynamics", "波士顿动力",
    "DexRobot", "灵巧智能",
    "Galaxea", "星海图",
    "优必选", "UBTECH",
    "云深处", "DeepRobotics",
    "智元机器人",
    "Fourier Intelligence", "傅利叶智能",
    "CloudMinds", "达闼",
    "Pudu Robotics", "普渡科技",
    "小米", "Xiaomi",
    "DJI", "大疆",
    "ECOVACS", "科沃斯",

    # Global
    "PAL Robotics",
    "Honda ASIMO",
    "Rainbow Robotics",
    "Hyundai Robotics",
    "Sanctuary AI",
    "1X Technologies",
    "ANYbotics",
    "Figure AI",
    "Apptronik",
    "Elephant Robotics",
    "Tesla Optimus",
    "Agility Robotics",
    "Digit robot",
    "Skild AI",
    "Physical Intelligence",

    # NVIDIA Robotics Stack
    "NVIDIA Robotics",
    "NVIDIA Isaac",

    "优傲",
    "Jetson",

    "remote control",
    "abb 机器人", "灵心巧手", "银河通用", "galbot", "星动纪元", "加速进化", "松应科技", "光轮智能",
    "求之科技", "穹彻智能", "具身风暴", "众擎机器人", "帕西尼", "千寻智能", "逐际动力", "limxdynamics",
    "开普勒", "gotokeple", "有鹿机器人",
    "星尘智能",
    "自变量机器人",
    "普渡", "PUDU",
    "乐聚机器人",
    "小鹏机器人",
    "具微科技", "Micro Robotech",
    "镜识科技", "Mirrormetech",
    "PNDbotics",
    "松延动力",
    "维他动力",

]

# ---------- 字母 / 数字枚举 ----------
ENUM_TERMS = list("")

SEARCH_TERMS = KEYWORDS + ENUM_TERMS


# =========================
# 3. Search API 调用
# =========================

def search_apps(term, country, limit=200):
    params = {
        "term": term,
        "country": country,
        "media": "software",
        "entity": "software",
        "limit": limit
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()
    return response.json().get("results", [])


# =========================
# 4. 主爬取逻辑（去重）
# =========================

def crawl_candidate_app_ids():
    seen = {}  # key: trackId or bundleId

    total_requests = 0

    for country in COUNTRIES:
        print(f"\n=== Country: {country} ===")

        for term in SEARCH_TERMS:
            try:
                results = search_apps(term, country)
                total_requests += 1

                print(
                    f"[{country}] term='{term}' "
                    f"-> {len(results)} results "
                    f"(req #{total_requests})"
                )

                for app in results:
                    track_id = app.get("trackId")
                    bundle_id = app.get("bundleId")

                    key = track_id or bundle_id
                    if not key:
                        continue

                    if key not in seen:
                        seen[key] = {
                            "trackId": track_id,
                            "bundleId": bundle_id,
                            "trackName": app.get("trackName"),
                            "primaryGenre": app.get("primaryGenreName"),
                            "sellerName": app.get("sellerName"),
                            "country": country
                        }

                time.sleep(RATE_LIMIT_SECONDS)

            except Exception as e:
                print(f"[ERROR] {country} | {term} | {e}", file=sys.stderr)
                time.sleep(10)

    return seen


# =========================
# 5. 保存候选集
# =========================

def save_candidates(apps, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "trackId",
                "bundleId",
                "trackName",
                "primaryGenre",
                "sellerName",
                "country"
            ]
        )
        writer.writeheader()

        for app in apps.values():
            writer.writerow(app)


# =========================
# 6. 主入口
# =========================

if __name__ == "__main__":
    print("Starting embodied intelligence App Store crawl...")
    candidates = crawl_candidate_app_ids()
    print(f"\nTotal unique candidate apps: {len(candidates)}")
    save_candidates(candidates, OUTPUT_FILE)
    print(f"Saved to: {OUTPUT_FILE}")

