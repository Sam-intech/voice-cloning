#!/usr/bin/env bash
set -e
IN_DIR="data/raw"
OUT_DIR="data/processed"
mkdir -p "$OUT_DIR"

shopt -s nullglob
for f in "$IN_DIR"/*; do
  base=$(basename "$f")
  out="$OUT_DIR/${base%.*}.wav"
  ffmpeg -y -i "$f" -ac 1 -ar 22050 -c:a pcm_s16le "$out"
done
echo "Converted to mono 22.05kHz WAV in $OUT_DIR"



