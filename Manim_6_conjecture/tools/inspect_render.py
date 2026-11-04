"""Extract key frames and a contact sheet from an already rendered video."""

import argparse
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--timeline", type=Path, default=Path("media/subtitles/OddEvenDecomposition.json"))
    parser.add_argument("--output", type=Path, default=Path("media/verification"))
    args = parser.parse_args()
    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    with av.open(str(args.video)) as container:
        stream = container.streams.video[0]
        duration = float(stream.duration * stream.time_base)
        print(f"Video: {stream.width}x{stream.height}, {float(stream.average_rate):.3f} fps, {duration:.3f} s")
        assert len(timeline["cues"]) == 24, "Expected all 24 narration segments"
        for cue in timeline["cues"]:
            assert 0 <= cue["start"] < cue["end"] <= duration + 0.15, cue
        for a, b in zip(timeline["cues"], timeline["cues"][1:]):
            assert a["end"] <= b["start"] + 0.001, "Subtitle cues overlap"
        print("All 24 subtitle cues fit the video timeline.")
        if timeline.get("audio_clips"):
            clips = timeline["audio_clips"]
            assert [clip["number"] for clip in clips] == list(range(1, 42)), "Audio files missing or out of order"
            assert len(timeline["subtitles"]) == 41, "Expected sentence subtitles"
            assert container.streams.audio, "The video is missing its audio track"
            for clip in clips:
                assert 0 <= clip["start"] < clip["end"] <= duration + 0.15, clip
                cue = next(c for c in timeline["cues"] if c["line"] == clip["line"])
                assert cue["start"] <= clip["start"] and clip["end"] <= cue["end"] + 0.05, clip
            for a, b in zip(clips, clips[1:]):
                assert a["end"] <= b["start"] + 0.001, "Audio clips overlap"
            for subtitle, clip in zip(timeline["subtitles"], clips):
                assert subtitle["text"] == clip["text"]
                assert abs(subtitle["start"] - clip["start"]) < 1 / float(stream.average_rate) + 0.01
                assert subtitle["end"] >= clip["end"] - 0.05
            print("All 41 audio clips and sentence subtitles are ordered, contained in their scenes, and do not overlap.")
        selected = [1, 6, 7, 11, 14, 15, 18, 23]
        board = Image.new("RGB", (1280, 4 * 386), "#10131A")
        draw = ImageDraw.Draw(board)
        for i, number in enumerate(selected):
            cue = next(c for c in timeline["cues"] if c["line"] == number)
            at = max(cue["start"], cue["end"] - 1.1)
            container.seek(int(at / stream.time_base), stream=stream, backward=True)
            frame = next(f for f in container.decode(stream) if float(f.pts * stream.time_base) >= at)
            snapshot = frame.to_image().convert("RGB")
            snapshot.save(args.output / f"line_{number:02d}.png")
            col, row = i % 2, i // 2
            board.paste(snapshot.resize((640, 360), Image.Resampling.LANCZOS), (col * 640, row * 386 + 26))
            draw.text((col * 640 + 10, row * 386 + 6), f"Line {number:02d} | {at:.2f}s", fill="white")
        board.save(args.output / "storyboard.jpg", quality=95)
    print(f"Key frames and storyboard: {args.output.resolve()}")


if __name__ == "__main__":
    main()
