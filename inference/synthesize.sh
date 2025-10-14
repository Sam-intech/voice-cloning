#!/usr/bin/env bash
set -e
source ../env/bin/activate
CHECKPOINT=$(ls -t out/*/*.pth | head -n 1)
echo "Using checkpoint: $CHECKPOINT"
tts --text "This is a test of the cloned voice." \
    --model_path "$CHECKPOINT" \
    --out_path inference/test.wav || echo "Direct synth may require model_name pairing."
