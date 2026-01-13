import pandas as pd

# ---------- 读取数据 ----------
app_df = pd.read_csv(
    "embodied_intelligence_app_candidates.csv",
    encoding="latin1",
    engine="python"
)

target_df = pd.read_csv(
    "target_unmatched_only.csv",
    encoding="utf-8-sig"
)

# ---------- 类型统一 ----------
app_df["trackName"] = app_df["trackName"].astype(str)
target_df["title_target"] = target_df["title_target"].astype(str)

# ---------- 构建匹配条件（注意方向） ----------
mask_matched = target_df["title_target"].isin(app_df["trackName"])

# ---------- 按 target 进行拆分 ----------
target_matched_df = target_df[mask_matched].copy()
target_unmatched_df = target_df[~mask_matched].copy()

# ---------- 保存结果 ----------
target_matched_df.to_csv(
    "target_matched_from_unmatched.csv",
    index=False,
    encoding="utf-8-sig"
)

target_unmatched_df.to_csv(
    "target_still_unmatched.csv",
    index=False,
    encoding="utf-8-sig"
)

# ---------- 输出统计 ----------
print("target_unmatched_only 再匹配完成")
print("target 总行数:", len(target_df))
print("新匹配到的行数:", len(target_matched_df))
print("仍未匹配的行数:", len(target_unmatched_df))
