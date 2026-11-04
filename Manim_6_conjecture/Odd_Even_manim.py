"""Odd/even decomposition and hyperbolic functions, styled after Affine_Trans_manim.py.

Render with .\render.ps1 -Quality l (preview) or -Quality h (1080p).
Chinese uses Text; mathematical expressions use ASCII-only MathTex.
Narration: numbered peiyin sentences are matched to video passages automatically.
Legacy 配音/01.mp3, 配音/02.mp3, ... (wav also supported) is also accepted.
"""

from pathlib import Path
import json
import math as math_module
import os
import tempfile

import numpy as np
from manim import *


ROOT = Path(__file__).resolve().parent
# dvisvgm on Windows needs an ASCII cache path in this Chinese workspace.
if os.name == "nt" and not str(config.get_dir("tex_dir").resolve()).isascii():
    config.tex_dir = str(Path(tempfile.gettempdir()) / "manim_odd_even_tex")
CJK_FONT = "Microsoft YaHei"
ODD_COLOR = BLUE_B
EVEN_COLOR = RED_B
EXP_COLOR = YELLOW
TANH_COLOR = TEAL_A

# Each item is (subtitle / voiceover text, silent reading duration in seconds).
# Audio duration replaces this estimate whenever the corresponding clip exists.
NARRATION = [
    ("你知道吗，任何一个定义域关于原点对称的函数，都可以拆分成奇函数和偶函数之和。", 9.0),
    ("这里的前提是：只要 x 在定义域内，负 x 也在定义域内。这样，f(x) 和 f(-x) 才能同时使用。", 10.0),
    ("先假设 f(x) 等于 O(x) 加 E(x)，其中 O 是奇函数，E 是偶函数。", 8.0),
    ("把 x 换成负 x。奇函数变号，偶函数不变，所以 f(-x) 等于负 O(x) 加 E(x)。", 10.0),
    ("两式相减，偶函数部分抵消，得到两倍的 O(x)。除以二，就解出了奇函数部分。", 9.0),
    ("两式相加，奇函数部分抵消，得到两倍的 E(x)。除以二，就解出了偶函数部分。", 9.0),
    ("这就得到了拆分公式。由这两个公式定义的 O 和 E，确实分别是奇函数和偶函数，而且相加等于原函数。", 11.0),
    ("下面看一个具体例子：指数函数 e 的 x 次方。它的定义域是全体实数，满足这个前提。", 9.0),
    ("把 x 换成负 x，得到 e 的负 x 次方。在图像上，这就是把原曲线关于 y 轴翻转。", 9.0),
    ("按照刚才的公式，奇函数部分是两个指数函数之差的一半，它叫双曲正弦，记作 sinh x。", 10.0),
    ("偶函数部分是两个指数函数之和的一半，它叫双曲余弦，记作 cosh x。", 8.0),
    ("于是，e 的 x 次方，等于双曲正弦加双曲余弦。", 6.0),
    ("先看双曲正弦的图像：它经过原点，关于原点中心对称，是奇函数。", 8.0),
    ("双曲余弦的图像关于 y 轴对称，是偶函数。它在 x 等于零时取得最小值一。", 9.0),
    ("当 x 和负 x 成对移动时，双曲正弦的函数值互为相反数，双曲余弦的函数值始终相等。", 10.0),
    ("把这三条曲线画在同一坐标系里。在同一个 x 处，蓝色的值加上红色的值，正好得到黄色的值。", 10.0),
    ("这里相加的是纵坐标。蓝色线段给出 sinh x，再接上红色线段给出的 cosh x，就到达 e 的 x 次方。", 11.0),
    ("即使 x 为负数，双曲正弦的值为负，这个相加关系仍然成立。", 7.0),
    ("还有一个常见的双曲函数：双曲正切。它等于双曲正弦除以双曲余弦，记作 tanh x。", 10.0),
    ("因为 e 的 x 次方与 e 的负 x 次方都大于零，所以双曲余弦始终大于零，分母不会为零。", 10.0),
    ("把 x 换成负 x：分子变号，分母不变。因此 tanh(-x) 等于负的 tanh(x)，它也是奇函数。", 10.0),
    ("看它的图像：经过原点，关于原点中心对称，所有函数值都在负一和一之间。", 9.0),
    ("当 x 越来越大时，图像趋近于 y 等于一；当 x 越来越小时，趋近于 y 等于负一。", 9.0),
    ("记住这两个构造：差的一半是奇函数部分，和的一半是偶函数部分。指数函数的两部分，就是双曲正弦和双曲余弦。", 12.0),
]


class OddEvenBase(Scene):
    def setup(self):
        self.camera.background_color = "#10131A"
        self.subtitle = None
        self.cues = []
        self.chapters = []
        self.subtitle_cues = []
        self.audio_cues = []
        self.animation_events = []
        self.voice_groups = {}
        if any((ROOT / "peiyin").glob("*.mp3")):
            from tools.prepare_voiceover import prepare_voiceover
            self.voice_groups = {group["line"]: group for group in prepare_voiceover(ROOT)["groups"]}

    def zh(self, text, size=30, color=WHITE):
        return Text(text, font=CJK_FONT, font_size=size, color=color)

    def math(self, *tex, size=40, color=WHITE):
        return MathTex(*tex, font_size=size, color=color)

    def title(self, text):
        return self.zh(text, 40, YELLOW).to_edge(UP, buff=0.32)

    @staticmethod
    def wrap(text, limit=32):
        lines = []
        while len(text) > limit:
            split = limit
            for i in range(limit - 1, limit - 12, -1):
                if text[i] in "，。；：！？":
                    split = i + 1
                    break
            # Avoid leaving only a word or punctuation on the final line.
            if len(text) - split < 8:
                split = len(text) - 8
                for i in range(split - 1, max(9, split - 12), -1):
                    if text[i] in "，。；：！？":
                        split = i + 1
                        break
            lines.append(text[:split])
            text = text[split:]
        return "\n".join(lines + [text])

    def set_subtitle(self, text):
        if self.subtitle is not None:
            if self.subtitle_cues:
                self.subtitle_cues[-1]["end"] = self.renderer.time
            self.remove(self.subtitle)
        caption = self.zh(self.wrap(text), 25).to_edge(DOWN, buff=0.20)
        if caption.width > config.frame_width - 1:
            caption.scale_to_fit_width(config.frame_width - 1)
        background = BackgroundRectangle(caption, fill_opacity=0.82, buff=0.13)
        self.subtitle = VGroup(background, caption).set_z_index(100)
        self.add(self.subtitle)
        self.subtitle_cues.append({"start": self.renderer.time, "end": self.renderer.time, "text": text})

    def speak(self, index, *animations, run_time=1.3, animation_parts=None):
        """Use exact sentence offsets for voice, subtitles and selected animations.

        animation_parts contains (sentence_index, animations, run_time) tuples.
        The original animations remain the fallback for a silent render.
        """
        text, duration = NARRATION[index - 1]
        if self.cues:
            self.cues[-1]["end"] = self.renderer.time
        start = self.renderer.time
        voice = self.voice_groups.get(index)
        if voice:
            self.add_sound(str(ROOT / "media" / "voiceover" / voice["wav"]))
            duration = voice["duration"]
            parts = {part[0]: (part[1], part[2]) for part in animation_parts} if animation_parts else {0: (animations, run_time)}
            for i, sentence in enumerate(voice["clips"]):
                offset = sentence["offset"]
                remaining = start + offset - self.renderer.time
                if remaining > 1 / config.frame_rate:
                    self.wait(remaining)
                self.set_subtitle(sentence["caption"])
                self.audio_cues.append({"line": index, "number": sentence["number"], "file": sentence["file"],
                                       "start": start + offset, "end": start + offset + sentence["duration"],
                                       "text": sentence["caption"]})
                if i in parts:
                    stage_animations, stage_run_time = parts[i]
                    if stage_animations:
                        next_offset = voice["clips"][i + 1]["offset"] if i + 1 < len(voice["clips"]) else duration
                        available = start + next_offset - self.renderer.time
                        stage_run_time = min(stage_run_time, max(1 / config.frame_rate, available - 1 / config.frame_rate))
                        animation_start = self.renderer.time
                        self.play(*stage_animations, run_time=stage_run_time)
                        self.animation_events.append({"line": index, "sentence": i, "start": animation_start,
                                                      "end": self.renderer.time})
            # Ceil to a video frame and add a short guard against adjacent audio
            # clips overlapping through the renderer's frame rounding.
            target = start + math_module.ceil((duration + 0.12) * config.frame_rate) / config.frame_rate
            remaining = target - self.renderer.time
            if remaining > 0:
                self.wait(remaining)
        else:
            self.set_subtitle(text)
            clip = next((ROOT / "配音" / f"{index:02d}{ext}"
                         for ext in (".mp3", ".wav") if (ROOT / "配音" / f"{index:02d}{ext}").is_file()), None)
            if clip is not None:
                from pydub import AudioSegment
                duration = AudioSegment.from_file(str(clip)).duration_seconds + 0.12
                self.add_sound(str(clip))
            if animations:
                self.play(*animations, run_time=run_time)
            remaining = max(duration, run_time if animations else 0) - (self.renderer.time - start)
            if remaining > 0:
                self.wait(remaining)
        self.subtitle_cues[-1]["end"] = self.renderer.time
        self.cues.append({"line": index, "start": start, "end": self.renderer.time, "text": text})

    def chapter(self, name):
        self.next_section(name)
        self.chapters.append({"name": name, "start": self.renderer.time})

    def clear_scene(self):
        self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=0.6)
        if self.cues:
            self.cues[-1]["end"] = self.renderer.time
        if self.subtitle_cues:
            self.subtitle_cues[-1]["end"] = self.renderer.time
        self.clear()
        self.subtitle = None

    def axes(self, x_range, y_range, width, height, center):
        axes = Axes(
            x_range=x_range, y_range=y_range, x_length=width, y_length=height,
            axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 21,
                         "include_numbers": True, "tip_width": 0.13, "tip_height": 0.13},
        ).move_to(center)
        labels = axes.get_axis_labels(self.math("x", size=25), self.math("y", size=25))
        return axes, labels

    @staticmethod
    def srt_time(seconds):
        ms = round(seconds * 1000)
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

    def export_cues(self):
        folder = ROOT / "media" / "subtitles"
        folder.mkdir(parents=True, exist_ok=True)
        name = type(self).__name__
        content = "\n\n".join(
            f"{i}\n{self.srt_time(cue['start'])} --> {self.srt_time(cue['end'])}\n{self.wrap(cue['text'])}"
            for i, cue in enumerate(self.subtitle_cues, 1)
        )
        (folder / f"{name}.srt").write_text(content + "\n", encoding="utf-8")
        (folder / f"{name}.json").write_text(
            json.dumps({"chapters": self.chapters, "cues": self.cues, "subtitles": self.subtitle_cues,
                        "audio_clips": self.audio_cues, "animation_events": self.animation_events}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def intro_and_proof(self):
        self.chapter("直接开篇")
        hook = self.zh("你知道吗？", 52, YELLOW).move_to(UP * 2.1)
        claim = self.zh("定义域关于原点对称的任何函数", 36).move_to(UP * 0.9)
        decomposition = self.math("f(x)", "=", "O(x)", "+", "E(x)", size=64).move_to(DOWN * 0.25)
        decomposition[2].set_color(ODD_COLOR)
        decomposition[4].set_color(EVEN_COLOR)
        meanings = VGroup(self.zh("奇函数", 28, ODD_COLOR), self.zh("偶函数", 28, EVEN_COLOR))
        meanings[0].next_to(decomposition[2], DOWN, buff=0.35)
        meanings[1].next_to(decomposition[4], DOWN, buff=0.35)
        self.speak(1, FadeIn(hook), FadeIn(claim), Write(decomposition), FadeIn(meanings), run_time=2,
                   animation_parts=[(0, [FadeIn(hook)], 0.7),
                                    (1, [FadeIn(claim), Write(decomposition), FadeIn(meanings)], 1.8)])
        self.clear_scene()

        self.chapter("假设拆分，联立求解")
        title = self.title("假设拆分，联立求解")
        condition = self.math(r"f:D\to\mathbb{R},\qquad x\in D\Longleftrightarrow -x\in D", size=34)
        condition.move_to(UP * 2.25)
        self.speak(2, FadeIn(title), Write(condition))
        assumption = self.math("f(x)", "=", "O(x)", "+", "E(x)", size=48).move_to(UP * 1.1)
        assumption[2].set_color(ODD_COLOR)
        assumption[4].set_color(EVEN_COLOR)
        names = VGroup(self.zh("O 是奇函数", 28, ODD_COLOR), self.zh("E 是偶函数", 28, EVEN_COLOR))
        names.arrange(RIGHT, buff=1.1).move_to(UP * 0.2)
        self.speak(3, Write(assumption), FadeIn(names), run_time=1.8)
        parity = VGroup(
            self.math(r"O(-x)=-O(x)", size=34, color=ODD_COLOR),
            self.math(r"E(-x)=E(x)", size=34, color=EVEN_COLOR),
        ).arrange(RIGHT, buff=0.8).move_to(names)
        substituted = self.math("f(-x)", "=", "O(-x)", "+", "E(-x)", size=45).move_to(DOWN * 1.05)
        substituted[2].set_color(ODD_COLOR)
        substituted[4].set_color(EVEN_COLOR)
        reflected = self.math("f(-x)", "=", "-O(x)", "+", "E(x)", size=45).move_to(substituted)
        reflected[2].set_color(ODD_COLOR)
        reflected[4].set_color(EVEN_COLOR)
        self.speak(4, ReplacementTransform(names, parity),
                   Succession(Write(substituted), ReplacementTransform(substituted, reflected)), run_time=3.2,
                   animation_parts=[(0, [Write(substituted)], 1.4),
                                    (1, [ReplacementTransform(names, parity), ReplacementTransform(substituted, reflected)], 1.3)])
        self.clear_scene()

        title = self.title("两式相减，解出奇函数部分")
        equations = VGroup(assumption.copy().set_opacity(1), reflected.copy().set_opacity(1)).arrange(DOWN, buff=0.38)
        equations.scale(0.8).move_to(UP * 1.55)
        difference = self.math(r"f(x)-f(-x)=2O(x)", size=43, color=ODD_COLOR).move_to(UP * 0.05)
        odd = self.math(r"O(x)=\frac{f(x)-f(-x)}{2}", size=46, color=ODD_COLOR).move_to(DOWN * 1.35)
        self.speak(5, FadeIn(title), FadeIn(equations),
                   Succession(Write(difference), Write(odd)), run_time=3,
                   animation_parts=[(0, [FadeIn(title), FadeIn(equations), Write(difference)], 1.8),
                                    (1, [Write(odd)], 1.2)])

        addition_title = self.title("两式相加，解出偶函数部分")
        addition = self.math(r"f(x)+f(-x)=2E(x)", size=43, color=EVEN_COLOR).move_to(difference)
        even = self.math(r"E(x)=\frac{f(x)+f(-x)}{2}", size=42, color=EVEN_COLOR).move_to(RIGHT * 3.2 + DOWN * 1.35)
        self.speak(6, ReplacementTransform(title, addition_title), ReplacementTransform(difference, addition),
                   odd.animate.scale(42 / 46).move_to(LEFT * 3.2 + DOWN * 1.35), Write(even), run_time=2.5,
                   animation_parts=[(0, [ReplacementTransform(title, addition_title), ReplacementTransform(difference, addition),
                                         odd.animate.scale(42 / 46).move_to(LEFT * 3.2 + DOWN * 1.35)], 1.5),
                                    (1, [Write(even)], 1.2)])
        self.clear_scene()

        title = self.title("于是，拆分公式就得到了")
        total = self.math("f(x)", "=", r"\frac{f(x)-f(-x)}{2}", "+", r"\frac{f(x)+f(-x)}{2}", size=46).move_to(UP * 1.2)
        total[2].set_color(ODD_COLOR)
        total[4].set_color(EVEN_COLOR)
        # The initial assumption identifies the only possible parts. This final
        # check also establishes that the solved formulas give a decomposition.
        checks = VGroup(
            self.math(r"O(-x)=-O(x)", size=35, color=ODD_COLOR),
            self.math(r"E(-x)=E(x)", size=35, color=EVEN_COLOR),
        ).arrange(RIGHT, buff=0.9).move_to(DOWN * 0.35)
        reconstruction = self.math("O(x)+E(x)=f(x)", size=39, color=YELLOW).move_to(DOWN * 1.5)
        self.speak(7, FadeIn(title), Write(total), FadeIn(checks), Write(reconstruction), run_time=2.5,
                   animation_parts=[(0, [FadeIn(title), Write(total)], 1.5),
                                    (1, [FadeIn(checks), Write(reconstruction)], 1.3)])
        self.clear_scene()

    def exponential_example(self):
        self.chapter("指数函数与镜像")
        title = self.title("把指数函数拆成两部分")
        formula = self.math(r"f(x)=e^x,\qquad D=\mathbb{R}", size=40, color=EXP_COLOR).move_to(UP * 2.1)
        axes, labels = self.axes([-2, 2, 1], [0, 8, 2], 8.2, 3.4, DOWN * 0.45)
        exp_graph = axes.plot(np.exp, x_range=[-2, 2, 0.02], color=EXP_COLOR, stroke_width=5)
        exp_label = self.math("e^x", size=30, color=EXP_COLOR).move_to(axes.c2p(1.6, 6.9))
        self.speak(8, FadeIn(title), Write(formula), Create(axes), FadeIn(labels), Create(exp_graph), FadeIn(exp_label), run_time=2)
        mirror = axes.plot(lambda x: np.exp(-x), x_range=[-2, 2, 0.02], color=GREY_A, stroke_width=4)
        mirror_label = self.math("e^{-x}", size=30, color=GREY_A).move_to(axes.c2p(-1.6, 6.9))
        self.speak(9, TransformFromCopy(exp_graph, mirror), FadeIn(mirror_label), run_time=2.2,
                   animation_parts=[(0, [FadeIn(mirror_label)], 0.7),
                                    (1, [TransformFromCopy(exp_graph, mirror)], 2.2)])
        self.clear_scene()

        self.chapter("sinh 与 cosh 的定义")
        title = self.title("指数函数的奇、偶部分有自己的名字")
        odd = self.math(r"O(x)=\frac{e^x-e^{-x}}{2}=\sinh x", size=46, color=ODD_COLOR).move_to(UP * 1.65)
        odd_name = self.zh("双曲正弦 · 奇函数", 28, ODD_COLOR).move_to(UP * 0.65)
        even = self.math(r"E(x)=\frac{e^x+e^{-x}}{2}=\cosh x", size=46, color=EVEN_COLOR).move_to(DOWN * 0.25)
        even_name = self.zh("双曲余弦 · 偶函数", 28, EVEN_COLOR).move_to(DOWN * 1.2)
        identity = self.math("e^x", "=", r"\sinh x", "+", r"\cosh x", size=52).move_to(DOWN * 2.15)
        identity[0].set_color(EXP_COLOR)
        identity[2].set_color(ODD_COLOR)
        identity[4].set_color(EVEN_COLOR)
        odd_definition = self.math(r"O(x)=\frac{e^x-e^{-x}}{2}", size=46, color=ODD_COLOR).move_to(odd)
        even_definition = self.math(r"E(x)=\frac{e^x+e^{-x}}{2}", size=46, color=EVEN_COLOR).move_to(even)
        self.speak(10, FadeIn(title), Write(odd), FadeIn(odd_name), run_time=2,
                   animation_parts=[(0, [FadeIn(title), Write(odd_definition)], 1.8),
                                    (1, [ReplacementTransform(odd_definition, odd), FadeIn(odd_name)], 1.2)])
        self.speak(11, Write(even), FadeIn(even_name), run_time=2,
                   animation_parts=[(0, [Write(even_definition)], 1.8),
                                    (1, [ReplacementTransform(even_definition, even), FadeIn(even_name)], 1.2)])
        self.speak(12, Write(identity), run_time=1.5)
        self.clear_scene()

    def hyperbolic_graphs(self):
        self.chapter("奇偶对称的图像")
        title = self.title("从图像看奇偶性")
        left_axes, left_labels = self.axes([-2, 2, 1], [-4, 4, 2], 4.8, 3.2, LEFT * 3.4 + DOWN * 0.35)
        right_axes, right_labels = self.axes([-2, 2, 1], [0, 4, 1], 4.8, 3.2, RIGHT * 3.4 + DOWN * 0.35)
        sinh = left_axes.plot(np.sinh, x_range=[-2, 2, 0.02], color=ODD_COLOR, stroke_width=5)
        cosh = right_axes.plot(np.cosh, x_range=[-2, 2, 0.02], color=EVEN_COLOR, stroke_width=5)
        left_name = self.math(r"y=\sinh x,\quad\sinh(-x)=-\sinh x", size=29, color=ODD_COLOR).move_to(LEFT * 3.4 + UP * 2.05)
        right_name = self.math(r"y=\cosh x,\quad\cosh(-x)=\cosh x", size=29, color=EVEN_COLOR).move_to(RIGHT * 3.4 + UP * 2.05)
        left_note = self.zh("关于原点中心对称", 26, ODD_COLOR).move_to(LEFT * 3.4 + DOWN * 2.55)
        right_note = self.zh("关于 y 轴对称", 26, EVEN_COLOR).move_to(RIGHT * 3.4 + DOWN * 2.55)
        origin = Dot(left_axes.c2p(0, 0), color=ODD_COLOR)
        origin_tag = self.math("(0,0)", size=24, color=ODD_COLOR).next_to(origin, DR, buff=0.13)
        self.speak(13, FadeIn(title), Create(left_axes), FadeIn(left_labels), Create(sinh), FadeIn(left_name),
                   FadeIn(left_note), FadeIn(origin), FadeIn(origin_tag), run_time=2.2)
        minimum = Dot(right_axes.c2p(0, 1), color=EVEN_COLOR)
        minimum_tag = self.math("(0,1)", size=24, color=EVEN_COLOR).next_to(minimum, UP, buff=0.15)
        self.speak(14, Create(right_axes), FadeIn(right_labels), Create(cosh), FadeIn(right_name),
                   FadeIn(right_note), FadeIn(minimum), FadeIn(minimum_tag), run_time=2.2,
                   animation_parts=[(0, [Create(right_axes), FadeIn(right_labels), Create(cosh), FadeIn(right_name), FadeIn(right_note)], 1.8),
                                    (1, [FadeIn(minimum), FadeIn(minimum_tag)], 0.7)])
        self.play(FadeOut(origin_tag), FadeOut(minimum_tag), run_time=0.4)
        tracker = ValueTracker(0.5)

        def paired_points():
            x = tracker.get_value()
            return VGroup(
                Dot(left_axes.c2p(x, np.sinh(x)), color=ODD_COLOR),
                Dot(left_axes.c2p(-x, -np.sinh(x)), color=ODD_COLOR),
                DashedLine(left_axes.c2p(-x, -np.sinh(x)), left_axes.c2p(x, np.sinh(x)), color=ODD_COLOR, stroke_opacity=0.5),
                Dot(right_axes.c2p(x, np.cosh(x)), color=EVEN_COLOR),
                Dot(right_axes.c2p(-x, np.cosh(x)), color=EVEN_COLOR),
                DashedLine(right_axes.c2p(-x, np.cosh(x)), right_axes.c2p(x, np.cosh(x)), color=EVEN_COLOR, stroke_opacity=0.5),
            )

        pairs = always_redraw(paired_points)
        self.add(pairs)
        self.speak(15, tracker.animate.set_value(1.8), run_time=4)
        pairs.clear_updaters()
        self.clear_scene()

    def sum_graph(self):
        self.chapter("图像上的纵坐标相加")
        title = self.title("同一个 x，纵坐标相加")
        identity = self.math("e^x", "=", r"\sinh x", "+", r"\cosh x", size=42).move_to(UP * 2.2)
        identity[0].set_color(EXP_COLOR)
        identity[2].set_color(ODD_COLOR)
        identity[4].set_color(EVEN_COLOR)
        axes, labels = self.axes([-2, 2, 1], [-4, 8, 2], 7.4, 3.6, LEFT * 1.9 + DOWN * 0.25)
        sinh = axes.plot(np.sinh, x_range=[-2, 2, 0.02], color=ODD_COLOR, stroke_width=4)
        cosh = axes.plot(np.cosh, x_range=[-2, 2, 0.02], color=EVEN_COLOR, stroke_width=4)
        exp = axes.plot(np.exp, x_range=[-2, 2, 0.02], color=EXP_COLOR, stroke_width=4)
        legend = VGroup(
            self.math(r"\sinh x", size=30, color=ODD_COLOR),
            self.math(r"\cosh x", size=30, color=EVEN_COLOR),
            self.math(r"e^x", size=30, color=EXP_COLOR),
        ).arrange(RIGHT, buff=0.7).move_to(LEFT * 1.7 + DOWN * 2.55)
        self.speak(16, FadeIn(title), Write(identity), Create(axes), FadeIn(labels), Create(sinh),
                   Create(cosh), Create(exp), FadeIn(legend), run_time=2.5)
        tracker = ValueTracker(1.3)

        def stack():
            x = tracker.get_value()
            # The red segment is cosh(x), translated to start at sinh(x).
            # For negative x, the blue segment points downward first.
            base, middle, top = axes.c2p(x, 0), axes.c2p(x, np.sinh(x)), axes.c2p(x, np.exp(x))
            offset = RIGHT * 0.13
            return VGroup(
                Line(base, middle, color=ODD_COLOR, stroke_width=8),
                Line(middle + offset, top + offset, color=EVEN_COLOR, stroke_width=8),
                DashedLine(top, top + offset, color=GREY_B),
                Dot(middle, radius=0.07, color=ODD_COLOR), Dot(top, radius=0.09, color=EXP_COLOR),
                Dot(axes.c2p(x, np.cosh(x)), radius=0.07, color=EVEN_COLOR),
            )

        values = VGroup(
            VGroup(self.math("x=", size=32), DecimalNumber(1.3, num_decimal_places=2, font_size=32)).arrange(RIGHT, buff=0.12),
            VGroup(self.math(r"\sinh x=", size=30, color=ODD_COLOR), DecimalNumber(np.sinh(1.3), num_decimal_places=2, font_size=30, color=ODD_COLOR)).arrange(RIGHT, buff=0.12),
            VGroup(self.math(r"\cosh x=", size=30, color=EVEN_COLOR), DecimalNumber(np.cosh(1.3), num_decimal_places=2, font_size=30, color=EVEN_COLOR)).arrange(RIGHT, buff=0.12),
            VGroup(self.math(r"e^x=", size=30, color=EXP_COLOR), DecimalNumber(np.exp(1.3), num_decimal_places=2, font_size=30, color=EXP_COLOR)).arrange(RIGHT, buff=0.12),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(RIGHT * 4.15)
        for row, fn in zip(values, (lambda x: x, np.sinh, np.cosh, np.exp)):
            row[1].add_updater(lambda mob, fn=fn: mob.set_value(fn(tracker.get_value())))
        segments = always_redraw(stack)
        self.add(segments)
        self.speak(17, FadeIn(values), tracker.animate.set_value(1.8), run_time=3,
                   animation_parts=[(0, [FadeIn(values)], 0.8), (1, [tracker.animate.set_value(1.8)], 3)])
        self.speak(18, tracker.animate.set_value(-1.7), run_time=5)
        segments.clear_updaters()
        values.clear_updaters()
        self.clear_scene()

    def tanh_example(self):
        self.chapter("双曲正切的奇性证明")
        title = self.title("双曲正切也是奇函数")
        definition = self.math(r"\tanh x=\frac{\sinh x}{\cosh x}=\frac{e^x-e^{-x}}{e^x+e^{-x}}", size=44, color=TANH_COLOR).move_to(UP * 1.6)
        positive = self.math(r"\cosh x=\frac{e^x+e^{-x}}{2}>0\quad(x\in\mathbb{R})", size=38, color=EVEN_COLOR).move_to(UP * 0.15)
        proof = self.math(r"\tanh(-x)=\frac{\sinh(-x)}{\cosh(-x)}=\frac{-\sinh x}{\cosh x}=-\tanh x", size=39, color=TANH_COLOR).move_to(DOWN * 1.3)
        self.speak(19, FadeIn(title), Write(definition), run_time=2,
                   animation_parts=[(0, [FadeIn(title)], 0.8), (1, [Write(definition)], 1.7)])
        self.speak(20, Write(positive), run_time=1.5)
        self.speak(21, Write(proof), run_time=2.5)
        self.clear_scene()

        self.chapter("双曲正切的图像")
        title = self.title("双曲正切：关于原点对称的 S 形曲线")
        formula = self.math(r"y=\tanh x,\qquad -1<\tanh x<1", size=37, color=TANH_COLOR).move_to(UP * 2.1)
        axes, labels = self.axes([-4, 4, 1], [-1.5, 1.5, 0.5], 9.2, 3.5, DOWN * 0.35)
        curve = axes.plot(np.tanh, x_range=[-4, 4, 0.025], color=TANH_COLOR, stroke_width=5)
        origin = Dot(axes.c2p(0, 0), color=TANH_COLOR)
        upper = DashedLine(axes.c2p(-4, 1), axes.c2p(4, 1), color=YELLOW, stroke_opacity=0.65)
        lower = DashedLine(axes.c2p(-4, -1), axes.c2p(4, -1), color=YELLOW, stroke_opacity=0.65)
        upper_tag = self.math("y=1", size=26, color=YELLOW).next_to(upper, RIGHT, buff=0.2)
        lower_tag = self.math("y=-1", size=26, color=YELLOW).next_to(lower, RIGHT, buff=0.2)
        # Rotate a short highlighted piece so its circular path stays in frame.
        positive_half = axes.plot(np.tanh, x_range=[0, 1.4, 0.025], color=WHITE, stroke_width=7)
        self.speak(22, FadeIn(title), Write(formula), Create(axes), FadeIn(labels), Create(curve), FadeIn(origin), run_time=2.5)
        self.add(positive_half)
        self.play(Rotate(positive_half, PI, about_point=axes.c2p(0, 0)), run_time=2)
        self.play(FadeOut(positive_half), run_time=0.5)
        limits = self.math(r"\lim_{x\to+\infty}\tanh x=1,\qquad\lim_{x\to-\infty}\tanh x=-1", size=30).move_to(DOWN * 2.55)
        self.speak(23, Create(upper), Create(lower), FadeIn(upper_tag), FadeIn(lower_tag), Write(limits), run_time=2,
                   animation_parts=[(0, [Create(upper), FadeIn(upper_tag)], 1),
                                    (1, [Create(lower), FadeIn(lower_tag), Write(limits)], 1.4)])
        self.clear_scene()

    def summary(self):
        self.chapter("回顾")
        title = self.title("差的一半是奇，和的一半是偶")
        general = self.math("f(x)", "=", r"\frac{f(x)-f(-x)}{2}", "+", r"\frac{f(x)+f(-x)}{2}", size=46).move_to(UP * 1.35)
        general[2].set_color(ODD_COLOR)
        general[4].set_color(EVEN_COLOR)
        condition = self.zh("前提：定义域关于原点对称", 28, GREY_A).move_to(UP * 2.3)
        example = self.math("e^x", "=", r"\sinh x", "+", r"\cosh x", size=52).move_to(DOWN * 0.25)
        example[0].set_color(EXP_COLOR)
        example[2].set_color(ODD_COLOR)
        example[4].set_color(EVEN_COLOR)
        tanh = self.math(r"\tanh x=\frac{\sinh x}{\cosh x},\qquad\tanh(-x)=-\tanh x", size=38, color=TANH_COLOR).move_to(DOWN * 1.75)
        self.speak(24, FadeIn(title), FadeIn(condition), Write(general), Write(example), Write(tanh), run_time=3,
                   animation_parts=[(0, [FadeIn(title), FadeIn(condition), Write(general)], 1.8),
                                    (1, [Write(example), Write(tanh)], 1.5)])


class OddEvenDecomposition(OddEvenBase):
    """Complete video: theorem, proof, exponential example, and four graphs."""

    def construct(self):
        self.intro_and_proof()
        self.exponential_example()
        self.hyperbolic_graphs()
        self.sum_graph()
        self.tanh_example()
        self.summary()
        self.export_cues()


class DecompositionProof(OddEvenBase):
    def construct(self):
        self.intro_and_proof()
        self.export_cues()


class HyperbolicFunctions(OddEvenBase):
    def construct(self):
        self.exponential_example()
        self.hyperbolic_graphs()
        self.sum_graph()
        self.tanh_example()
        self.summary()
        self.export_cues()
