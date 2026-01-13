import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 读取数据
df = pd.read_csv("putput_datatime.csv")

# 时间字段
df["released_dt"] = pd.to_datetime(df["released_ym"], format="%Y-%m")

# 类别映射
label_map = {
    1: "Cleaning Robots",
    2: "Service Robots",
    3: "Lawn Mowing Robots",
    4: "Drones",
    5: "Education & Companion Robots",
    6: "Industrial & Agricultural",
    7: "Wearable Devices",
    8: "Embodied Intelligent Robots"
}

# 映射为英文类别
df["category_en"] = df["label"].map(label_map)

# 可选：检查是否有未映射成功的类别
print(df[df["category_en"].isna()]["label"].unique())


g = sns.FacetGrid(
    df,
    col="category_en",
    col_wrap=4,          # 8 类 → 2 × 4
    height=3,
    sharex=True,
    sharey=True
)

g.map_dataframe(
    sns.histplot,
    x="released_dt",
    bins=20,
    stat="count",        # 如果要看比例，改为 stat="density"
    color="steelblue"
)

g.set_axis_labels("Released Time", "APP Count")
g.set_titles("{col_name}")
g.fig.subplots_adjust(top=0.88)
g.fig.suptitle("Released Time Distribution")


plt.savefig("datatime_figure.png")
plt.show()

