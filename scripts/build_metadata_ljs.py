import os, pandas as pd

WAV_DIR = "data/wavs"
TXT_DIR = "data/transcripts"
OUT_ALL = "data/metadata.csv"
OUT_TRAIN = "data/metadata_train.csv"
OUT_VAL = "data/metadata_val.csv"

rows = []
missing = 0
for wav in sorted(os.listdir(WAV_DIR)):
    if not wav.lower().endswith(".wav"): 
        continue
    utt_id = os.path.splitext(wav)[0]     # e.g. 000123
    txt_path = os.path.join(TXT_DIR, utt_id + ".txt")
    if not os.path.exists(txt_path):
        missing += 1
        continue
    text = open(txt_path, "r", encoding="utf-8").read().strip()
    text = " ".join(text.split()).replace("|", ",")
    if len(text) < 2:
        continue
    # LJSpeech expects THREE columns: ID | raw_text | normalized_text
    # If you don't have a normalized version, duplicate the raw text.
    rows.append([utt_id, text, text])

print(f"Found {len(rows)} items. Missing transcripts: {missing}")

df = pd.DataFrame(rows)
# Write LJSpeech-style (no header)
df.to_csv(OUT_ALL, sep="|", index=False, header=False)

# Split train/val (90/10)
msk = (pd.Series(range(len(df))) % 10) != 0
df[msk].to_csv(OUT_TRAIN, sep="|", index=False, header=False)
df[~msk].to_csv(OUT_VAL,   sep="|", index=False, header=False)
print(f"Wrote {OUT_ALL}, {OUT_TRAIN}, {OUT_VAL}")
