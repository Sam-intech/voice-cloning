#!/usr/bin/env bash
set -e
source ../env/bin/activate  # adjust if needed
mkdir -p out
# Download a pretrained VITS English checkpoint to warm-start (example ID may vary):
tts --list_models | grep -i vits

# Replace MODEL_NAME with a concrete one you see listed, e.g.:
MODEL_NAME="tts_models/en/vctk/vits"

# Train/fine-tune:
tts --text "warmup" --model_name $MODEL_NAME --out_path out/warmup.wav || true

# Now launch trainer pointing to our config and dataset:
python -m TTS.bin.train_tts \
  --config_path training/config_vits.json \
  --model_name $MODEL_NAME \
  --output_path out
