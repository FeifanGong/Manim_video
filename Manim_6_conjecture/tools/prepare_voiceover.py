"""Match numbered peiyin sentences to the 24 video passages and assemble WAVs."""

from pathlib import Path
import json
import re

from pydub import AudioSegment


def prepare_voiceover(root):
    root = Path(root)
    source = root / "peiyin"
    files = sorted(source.glob("*.mp3"), key=lambda p: int(p.name.split("_", 1)[0]))
    numbers = [int(p.name.split("_", 1)[0]) for p in files]
    if numbers != list(range(1, 42)):
        raise ValueError("peiyin must contain numbered sentences 0001 through 0041, without gaps.")
    paragraphs = (root / "Manboo配音文本.txt").read_text(encoding="utf-8").strip().split("\n\n")
    if len(paragraphs) != 24:
        raise ValueError("Expected 24 passages in the Manboo narration text.")
    sentences = [re.findall(r"[^。？！]+[。？！]?", paragraph) for paragraph in paragraphs]
    # These two openings were edited in the user's Manboo export. The filenames
    # provide their sentence prefixes; the remaining text follows the script.
    sentences[21][0] = "它的图像长这样：经过原点，关于原点中心对称，所有函数值都在负一和一之间。"
    sentences[23][0] = "这两个公式告诉我们：原函数与它的镜像，差的一半是奇函数部分，和的一半是偶函数部分。"
    flat = [text for group in sentences for text in group]
    if len(flat) != len(files):
        raise ValueError("The sentence count does not match the audio export.")
    for file, text in zip(files, flat):
        prefix = file.stem.split("_", 1)[1]
        if not text.startswith(prefix):
            raise ValueError(f"Audio sentence does not match narration: {file.name}")

    output = root / "media" / "voiceover"
    output.mkdir(parents=True, exist_ok=True)
    fingerprint = {"version": 1, "sentences": sentences,
                   "files": [{"name": f.name, "size": f.stat().st_size,
                              "mtime_ns": f.stat().st_mtime_ns} for f in files]}
    manifest_file = output / "manifest.json"
    if manifest_file.is_file():
        previous = json.loads(manifest_file.read_text(encoding="utf-8"))
        if previous.get("fingerprint") == fingerprint and all(
            (output / f"{i:02d}.wav").is_file() for i in range(1, 25)
        ):
            return previous

    cursor = 0
    groups = []
    for index, texts in enumerate(sentences, 1):
        combined = AudioSegment.empty()
        pieces = []
        for text in texts:
            file = files[cursor]
            cursor += 1
            clip = AudioSegment.from_file(str(file)).set_frame_rate(44100).set_channels(1).set_sample_width(2)
            if pieces:
                combined += AudioSegment.silent(duration=80, frame_rate=44100)
            offset = combined.frame_count() / 44100 if pieces else 0.0
            pieces.append({"number": cursor, "file": file.name, "offset": offset,
                           "duration": clip.frame_count() / 44100, "spoken_text": text,
                           "caption": text.replace("艾克斯", "x").replace("伊", "e")})
            combined += clip
        target = output / f"{index:02d}.wav"
        combined.export(str(target), format="wav")
        groups.append({"line": index, "wav": target.name,
                       "duration": combined.frame_count() / 44100, "clips": pieces})
    manifest = {"source": "peiyin", "fingerprint": fingerprint, "groups": groups}
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# 配音与画面对应表", "", "按文件名前缀和 Manboo 文案匹配，音频顺序为 0001 至 0041。", "",
             "| 视频段落 | 原始音频 | 段内起点（秒） | 音频时长（秒） | 对应文案 |", "| --- | --- | ---: | ---: | --- |"]
    for group in groups:
        for clip in group["clips"]:
            lines.append(f"| {group['line']:02d} | {clip['file']} | {clip['offset']:.3f} | {clip['duration']:.3f} | {clip['spoken_text']} |")
    (root / "配音对应表.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    manifest = prepare_voiceover(root)
    print(f"Matched 41 source clips to {len(manifest['groups'])} video passages.")
    print(f"Prepared duration: {sum(g['duration'] for g in manifest['groups']):.3f}s")
