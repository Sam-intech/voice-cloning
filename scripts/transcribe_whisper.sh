#!/usr/bin/env bash
set -e
OUTDIR="data/transcripts"
mkdir -p "$OUTDIR"
# Choose model: tiny/base/small/medium/large. Medium is a good balance.
MODEL="medium"

for f in data/chunks/*.wav; do
  base=$(basename "$f" .wav)
  whisper "$f" --model $MODEL --language en --task transcribe --output_format txt --output_dir "$OUTDIR"
  # mv "$OUTDIR/${base}.txt" "$OUTDIR/${base}.txt"
done
echo "Transcripts in $OUTDIR"



