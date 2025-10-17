#!/usr/bin/env bash
set -euo pipefail

# 1) Show which Python we're using (should be your conda env)
echo "Using python: $(which python)"
python -c "import sys; print('Python', sys.version)"

# 2) Sanity checks
test -f training/config_vits.json || { echo "Missing training/config_vits.json"; exit 1; }
test -f data/metadata_train.csv || { echo "Missing data/metadata_train.csv"; exit 1; }
test -f data/metadata_val.csv   || { echo "Missing data/metadata_val.csv"; exit 1; }

mkdir -p out

# 3) Start training FROM SCRATCH for now (we can switch to fine-tune later)
#    The config points to data/metadata_* and audio params we set earlier.
python -m TTS.bin.train_tts \
  --config_path training/config_vits.json \
  --output_path out
