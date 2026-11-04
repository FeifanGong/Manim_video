"""用柯西不等式证明椭圆切线方程；风格参考 Affine_Trans_manim.py。

Render with the existing virtual environment via: .\render.ps1 -Quality h
Chinese is rendered with Text; MathTex contains ASCII LaTeX only.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

from manim import *
import numpy as np
from pydub import AudioSegment


ROOT = Path(__file__).resolve().parent
CJK_FONT = "Microsoft YaHei"
BG = "#10131A"
MUTED = "#A9B5C7"
ELLIPSE_COLOR = "#63B5F6"
POINT_COLOR = "#FFCF5C"
MOVING_COLOR = "#76DBC5"
LINE_COLOR = "#FF8585"

# dvisvgm can fail on non-ASCII paths on Windows. Keep only its TeX cache in
# an ASCII temporary directory; all deliverables stay inside this project.
TEX_CACHE = Path(tempfile.gettempdir()) / "manim_cauchy_tangent_tex"
TEX_CACHE.mkdir(parents=True, exist_ok=True)
config.tex_dir = str(TEX_CACHE)

# Each item is a subtitle and a voiceover cue. Manboo split the 23 paragraphs
# into 29 clips in 配音文件; keep sentence splits within their original cue.
MANBOO_GROUPS = (
    (1,), (2,), (3,), (4, 5), (6,), (7,), (8,), (9,), (10, 11),
    (12,), (13,), (14, 15), (16, 17), (18,), (19,), (20,),
    (21, 22), (23, 24), (25,), (26,), (27,), (28,), (29,),
)
NARRATION = [
    ("今天我们用柯西不等式证明椭圆的切线。", 5.0),
    ("设椭圆上的已知点为 P(x₀, y₀)。", 5.0),
    ("我们把平方项的一个因子换成切点坐标。", 5.0),
    ("代入 P，只能说明直线经过 P。要证明相切，只需要证明直线与椭圆只有一个交点。", 7.5),
    ("任取 Q(x, y)，把两点的坐标分别除以 a 和 b。", 6.0),
    ("这样得到两个单位向量 u、v，恰好可以使用柯西不等式。", 5.5),
    ("由柯西不等式，(u·v)² ≤ ‖u‖²‖v‖²。", 5.0),
    ("代入归一化后的坐标，右边的两个括号都等于 1。", 6.0),
    ("因此 −1 ≤ F(Q) ≤ 1。我们关心的是上界 1。", 7.0),
    ("这意味着，椭圆上所有的点，都在候选直线的同一侧，或者在直线上。", 7.0),
    ("让 Q 沿椭圆移动，右边实时显示 F(Q) 的值。", 5.5),
    ("在对径点 −P 处，F(Q) = −1。平方形式也取等号，但它不在候选直线上。", 8.0),
    ("只有回到 P 时，F(Q) = 1。接下来证明取等点唯一。", 7.0),
    ("若 Q 同时在椭圆和候选直线上，则 u·v = 1。", 6.0),
    ("柯西取等时，两向量线性相关，即 u = λv。", 7.0),
    ("因为 ‖u‖ = ‖v‖ = 1，所以 λ = ±1。", 5.0),
    ("但 u·v = 1，所以 λ = 1；λ = −1 对应的是对径点。", 6.5),
    ("因此 u = v，Q = P。这条直线与椭圆只有一个公共点。", 6.5),
    ("整个椭圆位于直线同侧，并且只在 P 处接触，所以它就是 P 点处的切线。", 7.5),
    ("切点可以沿椭圆移动，切线方程的形式始终不变。", 5.5),
    ("当 P = (a, 0) 时，公式给出竖直切线 x = a。", 5.5),
    ("当 P = (0, b) 时，得到水平切线 y = b。", 5.0),
    ("左端点和下端点也一样：分别得到 x = −a、y = −b。", 7.0),
]


def ellipse_point(a: float, b: float, theta: float) -> np.ndarray:
    return np.array([a * np.cos(theta), b * np.sin(theta)])


def clipped_support_segment(a, b, theta, level=1.0, bounds=(-3.55, 3.55, -2.25, 2.25)):
    """Clip F(x,y)=level without a slope; works at all four axis vertices.

    F(x,y)=x*cos(theta)/a + y*sin(theta)/b.
    A point is level*P; a direction is (-a*sin(theta), b*cos(theta)).
    """
    point = level * ellipse_point(a, b, theta)
    direction = np.array([-a * np.sin(theta), b * np.cos(theta)])
    lo, hi = -np.inf, np.inf
    for coord, delta, lower, upper in zip(point, direction, bounds[::2], bounds[1::2]):
        if abs(delta) < 1e-10:
            if not lower <= coord <= upper:
                raise ValueError("Support line does not intersect the plotting window")
            continue
        t0, t1 = sorted(((lower - coord) / delta, (upper - coord) / delta))
        lo, hi = max(lo, t0), min(hi, t1)
    if lo > hi:
        raise ValueError("Support line does not intersect the plotting window")
    return point + lo * direction, point + hi * direction


class CauchyEllipseTangent(Scene):
    """Complete Chinese lesson, with captions and optional local voice clips."""

    A = 2.8
    B = 1.65
    THETA = PI / 3

    def construct(self):
        self.camera.background_color = BG
        self.subtitle = None
        self.cues = []
        self.chapters = []
        self.voiceovers = self.prepare_voiceovers()
        self.intro()
        self.candidate_line()
        self.cauchy_bound()
        self.geometric_meaning()
        self.equality_case()
        self.vertex_cases()
        self.export_timeline()

    @staticmethod
    def zh(text, font_size=30, color=WHITE):
        return Text(text, font=CJK_FONT, font_size=font_size, color=color)

    @staticmethod
    def math(tex, font_size=40, color=WHITE, max_width=12.4):
        result = MathTex(tex, font_size=font_size, color=color)
        if result.width > max_width:
            result.scale_to_fit_width(max_width)
        return result

    def heading(self, number, text):
        self.next_section(text)
        self.chapters.append({"title": text, "start": float(self.renderer.time)})
        tag = self.zh(number, 22, POINT_COLOR)
        title = self.zh(text, 39, POINT_COLOR)
        row = VGroup(tag, title).arrange(RIGHT, buff=0.28)
        row.to_edge(UP, buff=0.32).to_edge(LEFT, buff=0.55)
        rule = Line(LEFT * 6.55, RIGHT * 6.55, stroke_width=1, color=MUTED)
        rule.set_opacity(0.22).set_y(2.81)
        return VGroup(row, rule)

    def prepare_voiceovers(self):
        # Directly calling the conda Python should work without activating it.
        audio_bin = Path(sys.executable).parent / "Library" / "bin"
        if audio_bin.is_dir():
            os.environ["PATH"] = str(audio_bin) + os.pathsep + os.environ.get("PATH", "")
        source = ROOT / "配音文件"
        files = [p for p in source.iterdir() if p.is_file() and p.suffix.lower() in
                 {".mp3", ".wav", ".m4a"}] if source.is_dir() else []
        voiceovers = {}
        if files:
            indexed = {}
            for path in files:
                match = re.match(r"^(\d+)(?:_|$)", path.stem)
                if match is None:
                    raise ValueError(f"Voiceover filename needs a numeric prefix: {path.name}")
                number = int(match[1])
                if number in indexed:
                    raise ValueError(f"Duplicate voiceover number: {number}")
                indexed[number] = path
            expected = {number for group in MANBOO_GROUPS for number in group}
            if set(indexed) != expected:
                raise ValueError(f"Manboo voiceovers: missing {sorted(expected - set(indexed))}; "
                                 f"unexpected {sorted(set(indexed) - expected)}")
            out = Path(config.media_dir) / "cauchy_tangent" / "voiceover"
            out.mkdir(parents=True, exist_ok=True)
            for cue, group in enumerate(MANBOO_GROUPS, 1):
                combined = AudioSegment.empty()
                clips = []
                for number in group:
                    path = indexed[number]
                    segment = AudioSegment.from_file(path)
                    clips.append({"number": number, "file": str(path.relative_to(ROOT)),
                                  "offset": len(combined) / 1000,
                                  "duration": len(segment) / 1000})
                    # Preserve the supplied recordings and their natural pauses.
                    combined += segment
                target = out / f"cue_{cue:03d}.wav"
                combined.export(str(target), format="wav")
                voiceovers[cue] = {"path": target.resolve(), "duration": len(combined) / 1000,
                                   "clips": clips}
            return voiceovers

        # Also support the original one-file-per-paragraph convention.
        for number in range(1, len(NARRATION) + 1):
            path = next((ROOT / "配音" / f"{number:03d}{ext}" for ext in (".mp3", ".wav", ".m4a")
                         if (ROOT / "配音" / f"{number:03d}{ext}").exists()), None)
            if path is not None:
                duration = len(AudioSegment.from_file(path)) / 1000
                voiceovers[number] = {"path": path, "duration": duration,
                                      "clips": [{"number": number, "file": str(path.relative_to(ROOT)),
                                                 "offset": 0.0, "duration": duration}]}
        return voiceovers

    def wait_for_audio_part(self, part, fallback=0.0):
        audio = self.voiceovers.get(self.cues[-1]["number"])
        if audio and len(audio["clips"]) >= part:
            remaining = self.cue_start + audio["clips"][part - 1]["offset"] - self.renderer.time
        else:
            remaining = fallback
        if remaining > 0:
            self.wait(math.ceil(remaining * config.frame_rate - 1e-7) / config.frame_rate)

    def cue(self, number):
        text, duration = NARRATION[number - 1]
        if self.subtitle is not None:
            self.remove(self.subtitle)
        # Reserve a separate two-line subtitle strip below all math/graphics.
        lines, rest = [], text
        while len(rest) > 31:
            split = next((i + 1 for i in range(30, -1, -1) if rest[i] in "，。；："), 30)
            lines.append(rest[:split])
            rest = rest[split:]
        lines.append(rest)
        caption = self.zh("\n".join(lines), 25)
        if caption.width > 12.7:
            caption.scale_to_fit_width(12.7)
        caption.to_edge(DOWN, buff=0.23)
        background = BackgroundRectangle(caption, color=BLACK, fill_opacity=0.76, buff=0.15)
        self.subtitle = VGroup(background, caption).set_z_index(100)
        self.add(self.subtitle)
        audio = self.voiceovers.get(number)
        self.cue_start = float(self.renderer.time)
        cue = {"number": number, "text": text, "start": self.cue_start}
        if audio is not None:
            duration = audio["duration"] + 0.25
            # Scene.add_sound skips audio after a cached animation. Insert at
            # the explicit cue time so cached video still gets every recording.
            if config.write_to_movie:
                self.renderer.file_writer.add_sound(str(audio["path"]), self.cue_start)
            cue.update({"audio_file": str(audio["path"]), "audio_duration": audio["duration"],
                        "audio_clips": audio["clips"]})
        self.cue_duration = math.ceil(duration * config.frame_rate - 1e-7) / config.frame_rate
        self.cues.append(cue)

    def finish_cue(self):
        remaining = self.cue_duration - (self.renderer.time - self.cue_start)
        if remaining > 0:
            self.wait(math.ceil(remaining * config.frame_rate - 1e-7) / config.frame_rate)
        self.cues[-1]["end"] = float(self.renderer.time)

    def clear_stage(self):
        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.6)
        self.clear()
        self.subtitle = None

    def graph(self, filled=False):
        # Equal scale on both axes, with a separate right-hand formula column.
        axes = Axes(
            x_range=[-3.6, 3.6, 1], y_range=[-2.4, 2.4, 1],
            x_length=6.15, y_length=4.10,
            axis_config={"include_ticks": False, "include_tip": True,
                         "tip_width": 0.11, "tip_height": 0.13,
                         "color": GREY_B, "stroke_width": 1.5},
        ).move_to(LEFT * 3.55 + DOWN * 0.1)
        curve = ParametricFunction(
            lambda t: axes.c2p(*ellipse_point(self.A, self.B, t)),
            t_range=[0, TAU], color=ELLIPSE_COLOR, stroke_width=4,
        )
        if filled:
            curve.set_fill(ELLIPSE_COLOR, opacity=0.10)
        labels = VGroup(
            self.math("x", 26).next_to(axes.x_axis.get_end(), DOWN, buff=0.1),
            self.math("y", 26).next_to(axes.y_axis.get_end(), LEFT, buff=0.1),
            self.math("O", 24, MUTED).next_to(axes.c2p(0, 0), DL, buff=0.1),
        )
        return axes, curve, labels

    def support_line(self, axes, theta=None, level=1.0, color=LINE_COLOR):
        if theta is None:
            theta = self.THETA
        start, end = clipped_support_segment(self.A, self.B, theta, level)
        return Line(axes.c2p(*start), axes.c2p(*end), color=color, stroke_width=4)

    def right_at(self, mob, y):
        return mob.move_to(np.array([3.45, y, 0]))

    def coordinate_label(self, point):
        # Leave room above both the ellipse and the descending tangent.
        return self.math(r"P(x_0,y_0)", 29, POINT_COLOR).next_to(
            point, UP, buff=0.36,
        ).shift(RIGHT * 0.25)

    def intro(self):
        self.next_section("开场")
        self.chapters.append({"title": "开场", "start": 0.0})
        axes, curve, labels = self.graph()
        VGroup(axes, curve, labels).shift(RIGHT * 3.55 + DOWN * 0.25)
        point = Dot(axes.c2p(*ellipse_point(self.A, self.B, self.THETA)),
                    color=POINT_COLOR, radius=0.075)
        p_label = self.coordinate_label(point)
        tangent = self.support_line(axes)
        title = self.zh("用柯西不等式证明椭圆的切线", 46, POINT_COLOR).set_y(3.15)

        # Establish the geometry before introducing the topic in the subtitle.
        self.play(Create(axes), FadeIn(labels), run_time=0.7)
        self.play(Create(curve), run_time=1.1)
        self.play(Create(tangent), FadeIn(point), run_time=0.8)
        self.play(FadeIn(p_label), run_time=0.6)
        self.wait(0.4)
        self.cue(1)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=1.0)
        self.finish_cue()
        self.clear_stage()

    def candidate_line(self):
        heading = self.heading("01", "先写出一条候选直线")
        axes, curve, labels = self.graph()
        point = Dot(axes.c2p(*ellipse_point(self.A, self.B, self.THETA)), color=POINT_COLOR, radius=0.07)
        p_label = self.coordinate_label(point)
        ellipse_eq = self.right_at(self.math(r"\frac{x^2}{a^2}+\frac{y^2}{b^2}=1", 41, ELLIPSE_COLOR, 5.9), 1.85)
        assumptions = self.right_at(self.math(r"a>0,\quad b>0,\quad P\in E", 29, MUTED), 0.87)
        candidate = self.right_at(self.math(r"\ell:\ \frac{x x_0}{a^2}+\frac{y y_0}{b^2}=1", 38, LINE_COLOR, 6.1), -0.25)
        p_on_line = self.right_at(self.math(r"\frac{x_0^2}{a^2}+\frac{y_0^2}{b^2}=1\quad\Rightarrow\quad P\in\ell", 32, POINT_COLOR, 6.05), -1.40)
        warning = self.right_at(self.zh("只需证明：只有一个交点", 28), -2.28)
        self.cue(2)
        self.play(FadeIn(heading), Create(axes), Create(curve), FadeIn(labels), Write(ellipse_eq), FadeIn(assumptions), run_time=1.8)
        self.play(FadeIn(point), Write(p_label), run_time=0.8)
        self.finish_cue()
        self.cue(3)
        self.play(Write(candidate), Create(self.support_line(axes)), run_time=1.6)
        self.finish_cue()
        self.cue(4)
        self.play(Write(p_on_line), run_time=1.4)
        self.play(Indicate(point, color=POINT_COLOR), run_time=0.8)
        self.wait_for_audio_part(2)
        self.play(FadeIn(warning), run_time=0.6)
        self.finish_cue()
        self.clear_stage()

    def cauchy_bound(self):
        heading = self.heading("02", "柯西不等式：给出全局上界")
        conditions = VGroup(
            self.math(r"Q(x,y)\in E:\quad \frac{x^2}{a^2}+\frac{y^2}{b^2}=1", 33, MOVING_COLOR),
            self.math(r"P(x_0,y_0)\in E:\quad \frac{x_0^2}{a^2}+\frac{y_0^2}{b^2}=1", 33, POINT_COLOR),
        ).arrange(RIGHT, buff=0.65).set_y(2.07)
        if conditions.width > 12.7:
            conditions.scale_to_fit_width(12.7)
        vectors = self.math(
            r"\mathbf u=\left(\frac{x}{a},\frac{y}{b}\right),\qquad"
            r"\mathbf v=\left(\frac{x_0}{a},\frac{y_0}{b}\right)", 40,
        ).set_y(0.98)
        lengths = self.math(r"\|\mathbf u\|=\|\mathbf v\|=1", 33, MUTED).set_y(0.05)
        generic = self.math(r"(\mathbf u\cdot\mathbf v)^2\leq\|\mathbf u\|^2\|\mathbf v\|^2", 48).set_y(-1.12)
        expanded = self.math(
            r"\left(\frac{x x_0}{a^2}+\frac{y y_0}{b^2}\right)^2"
            r"\leq\left(\frac{x^2}{a^2}+\frac{y^2}{b^2}\right)"
            r"\left(\frac{x_0^2}{a^2}+\frac{y_0^2}{b^2}\right)=1", 43,
        ).set_y(-1.12)
        bound = self.math(r"-1\leq\frac{x x_0}{a^2}+\frac{y y_0}{b^2}\leq1", 53, MOVING_COLOR).set_y(-1.25)
        upper = self.math(r"\boxed{\ F(Q)=\frac{x x_0}{a^2}+\frac{y y_0}{b^2}\leq1\ }", 50, POINT_COLOR).set_y(-1.38)
        self.cue(5)
        self.play(FadeIn(heading), FadeIn(conditions), Write(vectors), run_time=1.8)
        self.finish_cue()
        self.cue(6)
        self.play(Write(lengths), run_time=1.0)
        self.finish_cue()
        self.cue(7)
        self.play(Write(generic), run_time=1.4)
        self.finish_cue()
        self.cue(8)
        self.play(ReplacementTransform(generic, expanded), run_time=1.5)
        self.finish_cue()
        self.cue(9)
        self.play(ReplacementTransform(expanded, bound), run_time=1.1)
        self.wait_for_audio_part(2, fallback=1.4)
        self.play(ReplacementTransform(bound, upper), run_time=1.1)
        self.finish_cue()
        self.clear_stage()

    def geometric_meaning(self):
        heading = self.heading("03", "上界的几何意义：整条椭圆在同侧")
        axes, curve, labels = self.graph(filled=True)
        p = Dot(axes.c2p(*ellipse_point(self.A, self.B, self.THETA)), color=POINT_COLOR, radius=0.075)
        p_label = self.math("P", 28, POINT_COLOR).next_to(p, UR, buff=0.14)
        level = ValueTracker(1.22)
        line = always_redraw(lambda: self.support_line(axes, level=level.get_value()))
        f_formula = self.right_at(self.math(r"F(Q)=\frac{x x_0}{a^2}+\frac{y y_0}{b^2}", 39, WHITE, 6.1), 1.9)
        bound = self.right_at(self.math(r"Q\in E\quad\Rightarrow\quad F(Q)\leq1", 36, ELLIPSE_COLOR, 6.1), 0.8)
        line_label = self.right_at(self.math(r"\ell:\ F=1", 33, LINE_COLOR), -0.17)
        self.cue(10)
        self.play(FadeIn(heading), Create(axes), FadeIn(curve), FadeIn(labels), FadeIn(p), FadeIn(p_label), Write(f_formula), Write(bound), run_time=1.5)
        self.add(line, level)
        self.play(level.animate.set_value(1), Write(line_label), run_time=1.8)
        line.clear_updaters()
        self.finish_cue()
        theta = ValueTracker(self.THETA + 0.85)
        q = Dot(color=MOVING_COLOR, radius=0.065)
        q.add_updater(lambda mob: mob.move_to(axes.c2p(*ellipse_point(self.A, self.B, theta.get_value()))))
        q.update()
        q_label = self.math("Q", 27, MOVING_COLOR)
        q_label.add_updater(lambda mob: mob.next_to(q, DL, buff=0.14))
        q_label.update()
        numeric_label = self.math(r"F(Q)=", 46, MOVING_COLOR).move_to([2.5, -1.23, 0])
        number = DecimalNumber(np.cos(theta.get_value() - self.THETA), num_decimal_places=2,
                               include_sign=False, font_size=46, color=MOVING_COLOR)
        def update_number(mob):
            mob.set_value(float(np.cos(theta.get_value() - self.THETA)))
            mob.next_to(numeric_label, RIGHT, buff=0.18)
        number.add_updater(update_number)
        number.update()
        status = self.right_at(self.zh("数值始终不超过 1", 28, MUTED), -2.25)
        self.cue(11)
        self.add(theta)
        self.play(FadeIn(q), FadeIn(q_label), FadeIn(numeric_label), FadeIn(number), FadeIn(status), run_time=0.8)
        self.play(theta.animate.set_value(self.THETA + 2.4), run_time=3.4, rate_func=linear)
        self.finish_cue()
        self.cue(12)
        self.play(theta.animate.set_value(self.THETA + PI), run_time=1.5, rate_func=linear)
        opposite = self.right_at(self.zh("对径点：F = −1", 28, MOVING_COLOR), -2.25)
        self.play(ReplacementTransform(status, opposite), run_time=0.5)
        self.finish_cue()
        self.cue(13)
        self.play(theta.animate.set_value(self.THETA + TAU), run_time=3.7, rate_func=linear)
        contact = self.right_at(self.zh("在 P 处：F = 1", 28, POINT_COLOR), -2.25)
        self.play(ReplacementTransform(opposite, contact), Circumscribe(number, color=POINT_COLOR), run_time=0.8)
        self.finish_cue()
        self.clear_stage()

    def equality_case(self):
        heading = self.heading("04", "取等条件：公共点只能是 P")
        premise = self.math(r"Q\in E\cap\ell\quad\Rightarrow\quad\|\mathbf u\|=\|\mathbf v\|=1,\quad\mathbf u\cdot\mathbf v=1", 37).set_y(2.04)
        line1 = self.math(r"\mathbf u=\lambda\mathbf v", 49, MOVING_COLOR).set_y(0.99)
        line2 = self.math(r"1=\|\mathbf u\|=|\lambda|\,\|\mathbf v\|=|\lambda|\quad\Rightarrow\quad\lambda=\pm1", 39).set_y(-0.04)
        line3 = self.math(r"1=\mathbf u\cdot\mathbf v=\lambda\|\mathbf v\|^2=\lambda", 44, POINT_COLOR).set_y(-1.08)
        conclusion = self.math(r"\mathbf u=\mathbf v\quad\Rightarrow\quad(x,y)=(x_0,y_0)\quad\Rightarrow\quad Q=P", 39, POINT_COLOR).set_y(-2.12)
        self.cue(14)
        self.play(FadeIn(heading), Write(premise), run_time=1.5)
        self.finish_cue()
        self.cue(15)
        self.play(Write(line1), run_time=1)
        self.finish_cue()
        self.cue(16)
        self.play(Write(line2), run_time=1.3)
        self.finish_cue()
        self.cue(17)
        self.play(Write(line3), run_time=1.3)
        self.finish_cue()
        self.cue(18)
        self.play(Write(conclusion), run_time=1.4)
        self.finish_cue()
        self.cue(19)
        self.play(FadeOut(line1), FadeOut(line2), FadeOut(line3), FadeOut(conclusion), run_time=0.5)
        reasons = VGroup(
            self.zh("① 整个椭圆位于直线同侧", 33, ELLIPSE_COLOR),
            self.zh("② 直线与椭圆仅在 P 处接触", 33, MOVING_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).set_y(0.25)
        result = self.math(r"\boxed{\ \ell:\ \frac{x x_0}{a^2}+\frac{y y_0}{b^2}=1\ }", 58, LINE_COLOR).set_y(-1.65)
        self.play(FadeIn(reasons), Write(result), run_time=1.6)
        self.finish_cue()
        self.clear_stage()

    def vertex_cases(self):
        heading = self.heading("05", "切点变化，公式依然成立")
        axes, curve, labels = self.graph()
        theta = ValueTracker(self.THETA)
        line = always_redraw(lambda: self.support_line(axes, theta.get_value()))
        p = Dot(color=POINT_COLOR, radius=0.075)
        p.add_updater(lambda mob: mob.move_to(axes.c2p(*ellipse_point(self.A, self.B, theta.get_value()))))
        p.update()
        p_label = self.math("P", 27, POINT_COLOR)
        p_label.add_updater(lambda mob: mob.next_to(p, UR, buff=0.14))
        p_label.update()
        general = self.right_at(self.math(r"\frac{x x_0}{a^2}+\frac{y y_0}{b^2}=1", 45, LINE_COLOR, 5.8), 1.85)
        parameters = self.right_at(self.math(r"x_0=a\cos t,\quad y_0=b\sin t", 32, POINT_COLOR, 6), 0.65)
        note = self.right_at(self.zh("同一个方程，包含所有切点", 28, MUTED), -2.15)
        self.cue(20)
        self.add(theta)
        self.play(FadeIn(heading), Create(axes), Create(curve), FadeIn(labels), Write(general), Write(parameters), FadeIn(note), run_time=1.5)
        self.add(line, p, p_label)
        self.play(theta.animate.set_value(TAU), run_time=3.0, rate_func=linear)
        self.finish_cue()
        self.cue(21)
        special = self.right_at(self.math(r"P(a,0)\quad\Rightarrow\quad\boxed{x=a}", 40, POINT_COLOR, 5.9), -0.85)
        self.play(Write(special), run_time=1)
        self.finish_cue()
        self.cue(22)
        self.play(theta.animate.set_value(TAU + PI / 2), run_time=2.0, rate_func=linear)
        top = self.right_at(self.math(r"P(0,b)\quad\Rightarrow\quad\boxed{y=b}", 40, POINT_COLOR, 5.9), -0.85)
        self.play(ReplacementTransform(special, top), run_time=0.7)
        self.finish_cue()
        self.cue(23)
        self.play(theta.animate.set_value(TAU + PI), run_time=1.8, rate_func=linear)
        left = self.right_at(self.math(r"P(-a,0)\quad\Rightarrow\quad\boxed{x=-a}", 38, POINT_COLOR, 5.9), -0.85)
        self.play(ReplacementTransform(top, left), run_time=0.5)
        self.wait(0.6)
        self.play(theta.animate.set_value(TAU + 3 * PI / 2), run_time=1.8, rate_func=linear)
        bottom = self.right_at(self.math(r"P(0,-b)\quad\Rightarrow\quad\boxed{y=-b}", 38, POINT_COLOR, 5.9), -0.85)
        self.play(ReplacementTransform(left, bottom), run_time=0.5)
        self.finish_cue()
        self.clear_stage()

    def export_timeline(self):
        out = Path(config.media_dir) / "cauchy_tangent"
        out.mkdir(parents=True, exist_ok=True)
        (out / "timeline.json").write_text(json.dumps({
            "scene": type(self).__name__, "duration": float(self.renderer.time),
            "chapters": self.chapters, "cues": self.cues,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        def stamp(seconds):
            ms = round(seconds * 1000)
            h, ms = divmod(ms, 3600000)
            m, ms = divmod(ms, 60000)
            s, ms = divmod(ms, 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
        srt = "\n\n".join(
            f"{cue['number']}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n{cue['text']}"
            for cue in self.cues
        )
        (out / "CauchyEllipseTangent.srt").write_text(srt + "\n", encoding="utf-8-sig")
        clips = []
        for cue in self.cues:
            for clip in cue.get("audio_clips", []):
                start = cue["start"] + clip["offset"]
                clips.append({**clip, "cue": cue["number"], "start": start,
                              "end": start + clip["duration"]})
        (out / "voiceover_manifest.json").write_text(
            json.dumps({"clips": clips}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    # Export the narration without requiring a render.
    script = "\n".join(f"{i:03d}  {text}" for i, (text, _) in enumerate(NARRATION, 1))
    print(script)
