"""Check that each original MP3 is audible at its scheduled video position."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

runtime_bin = Path(sys.executable).parent / "Library" / "bin"
if runtime_bin.is_dir():
    os.environ["PATH"] = str(runtime_bin) + os.pathsep + os.environ.get("PATH", "")

import numpy as np
from scipy.signal import correlate, resample_poly
from pydub import AudioSegment


def pcm(path, prepare_source=False):
    executable = shutil.which("ffmpeg")
    if executable is None:
        candidate = Path(sys.executable).parent / "Library" / "bin" / "ffmpeg.exe"
        if candidate.is_file():
            executable = str(candidate)
    if executable is None:
        raise RuntimeError("ffmpeg is required; use the Manim environment PATH.")
    if prepare_source:
        # Reproduce the preparation's resampling before comparing against AAC;
        # directly downsampling a source MP3 can use a different filter.
        clip = AudioSegment.from_file(str(path)).set_frame_rate(44100).set_channels(1).set_sample_width(2)
        result = subprocess.run([executable, "-v", "error", "-f", "s16le", "-ar", "44100", "-ac", "1", "-i", "pipe:0",
                                 "-ar", "8000", "-f", "s16le", "pipe:1"], input=clip.raw_data, check=True, capture_output=True)
    else:
        result = subprocess.run([executable, "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "8000",
                                 "-f", "s16le", "pipe:1"], check=True, capture_output=True)
    return np.frombuffer(result.stdout, dtype="<i2").astype(np.float64)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--timeline", type=Path, default=Path("media/subtitles/OddEvenDecomposition.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    video = pcm(args.video)
    results = []
    for cue in timeline["audio_clips"]:
        original = pcm(root / "peiyin" / cue["file"], prepare_source=True)
        # Compare the loudest half-second in each sentence, allowing 100 ms of
        # decoder delay. FFT correlation verifies the actual embedded waveform.
        window = min(4000, len(original))
        starts = range(0, len(original) - window + 1, 800)
        at = max(starts, key=lambda i: np.dot(original[i:i + window], original[i:i + window]))
        reference = original[at:at + window]
        expected = round(cue["start"] * 8000) + at
        search_start = max(0, expected - 800)
        search_end = min(len(video), expected + window + 800)
        search = video[search_start:search_end]
        # Oversample the band-limited waveform: an integer 8 kHz alignment can
        # otherwise look dissimilar because of a sub-sample AAC/resampling delay.
        reference = resample_poly(reference, 4, 1)
        search = resample_poly(search, 4, 1)
        window = len(reference)
        values = correlate(search, reference, mode="valid", method="fft")
        energy = np.concatenate(([0.0], np.cumsum(search ** 2)))
        norms = np.sqrt(np.maximum(energy[window:] - energy[:-window], 0) * np.dot(reference, reference))
        scores = values / np.maximum(norms, 1)
        best = int(np.argmax(scores))
        score = float(scores[best])
        delay = (search_start - expected) / 8000 + best / 32000
        results.append({"number": cue["number"], "file": cue["file"], "correlation": score, "offset_seconds": delay})
    assert len(results) == 41
    output = root / "media" / "verification" / "voiceover_sync.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    failures = [r for r in results if r["correlation"] <= 0.95 or abs(r["offset_seconds"]) >= 0.075]
    assert not failures, failures
    print(f"Verified all 41 embedded clips. Minimum correlation: {min(r['correlation'] for r in results):.5f}; "
          f"largest absolute delay: {max(abs(r['offset_seconds']) for r in results):.4f}s")


if __name__ == "__main__":
    main()
