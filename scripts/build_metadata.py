import os, pandas as pd

WAV_DIR = "data/chunks"
TXT_DIR = "data/transcripts"
OUT = "data/metadata.csv"

rows = []
for wav in sorted(os.listdir(WAV_DIR)):
  if not wav.endswith(".wav"): 
    continue
  base = os.path.splitext(wav)[0]
  txt_path = os.path.join(TXT_DIR, base + ".txt")
  if not os.path.exists(txt_path):
    continue
  with open(txt_path, "r", encoding="utf-8") as f:
    text = f.read().strip()
  # Basic cleaning
  text = " ".join(text.split())
  # Skip empty/1-char lines
  if len(text) < 2:
    continue
  # Relative path so trainer can find files
  rows.append([f"data/chunks/{wav}", text])

df = pd.DataFrame(rows, columns=["path", "text"])
df.to_csv(OUT, index=False, sep="|", header=False)

print(f"Wrote {len(df)} rows to {OUT}")
