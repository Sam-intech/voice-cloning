import os, sys, json, traceback
from pathlib import Path

MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else "tts_models/en/vctk/vits"
print(f"[1/6] Using model name: {MODEL_NAME}")

try:
    from TTS.api import TTS
    print("[2/6] Imported TTS.api.TTS successfully")
except Exception as e:
    print("[ERR] Import TTS failed")
    traceback.print_exc()
    sys.exit(1)

try:
    print("[3/6] Loading model (this may download weights, can take a while)...")
    tts = TTS(model_name=MODEL_NAME, gpu=False, progress_bar=False)
    print("[3/6] Model loaded.")
except Exception as e:
    print("[ERR] Loading model failed")
    traceback.print_exc()
    sys.exit(1)

try:
    cfg = getattr(tts.synthesizer, "tts_config", None)
    if cfg is None:
        raise RuntimeError("tts_config not found on synthesizer")
    if hasattr(cfg, "to_dict"):
        cfg_dict = cfg.to_dict()
    else:
        cfg_dict = dict(cfg)
    print("[4/6] Extracted config dict.")
except Exception as e:
    print("[ERR] Extracting config failed")
    traceback.print_exc()
    sys.exit(1)

# Minimal safe adjustments
cfg_dict.setdefault("audio", {})
cfg_dict["audio"]["sample_rate"] = 22050

cfg_dict["datasets"] = [{
    "formatter": "ljspeech",
    "path": "data",
    "meta_file_train": "metadata_train.csv",
    "meta_file_val":   "metadata_val.csv",
    "language": "en"
}]

cfg_dict.setdefault("batch_size", 16)
cfg_dict.setdefault("eval_batch_size", 8)
cfg_dict.setdefault("num_loader_workers", 2)
cfg_dict.setdefault("run_eval", True)
cfg_dict.setdefault("epochs", 200)
cfg_dict.setdefault("lr", 2e-4)
cfg_dict["output_path"] = "out"

# Normalize known list fields if present
for key in ("text_cleaner", "test_sentences", "phoneme_language", "speaker_mapping"):
    if key in cfg_dict and not isinstance(cfg_dict[key], list):
        cfg_dict[key] = [cfg_dict[key]]

try:
    Path("training").mkdir(parents=True, exist_ok=True)
    out_path = Path("training/config_vits.json")
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(cfg_dict, f, indent=2, ensure_ascii=False)
    print(f"[5/6] Wrote config to {out_path.resolve()}")
except Exception as e:
    print("[ERR] Writing config failed")
    traceback.print_exc()
    sys.exit(1)

print("[6/6] Done.")
