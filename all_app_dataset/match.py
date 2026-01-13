import pandas as pd
import unicodedata
import re

# ---------- 标题规范化函数 ----------
def normalize(text):
    if text is None:
        return ""
    text = str(text)
    # 去 BOM、换行
    text = text.replace("\ufeff", "").replace("\r", "").replace("\n", "")
    # Unicode 规范化（全角半角、兼容字符）
    text = unicodedata.normalize("NFKC", text)
    # 去 Excel 常见引号
    text = text.strip().strip('"').strip("'")
    # 去不可见空白字符
    text = re.sub(r"[\u00a0\u200b\u200e\u200f]", "", text)
    # 多空格压缩为一个
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------- 读取 all_cleaned.csv ----------
df_all = pd.read_csv(
    "all_cleaned.csv",
    encoding="latin1",      # 防止 UTF-8 解码失败
    engine="python"
)
df_all['__title_norm__'] = df_all['title'].apply(normalize)

# ---------- 读取 Excel target.xlsx ----------
df_target = pd.read_excel("target.xlsx", engine="openpyxl")
df_target['__title_norm__'] = df_target['title'].apply(normalize)

# ---------- 标记匹配 ----------
df_merged = pd.merge(
    df_target,
    df_all,
    on='__title_norm__',
    how='left',
    suffixes=('_target', '_all')
)

df_merged['matched'] = ~df_merged['title_all'].isna()

# ---------- 分离匹配 / 未匹配 ----------
df_matched = df_merged[df_merged['matched']].copy()
df_unmatched = df_merged[~df_merged['matched']].copy()

# ---------- 删除辅助列 ----------
for df in (df_merged, df_matched, df_unmatched):
    df.drop(columns='__title_norm__', inplace=True)

# ---------- 保存结果 ----------
df_merged.to_csv(
    "target_matched_full.csv",
    index=False,
    encoding="utf-8-sig"
)

df_matched.to_csv(
    "target_matched_only.csv",
    index=False,
    encoding="utf-8-sig"
)

df_unmatched.to_csv(
    "target_unmatched_only.csv",
    index=False,
    encoding="utf-8-sig"
)

# ---------- 输出统计 ----------
total_rows = len(df_target)
matched_count = len(df_matched)
unmatched_count = len(df_unmatched)

print("匹配完成")
print("target 总行数:", total_rows)
print("匹配到的行数:", matched_count)
print("未匹配到的行数:", unmatched_count)
