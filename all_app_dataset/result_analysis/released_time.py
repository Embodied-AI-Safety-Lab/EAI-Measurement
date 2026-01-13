import pandas as pd

# 1. 读取 CSV 文件
df = pd.read_excel("output.xlsx")

# 2. 定义时间解析函数
def parse_to_year_month(x):
    if pd.isna(x):
        return None
    try:
        # pandas 自动识别多种日期格式
        dt = pd.to_datetime(x, errors="coerce", utc=True)
        if pd.isna(dt):
            return None
        return dt.strftime("%Y-%m")
    except Exception:
        return None

# 3. 对 released 字段进行格式化
df["released_ym"] = df["released"].apply(parse_to_year_month)

# 4. （可选）查看无法解析的记录
invalid_rows = df[df["released_ym"].isna()]
print(f"无法解析的日期数量：{len(invalid_rows)}")

# 5. 保存结果
df.to_csv("putput_datatime.csv", index=False)
