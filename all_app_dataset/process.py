import pandas as pd
import io

with open("all.csv", "rb") as f:
    text = f.read().decode("utf-8", errors="ignore")

df = pd.read_csv(io.StringIO(text))

df = df[df['title'].notna()]
df = df[df['title'].astype(str).str.strip() != ""]
df = df.drop_duplicates(subset='pkg_name', keep='first')

df.to_csv("all_cleaned.csv", index=False, encoding="utf-8")

print("处理完成")
