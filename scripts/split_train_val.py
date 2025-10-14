# scripts/05_split_train_val.py
import pandas as pd, numpy as np

df = pd.read_csv("data/metadata.csv", sep="|", header=None, names=["path","text"])
msk = np.random.rand(len(df)) < 0.9
df[msk].to_csv("data/metadata_train.csv", sep="|", header=False, index=False)
df[~msk].to_csv("data/metadata_val.csv",   sep="|", header=False, index=False)
print("Train/val written.")
