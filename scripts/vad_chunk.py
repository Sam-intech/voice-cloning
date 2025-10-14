# import os, wave, contextlib, webrtcvad, collections, sys
# from pydub import AudioSegment

# IN_DIR = "data/processed"
# OUT_DIR = "data/chunks"
# TARGET_LEN_MAX = 10.0  # seconds
# TARGET_LEN_MIN = 2.0   # seconds
# VAD_AGGRESSIVENESS = 2 # 0-3 (higher = stricter speech)

# os.makedirs(OUT_DIR, exist_ok=True)
# vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

# def read_pcm16(wav_path):
#     audio = AudioSegment.from_wav(wav_path)
#     if audio.frame_rate != 22050 or audio.channels != 1:
#         audio = audio.set_frame_rate(22050).set_channels(1)
#     raw = audio.raw_data
#     return raw, audio.frame_rate

# def frame_generator(frame_ms, audio_bytes, sample_rate):
#     nbytes = int(sample_rate * (frame_ms/1000.0) * 2)  # 16-bit mono
#     for i in range(0, len(audio_bytes), nbytes):
#         yield audio_bytes[i:i+nbytes]

# def vad_collector(sample_rate, frame_ms, padding_ms, frames):
#     num_padding = int(padding_ms / frame_ms)
#     ring = collections.deque(maxlen=num_padding)
#     triggered = False
#     voiced_frames = []
#     for frame in frames:
#         is_speech = vad.is_speech(frame, sample_rate)
#         if not triggered:
#             ring.append((frame, is_speech))
#             if sum(1 for f,s in ring if s) > 0.9 * ring.maxlen:
#                 triggered = True
#                 voiced_frames.extend(f for f,s in ring)
#                 ring.clear()
#         else:
#             voiced_frames.append(frame)
#             ring.append((frame, is_speech))
#             if sum(1 for f,s in ring if not s) > 0.9 * ring.maxlen:
#                 triggered = False
#                 yield b"".join(voiced_frames)
#                 ring.clear()
#                 voiced_frames = []
#     if voiced_frames:
#         yield b"".join(voiced_frames)

# idx = 1
# for fname in sorted(os.listdir(IN_DIR)):
#     if not fname.lower().endswith(".wav"): continue
#     path = os.path.join(IN_DIR, fname)
#     raw, sr = read_pcm16(path)

#     frames = list(frame_generator(30, raw, sr))  # 30ms frames
#     for chunk in vad_collector(sr, 30, 300, frames):
#         # save temporary chunk
#         tmp_path = os.path.join(OUT_DIR, f"tmp_{idx:06d}.wav")
#         audio = AudioSegment(
#             data=chunk, sample_width=2, frame_rate=sr, channels=1
#         )
#         dur = audio.duration_seconds
#         if dur >= TARGET_LEN_MIN:
#             if dur > TARGET_LEN_MAX:
#                 # split long chunks into ~<=10s
#                 pieces = int(dur // TARGET_LEN_MAX) + 1
#                 step = dur / pieces
#                 for p in range(pieces):
#                     start = int(p*step*1000); end = int(min((p+1)*step*1000, dur*1000))
#                     seg = audio[start:end]
#                     seg.export(os.path.join(OUT_DIR, f"{idx:06d}.wav"), format="wav")
#                     idx += 1
#             else:
#                 audio.export(os.path.join(OUT_DIR, f"{idx:06d}.wav"), format="wav")
#                 idx += 1

# print("VAD chunks saved to", OUT_DIR)

# ============================================================================================================================================================================================================

# scripts/vad_chunk.py
import os, collections
from pydub import AudioSegment
import webrtcvad

IN_DIR = "data/processed"
OUT_DIR = "data/chunks"
os.makedirs(OUT_DIR, exist_ok=True)

# VAD params
FRAME_MS = 30              # 10, 20, or 30 ms only
PADDING_MS = 300           # hangover padding
VAD_AGGR = 2               # 0..3 (higher = stricter)
TARGET_LEN_MIN = 2.0       # seconds
TARGET_LEN_MAX = 10.0      # seconds

# TTS sample rate target for saved clips
TTS_SR = 22050

vad = webrtcvad.Vad(VAD_AGGR)

def frame_generator(frame_ms, audio_bytes, sample_rate):
    # 16-bit mono PCM => 2 bytes per sample
    bytes_per_frame = int(sample_rate * (frame_ms / 1000.0) * 2)
    for i in range(0, len(audio_bytes), bytes_per_frame):
        frame = audio_bytes[i:i+bytes_per_frame]
        if len(frame) == bytes_per_frame:
            yield frame

def vad_collector(sample_rate, frame_ms, padding_ms, frames):
    num_padding_frames = int(padding_ms / frame_ms)
    ring = collections.deque(maxlen=num_padding_frames)
    voiced_frames = []
    triggered = False

    for frame in frames:
        is_speech = vad.is_speech(frame, sample_rate)

        if not triggered:
            ring.append((frame, is_speech))
            if sum(1 for _, s in ring if s) > 0.9 * ring.maxlen:
                triggered = True
                voiced_frames.extend(f for f, _ in ring)
                ring.clear()
        else:
            voiced_frames.append(frame)
            ring.append((frame, is_speech))
            if sum(1 for _, s in ring if not s) > 0.9 * ring.maxlen:
                triggered = False
                yield b"".join(voiced_frames)
                voiced_frames = []
                ring.clear()

    if voiced_frames:
        yield b"".join(voiced_frames)

idx = 1
for fname in sorted(os.listdir(IN_DIR)):
    if not fname.lower().endswith(".wav"):
        continue
    path = os.path.join(IN_DIR, fname)

    # Load your processed file (likely 22050 Hz, mono)
    audio_22k = AudioSegment.from_wav(path).set_channels(1).set_frame_rate(TTS_SR)

    # Make a 16 kHz version for VAD (webrtcvad requirement)
    audio_16k = audio_22k.set_frame_rate(16000)
    raw_16k = audio_16k.raw_data
    sr_vad = 16000

    # Build 30 ms frames and run VAD
    frames = list(frame_generator(FRAME_MS, raw_16k, sr_vad))
    for chunk_bytes in vad_collector(sr_vad, FRAME_MS, PADDING_MS, frames):
        # Reconstruct a pydub segment at 16k from raw PCM bytes
        seg_16k = AudioSegment(
            data=chunk_bytes,
            sample_width=2,   # 16-bit
            frame_rate=sr_vad,
            channels=1
        )
        dur = seg_16k.duration_seconds
        if dur < TARGET_LEN_MIN:
            continue

        # If too long, split into <= TARGET_LEN_MAX pieces
        if dur > TARGET_LEN_MAX:
            pieces = int(dur // TARGET_LEN_MAX) + 1
            step_ms = int(dur * 1000 / pieces)
            for p in range(pieces):
                start = p * step_ms
                end = min((p + 1) * step_ms, int(dur * 1000))
                piece_16k = seg_16k[start:end]

                # Convert back to 22,050 Hz for TTS
                piece_22k = piece_16k.set_frame_rate(TTS_SR)
                out_path = os.path.join(OUT_DIR, f"{idx:06d}.wav")
                piece_22k.export(out_path, format="wav")
                idx += 1
        else:
            # Convert back to 22,050 Hz for TTS
            seg_22k = seg_16k.set_frame_rate(TTS_SR)
            out_path = os.path.join(OUT_DIR, f"{idx:06d}.wav")
            seg_22k.export(out_path, format="wav")
            idx += 1

print(f"VAD chunks saved to {OUT_DIR}")
