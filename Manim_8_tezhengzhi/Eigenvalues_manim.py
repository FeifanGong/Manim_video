"""矩阵的特征值与特征向量，画面风格参考 Affine_Trans_manim.py。

Render: .\render.ps1 -Quality h
Export narration: python Eigenvalues_manim.py
Chinese uses Text; MathTex contains ASCII LaTeX only.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

from manim import *
import numpy as np
from pydub import AudioSegment


ROOT = Path(__file__).resolve().parent
CJK_FONT = "Microsoft YaHei"
BG = "#10131A"
MUTED = "#A9B5C7"
ACCENT = "#FFCF5C"
BLUE_VECTOR = "#63B5F6"
GREEN_VECTOR = "#76DBC5"
RED_VECTOR = "#FF8585"
PANEL = "#19212E"

MATRIX_A = np.array([[2, 0], [0, 3]])
MATRIX_B = np.array([[5, -1], [-1, 5]])

# Scenes 8--10 share this exact viewport, including the same NumberPlane object.
B_X_RANGE = (-7.5, 7.5, 1)
B_Y_RANGE = (-4.2, 7.0, 1)
B_UNIT = 0.5

# dvisvgm on Windows can fail when its input path contains Chinese characters.
# Only the intermediate TeX cache goes to an ASCII system-temp directory.
TEX_CACHE = Path(tempfile.gettempdir()) / "manim_eigenvalues_tex"
TEX_CACHE.mkdir(parents=True, exist_ok=True)
config.tex_dir = str(TEX_CACHE)


def column(x, y):
    return rf"\begin{{bmatrix}}{x}\\{y}\end{{bmatrix}}"


def matrix_tex(matrix):
    rows = ("&".join(str(int(value)) for value in row) for row in matrix)
    return r"\begin{bmatrix}" + r"\\".join(rows) + r"\end{bmatrix}"


A_TEX = matrix_tex(MATRIX_A)
B_TEX = matrix_tex(MATRIX_B)

# Each numbered line is a subtitle and an optional voiceover cue.
# Use Arabic numerals for numeric values, including coordinates and negatives.
# Use parenthesized pairs for inline vectors and "一个矩阵" in prose.
# Optional audio: 配音/001.mp3, 配音/002.mp3, ... (also WAV or M4A).
NARRATION = [
    ("今天我们来解释什么是矩阵的特征值和特征向量。", 3.5),
    ("假如我们有一个矩阵 A，让它作用在向量 (x,y) 上。", 4.5),
    ("结果就是 (2x,3y)：横坐标扩大 2 倍，纵坐标扩大 3 倍。", 6.0),
    ("观察这个点：(1,1) 变成 (2,3)。横向走 2 格，纵向走 3 格。", 6.5),
    ("先只看水平方向。(1,0) 变成 (2,0)，长度扩大 2 倍，方向不变。", 7.0),
    ("再看竖直方向。(0,1) 变成 (0,3)，长度扩大 3 倍，方向不变。", 7.0),
    ("因此，横轴与纵轴上的所有非 0 向量，都是 A 的特征向量。", 6.5),
    ("但是 (1,1) 变成 (2,3)。原来沿着对角线，现在向量偏向了更陡的方向。", 7.5),
    ("(1,1) 和 (2,3) 的方向不同，所以 (1,1) 不是 A 的特征向量。", 6.0),
    ("特征向量满足 A v 等于拉姆达 v，其中 v 不能是 0 向量。", 5.5),
    ("v 是特征向量，拉姆达是对应的特征值。", 4.0),
    ("正特征值保持同向，负特征值使向量反向，0 特征值把向量压到原点。", 7.0),
    ("现在换成矩阵 B：对角线是 5，另外 2 个元素都是 -1。", 6.0),
    ("(1,0) 变成 (5,-1)；(0,1) 变成 (-1,5)。2 个坐标轴方向都偏了。", 7.5),
    ("再取 8 个不同方向一起变换。你会发现，只有这 2 条对角线上的向量，仍沿原来的直线伸缩。", 10.0),
    ("怎样求这些倍数？由 B v 等于拉姆达 v，可得 B 减拉姆达 I 乘 v 等于 0。", 8.0),
    ("要使这个方程有非 0 解，B 减拉姆达 I 的行列式必须为 0。", 7.0),
    ("计算得到，5 减拉姆达的平方，再减 1，等于 0。因此特征值是 4 和 6。", 8.5),
    ("代入特征值 4，得到 x 减 y 等于 0，所以可以选 (1,1) 作为特征向量。", 8.0),
    ("代入特征值 6，得到 x 加 y 等于 0，所以可以选 (-1,1) 作为特征向量。", 8.0),
    ("先看 (1,1)。B 把它变成 (4,4)，也就是原向量的 4 倍。", 6.5),
    ("变换前后的向量都在 y 等于 x 的直线上，方向没有改变。", 5.5),
    ("再看 (-1,1)。B 把它变成 (-6,6)，也就是原向量的 6 倍。", 7.0),
    ("变换前后的向量都在 y 等于负 x 的直线上，方向同样没有改变。", 5.5),
    ("把 2 个方向放在一起：B 的特征方向是 2 条对角线，对应的特征值分别是 4 和 6。", 8.0),
    ("对这两条直线上的任意非 0 向量，B 都只会分别乘以 4 或 6。", 7.0),
    ("回头比较：A 的特征方向是坐标轴，B 的特征方向是 2 条对角线。", 7.0),
    ("找特征向量，就是找变换后仍与原向量共线的非 0 向量；对应的倍数，就是特征值。", 8.0),
]


class EigenvaluesAndEigenvectors(Scene):
    """Complete Chinese lesson with optional numbered local voice clips."""

    def construct(self):
        self.camera.background_color = BG
        self.subtitle = None
        self.cues = []
        self.subtitle_events = []
        self.observations = []
        self.chapters = []
        self.diagonal_action()
        self.diagonal_directions()
        self.diagonal_counterexample()
        self.definition()
        self.new_matrix()
        self.find_eigenvalues()
        self.find_eigenvectors()
        self.stretch_direction(1)
        self.stretch_direction(2)
        self.both_directions()
        self.summary()
        self.export_timeline()

    @staticmethod
    def zh(text, font_size=30, color=WHITE, max_width=12.6):
        result = Text(text, font=CJK_FONT, font_size=font_size, color=color)
        if result.width > max_width:
            result.scale_to_fit_width(max_width)
        return result

    @staticmethod
    def math(tex, font_size=40, color=WHITE, max_width=12.6):
        result = MathTex(tex, font_size=font_size, color=color)
        if result.width > max_width:
            result.scale_to_fit_width(max_width)
        return result

    def heading(self, number, text):
        self.next_section(text)
        self.chapters.append({"title": text, "start": float(self.renderer.time)})
        row = VGroup(self.zh(number, 20, ACCENT), self.zh(text, 32, ACCENT))
        row.arrange(RIGHT, buff=0.28).to_edge(UP, buff=0.32).to_edge(LEFT, buff=0.55)
        rule = Line(LEFT * 6.55, RIGHT * 6.55, color=MUTED, stroke_width=1)
        rule.set_opacity(0.22).set_y(3.10)
        return VGroup(row, rule)

    @staticmethod
    def right_at(mobject, y):
        if mobject.width > 4.2:
            mobject.scale_to_fit_width(4.2)
        return mobject.move_to([4.4, y, 0])

    def say(self, text):
        """Change the visible phrase at its action, and timestamp it for SRT."""
        if self.subtitle is not None:
            self.remove(self.subtitle)
        now = float(self.renderer.time)
        if self.subtitle_events and "end" not in self.subtitle_events[-1]:
            self.subtitle_events[-1]["end"] = now
        self.subtitle_events.append({"text": text, "start": now})
        lines, rest = [], text
        while len(rest) > 31:
            # Allow a short first clause rather than orphaning a final number.
            split = next((i + 1 for i in range(30, 9, -1) if rest[i] in "，。；："), 30)
            lines.append(rest[:split])
            rest = rest[split:]
        lines.append(rest)
        caption = self.zh("\n".join(lines), 25).to_edge(DOWN, buff=0.23)
        background = BackgroundRectangle(caption, color=BLACK, fill_opacity=0.76, buff=0.15)
        self.subtitle = VGroup(background, caption).set_z_index(100)
        self.add(self.subtitle)

    def cue(self, number, opening=None):
        text, duration = NARRATION[number - 1]
        audio = next((ROOT / "配音" / f"{number:03d}{ext}" for ext in (".mp3", ".wav", ".m4a")
                      if (ROOT / "配音" / f"{number:03d}{ext}").is_file()), None)
        if audio is not None:
            duration = max(duration, len(AudioSegment.from_file(audio)) / 1000 + 0.25)
            self.add_sound(str(audio))
        self.cue_start = float(self.renderer.time)
        self.cue_duration = duration
        self.cues.append({"number": number, "text": text, "start": self.cue_start})
        self.say(text if opening is None else opening)

    def finish_cue(self):
        remaining = self.cue_duration - (self.renderer.time - self.cue_start)
        if remaining > 0:
            self.wait(remaining)
        self.cues[-1]["end"] = float(self.renderer.time)
        self.subtitle_events[-1]["end"] = float(self.renderer.time)

    def clear_stage(self):
        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=0.5)
        self.clear()
        self.subtitle = None

    def graph(self, x_range=(-2.4, 4.1, 1), y_range=(-0.6, 3.8, 1), unit=1.15):
        # Equal units on x and y: lengths, slopes and angles stay meaningful.
        plane = NumberPlane(
            x_range=x_range, y_range=y_range,
            x_length=(x_range[1] - x_range[0]) * unit,
            y_length=(y_range[1] - y_range[0]) * unit,
            background_line_style={"stroke_color": MUTED, "stroke_opacity": 0.12, "stroke_width": 1},
            faded_line_ratio=1,
            axis_config={"include_ticks": False, "include_tip": True, "color": GREY_B,
                         "stroke_width": 1.5, "tip_width": 0.10, "tip_height": 0.12},
        ).move_to([-2.6, 0.05, 0])
        labels = VGroup(
            self.math("x", 24, MUTED).next_to(plane.x_axis.get_end(), DOWN, buff=0.1),
            self.math("y", 24, MUTED).next_to(plane.y_axis.get_end(), LEFT, buff=0.1),
            self.math("O", 21, MUTED).next_to(plane.c2p(0, 0), DL, buff=0.08),
        )
        return plane, labels

    def grid_patch(self, plane, x_bounds, y_bounds, step):
        """A moving sample of the plane above a fixed, faint reference grid."""
        segments = [((x, y_bounds[0]), (x, y_bounds[1]))
                    for x in np.arange(x_bounds[0], x_bounds[1] + step / 2, step)]
        segments += [((x_bounds[0], y), (x_bounds[1], y))
                     for y in np.arange(y_bounds[0], y_bounds[1] + step / 2, step)]
        return VGroup(*[Line(plane.c2p(*a), plane.c2p(*b), color=ACCENT,
                            stroke_width=1.5, stroke_opacity=0.5) for a, b in segments]).set_z_index(1)

    @staticmethod
    def mapped_grid(plane, grid, matrix):
        target = grid.copy()
        for source, line in zip(grid, target):
            start = matrix @ plane.p2c(source.get_start())[:2]
            end = matrix @ plane.p2c(source.get_end())[:2]
            line.put_start_and_end_on(plane.c2p(*start), plane.c2p(*end))
        return target

    def change_heading(self, old, number, text):
        heading = self.heading(number, text)
        return heading, FadeTransform(old, heading, stretch=False)

    def observe(self, kind, **details):
        """Record visible action endpoints for checking the rendered timeline."""
        self.observations.append({"kind": kind, "time": float(self.renderer.time), **details})

    @staticmethod
    def vector(plane, coordinates, color, width=5, z_index=4):
        return Arrow(plane.c2p(0, 0), plane.c2p(*coordinates), buff=0, color=color,
                     stroke_width=width, max_tip_length_to_length_ratio=0.18,
                     max_stroke_width_to_length_ratio=12).set_z_index(z_index)

    def point_label(self, plane, coordinates, tex, color=WHITE, direction=UR):
        return self.math(tex, 27, color).next_to(plane.c2p(*coordinates), direction, buff=0.12)

    def diagonal_action(self):
        heading = self.heading("01", "矩阵的特征值与特征向量")
        plane, labels = self.graph()
        matrix = self.right_at(self.math("A=" + A_TEX, 40, ACCENT), 1.95)
        input_action = self.right_at(self.math(r"\mathbf v=" + column("x", "y"), 42), 0.45)
        mapping = self.right_at(self.math(r"A\mathbf v=" + column("2x", "3y"), 42), 0.45)
        horizontal = self.right_at(self.zh("横坐标 ×2", 28, BLUE_VECTOR), -1.05)
        vertical = self.right_at(self.zh("纵坐标 ×3", 28, GREEN_VECTOR), -1.75)
        grid = self.grid_patch(plane, (-0.5, 1.5), (-0.15, 1.05), 0.25)
        grid_target = self.mapped_grid(plane, grid, MATRIX_A)
        square = Polygon(*(plane.c2p(*p) for p in ((0, 0), (1, 0), (1, 1), (0, 1))),
                         color=BLUE_VECTOR, fill_color=BLUE_VECTOR, fill_opacity=0.12, stroke_width=2)
        original = square.copy().set_fill(opacity=0).set_stroke(opacity=0.35, width=1.5)
        rectangle = Polygon(*(plane.c2p(*p) for p in ((0, 0), (2, 0), (2, 3), (0, 3))),
                            color=GREEN_VECTOR, fill_color=GREEN_VECTOR, fill_opacity=0.12, stroke_width=2)
        point = Dot(plane.c2p(1, 1), color=ACCENT, radius=0.065).set_z_index(5)
        point_label = self.point_label(plane, (1, 1), "P(1,1)", ACCENT)
        final_label = self.point_label(plane, (2, 3), "P'(2,3)", ACCENT)
        numbers = VGroup(
            self.math("2", 25, BLUE_VECTOR).next_to(plane.c2p(2, 0), DOWN, buff=0.12),
            self.math("3", 25, GREEN_VECTOR).next_to(plane.c2p(0, 3), LEFT, buff=0.12),
        )
        # Start on the actual example, with no separate title card or fade-in.
        self.add(heading, plane, labels, matrix)
        self.cue(1)
        self.finish_cue()
        self.cue(2)
        self.play(Write(input_action), Create(grid), Create(square), run_time=1.1)
        self.add(original)
        self.finish_cue()
        self.cue(3, "结果就是 (2x,3y)：")
        self.play(Transform(grid, grid_target), Transform(square, rectangle),
                  ReplacementTransform(input_action, mapping), run_time=2.3)
        self.say("横坐标扩大 2 倍，纵坐标扩大 3 倍。")
        self.play(FadeIn(horizontal), FadeIn(vertical), FadeIn(numbers), run_time=0.5)
        self.finish_cue()
        self.cue(4, "观察这个点：(1,1) 变成 (2,3)。")
        self.play(FadeIn(point), FadeIn(point_label), run_time=0.4)
        ghost_point = point.copy().set_opacity(0.35)
        self.add(ghost_point)
        self.play(point.animate.move_to(plane.c2p(2, 3)), run_time=1.9)
        self.play(FadeIn(final_label), point_label.animate.set_opacity(0.4), run_time=0.3)
        self.say("横向走 2 格，纵向走 3 格。")
        guides = VGroup(
            DashedLine(plane.c2p(0, 0), plane.c2p(2, 0), color=BLUE_VECTOR),
            DashedLine(plane.c2p(2, 0), plane.c2p(2, 3), color=GREEN_VECTOR),
        )
        self.play(Create(guides), run_time=0.7)
        self.finish_cue()
        self.a_stage = dict(heading=heading, plane=plane, labels=labels, matrix=matrix, grid=grid,
                            extras=VGroup(mapping, horizontal, vertical, square, original, point,
                                          point_label, final_label, ghost_point, numbers, guides))

    def diagonal_directions(self):
        stage = self.a_stage
        plane = stage["plane"]
        e1 = self.vector(plane, (1, 0), BLUE_VECTOR)
        e2 = self.vector(plane, (0, 1), GREEN_VECTOR)
        ghost1 = self.vector(plane, (1, 0), GREY_B, 2, 6)
        ghost2 = self.vector(plane, (0, 1), GREY_B, 2, 6)
        eq1 = self.right_at(self.math("A" + column(1, 0) + "=2" + column(1, 0), 39, BLUE_VECTOR), 0.55)
        eq2 = self.right_at(self.math("A" + column(0, 1) + "=3" + column(0, 1), 39, GREEN_VECTOR), -0.85)
        conclusion = self.right_at(self.zh("只改变长度，方向不变", 25, ACCENT), -2.15)
        tag1 = self.point_label(plane, (2, 0), "(2,0)", BLUE_VECTOR, DOWN)
        tag2 = self.point_label(plane, (0, 3), "(0,3)", GREEN_VECTOR, RIGHT)
        self.cue(5, "先只看水平方向。")
        heading, heading_change = self.change_heading(stage["heading"], "02", "先看 2 个坐标轴方向")
        self.play(heading_change, FadeOut(stage["extras"]), stage["grid"].animate.set_opacity(0.12),
                  GrowArrow(e1), run_time=0.7)
        self.add(ghost1)
        self.say("(1,0) 变成 (2,0)，长度扩大 2 倍，方向不变。")
        self.play(Transform(e1, self.vector(plane, (2, 0), BLUE_VECTOR)), run_time=2.1)
        self.play(Write(eq1), FadeIn(tag1), run_time=0.6)
        self.finish_cue()
        self.cue(6, "再看竖直方向。")
        self.play(GrowArrow(e2), eq1.animate.set_opacity(0.35), run_time=0.7)
        self.add(ghost2)
        self.say("(0,1) 变成 (0,3)，长度扩大 3 倍，方向不变。")
        self.play(Transform(e2, self.vector(plane, (0, 3), GREEN_VECTOR)), run_time=2.1)
        self.play(Write(eq2), FadeIn(tag2), run_time=0.6)
        self.finish_cue()
        self.cue(7)
        self.play(FadeIn(conclusion), eq1.animate.set_opacity(1),
                  Indicate(e1, color=BLUE_VECTOR), Indicate(e2, color=GREEN_VECTOR), run_time=1.4)
        self.finish_cue()
        stage.update(heading=heading, extras=VGroup(e1, e2, ghost1, ghost2, eq1, eq2, conclusion, tag1, tag2))

    def diagonal_counterexample(self):
        stage = self.a_stage
        plane = stage["plane"]
        line = DashedLine(plane.c2p(-0.4, -0.4), plane.c2p(3.5, 3.5),
                          color=MUTED, stroke_width=2, dash_length=0.08)
        ghost = self.vector(plane, (1, 1), BLUE_VECTOR, 3, 6)
        vector = self.vector(plane, (1, 1), RED_VECTOR)
        start_label = self.point_label(plane, (1, 1), "(1,1)", BLUE_VECTOR, RIGHT)
        end_label = self.point_label(plane, (2, 3), "(2,3)", RED_VECTOR)
        equation = self.right_at(self.math("A" + column(1, 1) + "=" + column(2, 3), 38, RED_VECTOR), 0.45)
        direction_note = self.right_at(self.zh("(1,1) 与 (2,3)\n方向不同", 27, RED_VECTOR), -1.0)
        conclusion = self.right_at(self.zh("(1,1) 不是 A 的特征向量", 25, RED_VECTOR), -2.15)
        arc = Arc(radius=0.9, start_angle=PI / 4, angle=np.arctan2(3, 2) - PI / 4,
                  arc_center=plane.c2p(0, 0), color=RED_VECTOR, stroke_width=5)
        self.cue(8, "但是 (1,1) 变成 (2,3)。")
        heading, heading_change = self.change_heading(stage["heading"], "03", "对比 (1,1) 与 (2,3)：方向不同")
        self.play(heading_change, FadeOut(stage["extras"]), Create(line),
                  GrowArrow(vector), FadeIn(start_label), run_time=0.7)
        self.add(ghost)
        self.play(Transform(vector, self.vector(plane, (2, 3), RED_VECTOR)), run_time=2.4)
        self.play(FadeIn(end_label), Write(equation), run_time=0.5)
        self.say("原来沿着对角线，现在向量偏向了更陡的方向。")
        self.play(Create(arc), FadeIn(direction_note), run_time=0.8)
        self.finish_cue()
        self.cue(9)
        self.play(FadeIn(conclusion), run_time=0.8)
        self.finish_cue()
        self.clear_stage()

    def definition(self):
        heading = self.heading("04", "从图像到定义")
        equation = self.math(r"\boxed{A\mathbf v=\lambda\mathbf v},\qquad\mathbf v\ne\mathbf 0", 57).set_y(1.7)
        equation.set_color_by_tex(r"\boxed{A\mathbf v=\lambda\mathbf v},\qquad\mathbf v\ne\mathbf 0", ACCENT)
        left = VGroup(self.math(r"\mathbf v", 36, BLUE_VECTOR), self.zh("特征向量", 27, BLUE_VECTOR)).arrange(RIGHT, buff=0.2).move_to([-2.7, 0.45, 0])
        right = VGroup(self.math(r"\lambda", 36, GREEN_VECTOR), self.zh("对应的特征值", 27, GREEN_VECTOR)).arrange(RIGHT, buff=0.2).move_to([2.7, 0.45, 0])
        meaning = self.zh("变换后，是原向量的倍数", 27, MUTED).set_y(-0.25)
        cases, arrows, targets = [], [], []
        for center, tex, text, color, factor in (
            (-4.4, r"\lambda>0", "同向伸缩", BLUE_VECTOR, 1.7),
            (0, r"\lambda<0", "反向伸缩", RED_VECTOR, -1),
            (4.4, r"\lambda=0", "压到原点", GREEN_VECTOR, 0),
        ):
            origin = np.array([center - 0.65, -1.85, 0])
            arrow = Arrow(origin, origin + RIGHT, buff=0, color=color, stroke_width=5)
            ghost = arrow.copy().set_color(GREY_B).set_stroke(width=2, opacity=0.5).set_z_index(5)
            baseline = Line(origin - RIGHT * 1.1, origin + RIGHT * 1.9, color=MUTED,
                            stroke_width=1, stroke_opacity=0.25)
            label = self.math(tex, 33, color).move_to([center, -1.0, 0])
            note = self.zh(text, 23, color).move_to([center, -2.55, 0])
            cases.append(VGroup(baseline, ghost, Dot(origin, radius=0.035), label, note))
            arrows.append(arrow)
            targets.append(Arrow(origin, origin + factor * RIGHT, buff=0, color=color, stroke_width=5)
                           if factor else Dot(origin, radius=0.07, color=color))
        self.cue(10)
        self.play(FadeIn(heading), Write(equation), run_time=1.7)
        self.finish_cue()
        self.cue(11)
        self.play(FadeIn(left), FadeIn(right), FadeIn(meaning), run_time=0.8)
        self.finish_cue()
        self.cue(12, "正特征值保持同向，")
        self.play(*[FadeIn(case) for case in cases], *[GrowArrow(arrow) for arrow in arrows], run_time=0.5)
        self.play(Transform(arrows[0], targets[0]), run_time=1.0)
        self.wait(0.5)
        self.say("负特征值使向量反向，")
        self.play(Transform(arrows[1], targets[1]), run_time=1.2)
        self.wait(0.8)
        self.say("0 特征值把向量压到原点。")
        self.play(ReplacementTransform(arrows[2], targets[2]), run_time=1.2)
        self.finish_cue()
        self.clear_stage()

    def new_matrix(self):
        heading = self.heading("05", "换成 B：寻找新的特征方向")
        plane, labels = self.graph(B_X_RANGE, B_Y_RANGE, B_UNIT)
        e1 = self.vector(plane, (1, 0), BLUE_VECTOR)
        e2 = self.vector(plane, (0, 1), GREEN_VECTOR)
        ghosts = VGroup(self.vector(plane, (1, 0), GREY_B, 2, 6), self.vector(plane, (0, 1), GREY_B, 2, 6))
        grid = self.grid_patch(plane, (-0.6, 0.6), (-0.6, 0.6), 0.3)
        grid_source = grid.copy()
        grid_target = self.mapped_grid(plane, grid, MATRIX_B)
        matrix = self.right_at(self.math("B=" + B_TEX, 43, ACCENT), 1.95)
        eq1 = self.right_at(self.math("B" + column(1, 0) + "=" + column(5, -1), 38, BLUE_VECTOR), 0.55)
        eq2 = self.right_at(self.math("B" + column(0, 1) + "=" + column(-1, 5), 38, GREEN_VECTOR), -0.8)
        conclusion = self.right_at(self.zh("坐标轴方向都发生了偏转", 25, RED_VECTOR), -2.15)
        tag1 = self.point_label(plane, (5, -1), "(5,-1)", BLUE_VECTOR, DOWN)
        tag2 = self.point_label(plane, (-1, 5), "(-1,5)", GREEN_VECTOR, UP)
        self.cue(13)
        self.play(FadeIn(heading), Create(plane), FadeIn(labels), Write(matrix),
                  Create(grid), GrowArrow(e1), run_time=1.3)
        self.finish_cue()
        self.cue(14, "(1,0) 变成 (5,-1)；")
        self.add(ghosts[0])
        self.play(Transform(e1, self.vector(plane, (5, -1), BLUE_VECTOR)),
                  Transform(grid, grid_target), run_time=1.8)
        self.play(Write(eq1), FadeIn(tag1), run_time=0.4)
        self.say("(0,1) 变成 (-1,5)。")
        self.play(GrowArrow(e2), run_time=0.3)
        self.add(ghosts[1])
        self.play(Transform(e2, self.vector(plane, (-1, 5), GREEN_VECTOR)),
                  eq1.animate.set_opacity(0.35), run_time=1.8)
        self.play(Write(eq2), FadeIn(tag2), run_time=0.4)
        self.say("2 个坐标轴方向都偏了。")
        self.play(FadeIn(conclusion), run_time=0.4)
        self.finish_cue()
        self.cue(15, "再取 8 个不同方向一起变换。")
        self.play(FadeOut(VGroup(e1, e2, ghosts, eq1, eq2, tag1, tag2, conclusion)),
                  Transform(grid, grid_source), run_time=0.6)
        candidates, outputs = [], []
        for k in range(8):
            direction = 0.75 * np.array([np.cos(k * PI / 4), np.sin(k * PI / 4)])
            color = (BLUE_VECTOR if k in (1, 5) else GREEN_VECTOR) if k % 2 else RED_VECTOR
            candidates.append(self.vector(plane, direction, color, 4))
            outputs.append(self.vector(plane, MATRIX_B @ direction, color, 4))
        references = VGroup(*[arrow.copy().set_color(GREY_B).set_stroke(width=1.5, opacity=0.4)
                              for arrow in candidates]).set_z_index(6)
        lines = VGroup(
            DashedLine(plane.c2p(-4, -4), plane.c2p(6.8, 6.8), color=BLUE_VECTOR,
                       dash_length=0.09, stroke_width=2),
            DashedLine(plane.c2p(-6.8, 6.8), plane.c2p(4, -4), color=GREEN_VECTOR,
                       dash_length=0.09, stroke_width=2),
        ).set_opacity(0.22)
        self.play(*[GrowArrow(arrow) for arrow in candidates], Create(lines), run_time=0.7)
        self.add(references)
        self.play(*[Transform(arrow, target) for arrow, target in zip(candidates, outputs)],
                  Transform(grid, grid_target), run_time=2.6)
        self.observe("candidate_directions_transformed", count=8)
        self.say("你会发现，只有这 2 条对角线上的向量，")
        directions = self.right_at(VGroup(
            self.math("y=x", 40, BLUE_VECTOR), self.math("y=-x", 40, GREEN_VECTOR),
            self.zh("伸缩多少倍？", 27, ACCENT),
        ).arrange(DOWN, buff=0.55), -0.1)
        self.play(*[FadeOut(candidates[k]) for k in (0, 2, 4, 6)],
                  lines.animate.set_opacity(0.65), grid.animate.set_opacity(0.12),
                  FadeIn(directions), run_time=0.8)
        self.say("仍沿原来的直线伸缩。")
        self.finish_cue()
        self.clear_stage()

    def find_eigenvalues(self):
        heading = self.heading("06", "先求特征值：让方程有非 0 解")
        equation = self.math(r"B\mathbf v=\lambda\mathbf v\quad\Longleftrightarrow\quad(B-\lambda I)\mathbf v=\mathbf0", 44).set_y(1.85)
        determinant = self.math(r"\det(B-\lambda I)=\begin{vmatrix}5-\lambda&-1\\-1&5-\lambda\end{vmatrix}=0", 45).set_y(0.35)
        nonzero = self.zh("存在非 0 解，才有特征向量", 28, MUTED).set_y(-1.1)
        expanded = self.math(r"(5-\lambda)^2-1=(\lambda-4)(\lambda-6)=0", 46).set_y(0.25)
        results = VGroup(self.math(r"\lambda_1=4", 53, BLUE_VECTOR), self.math(r"\lambda_2=6", 53, GREEN_VECTOR))
        results.arrange(RIGHT, buff=2.1).set_y(-1.55)
        self.cue(16)
        self.play(FadeIn(heading), Write(equation), run_time=1.8)
        self.finish_cue()
        self.cue(17)
        self.play(Write(determinant), FadeIn(nonzero), run_time=1.7)
        self.finish_cue()
        self.cue(18)
        self.play(ReplacementTransform(determinant, expanded), FadeOut(nonzero), run_time=1.5)
        self.play(Write(results), run_time=1.2)
        self.finish_cue()
        self.clear_stage()

    def find_eigenvectors(self):
        heading = self.heading("07", "代回方程，找到对应的特征向量")
        cards = []
        for center, value, color, reduced, relation, vector in (
            (-3.25, 4, BLUE_VECTOR, r"\begin{bmatrix}1&-1\\-1&1\end{bmatrix}", r"x-y=0\quad\Rightarrow\quad x=y", (1, 1)),
            (3.25, 6, GREEN_VECTOR, r"\begin{bmatrix}-1&-1\\-1&-1\end{bmatrix}", r"x+y=0\quad\Rightarrow\quad x=-y", (-1, 1)),
        ):
            background = RoundedRectangle(width=5.9, height=4.55, corner_radius=0.16,
                                          stroke_color=color, stroke_opacity=0.4, stroke_width=1.5,
                                          fill_color=PANEL, fill_opacity=0.75).move_to([center, -0.05, 0])
            title = self.math(rf"\lambda={value}", 46, color).move_to([center, 1.65, 0])
            system = self.math(reduced + column("x", "y") + "=" + column(0, 0), 34, max_width=5.2).move_to([center, 0.38, 0])
            condition = self.math(relation, 33, color, 5.2).move_to([center, -0.65, 0])
            result = self.math(rf"\mathbf v_{1 if value == 4 else 2}=" + column(*vector), 42, color).move_to([center, -1.55, 0])
            cards.append(VGroup(background, title, system, condition, result))
        self.cue(19)
        self.play(FadeIn(heading), FadeIn(cards[0][0]), Write(cards[0][1:]), run_time=2.4)
        self.finish_cue()
        self.cue(20)
        self.play(FadeIn(cards[1][0]), Write(cards[1][1:]), run_time=2.4)
        self.finish_cue()
        self.clear_stage()

    def stretch_direction(self, index):
        first = index == 1
        value, color = (4, BLUE_VECTOR) if first else (6, GREEN_VECTOR)
        start = np.array([1, 1]) if first else np.array([-1, 1])
        end = MATRIX_B @ start
        if first:
            plane, labels = self.graph(B_X_RANGE, B_Y_RANGE, B_UNIT)
            matrix = self.right_at(self.math("B=" + B_TEX, 40, ACCENT), 2.0)
            stage = self.b_stage = dict(plane=plane, labels=labels, matrix=matrix, results=[])
        else:
            stage = self.b_stage
            plane, labels, matrix = (stage[key] for key in ("plane", "labels", "matrix"))
        line_ends = ((-4, -4), (6.8, 6.8)) if first else ((-6.8, 6.8), (4, -4))
        direction_line = DashedLine(*(plane.c2p(*p) for p in line_ends), color=color,
                                    stroke_width=2.0, dash_length=0.09).set_opacity(0.5)
        moving = self.vector(plane, start, color, 6)
        original = self.vector(plane, start, GREY_B, 2.5, 6)
        original_dot = Dot(plane.c2p(*start), color=WHITE, radius=0.04).set_z_index(7)
        start_tag = self.point_label(plane, start, f"({start[0]},{start[1]})", MUTED,
                                     RIGHT if first else LEFT)
        end_tag = self.point_label(plane, end, f"({end[0]},{end[1]})", color, UP)
        input_label = self.right_at(self.math(rf"\mathbf v_{index}=" + column(*start), 40, color), 0.55)
        product = self.right_at(self.math(rf"B\mathbf v_{index}={value}\mathbf v_{index}", 43, color), 0.75)
        multiple = self.right_at(self.math(column(*end) + "=" + str(value) + column(*start), 35, color), -0.45)
        direction = self.right_at(self.math("y=x" if first else "y=-x", 36, color), -1.55)
        badge = self.right_at(self.zh(f"长度 ×{value}，方向不变", 26, color), -2.25)
        step = plane.c2p(*start) - plane.c2p(0, 0)
        normal = np.array([-step[1], step[0], 0]) / np.linalg.norm(step)
        marks = VGroup(*[Line(plane.c2p(*(n * start)) - 0.06 * normal,
                             plane.c2p(*(n * start)) + 0.06 * normal,
                             color=color, stroke_width=2).set_z_index(7) for n in range(1, value + 1)])
        self.cue(21 if first else 23, "先看 (1,1)。" if first else "再看 (-1,1)。")
        if first:
            heading = self.heading("08", "特征方向 1：沿原方向扩大 4 倍")
            self.play(FadeIn(heading), Create(plane), FadeIn(labels), Write(matrix),
                      Create(direction_line), GrowArrow(moving), FadeIn(start_tag),
                      Write(input_label), run_time=1.1)
        else:
            heading, heading_change = self.change_heading(stage["heading"], "09", "特征方向 2：沿原方向扩大 6 倍")
            previous = stage["results"][0]
            self.play(heading_change, FadeOut(stage["right_body"]),
                      previous["arrow"].animate.set_opacity(0.38),
                      previous["end_tag"].animate.set_opacity(0.4),
                      previous["line"].animate.set_opacity(0.25),
                      previous["marks"].animate.set_opacity(0.3),
                      Create(direction_line), GrowArrow(moving), FadeIn(start_tag),
                      Write(input_label), run_time=1.1)
        self.add(original, original_dot)
        unit = float(np.linalg.norm(plane.c2p(1, 0) - plane.c2p(0, 0)))
        self.observe("eigenvector_motion_start", index=index, unit=unit,
                     origin=plane.c2p(0, 0).tolist(), start=start.tolist(), end=end.tolist())
        self.say(f"B 把它变成 ({end[0]},{end[1]})，")
        self.play(Transform(moving, self.vector(plane, end, color, 6)), run_time=2.2)
        self.observe("eigenvector_motion_end", index=index)
        self.play(FadeIn(end_tag), FadeIn(marks), run_time=0.3)
        self.say(f"也就是原向量的 {value} 倍。")
        self.play(ReplacementTransform(input_label, product), Write(multiple), run_time=0.8)
        self.finish_cue()
        self.cue(22 if first else 24)
        self.play(FadeIn(direction), FadeIn(badge),
                  Indicate(direction_line, color=color, scale_factor=1), run_time=0.9)
        self.finish_cue()
        stage.update(heading=heading, right_body=VGroup(product, multiple, direction, badge))
        stage["results"].append(dict(arrow=moving, line=direction_line, end_tag=end_tag, marks=marks))

    def both_directions(self):
        stage = self.b_stage
        plane = stage["plane"]
        eq1 = self.right_at(self.math(r"B\mathbf v_1=4\mathbf v_1", 40, BLUE_VECTOR), 0.85)
        eq2 = self.right_at(self.math(r"B\mathbf v_2=6\mathbf v_2", 40, GREEN_VECTOR), -0.3)
        rule = self.right_at(self.math(r"B(c\mathbf v_i)=\lambda_i(c\mathbf v_i),\quad c\ne0", 31, ACCENT), -1.5)
        hint = self.right_at(self.zh("这两条直线上的\n任意非 0 向量，都适用", 24, MUTED), -2.35)
        self.cue(25)
        heading, heading_change = self.change_heading(stage["heading"], "10", "B在两个特征方向上的作用")
        previous = stage["results"][0]
        self.play(heading_change, FadeOut(stage["right_body"]),
                  previous["arrow"].animate.set_opacity(1),
                  previous["end_tag"].animate.set_opacity(1),
                  previous["line"].animate.set_opacity(0.5),
                  previous["marks"].animate.set_opacity(1),
                  Write(eq1), Write(eq2), run_time=1.1)
        self.finish_cue()
        self.cue(26)
        negative1 = self.vector(plane, (-0.6, -0.6), BLUE_VECTOR, 4)
        negative2 = self.vector(plane, (0.6, -0.6), GREEN_VECTOR, 4)
        self.play(GrowArrow(negative1), GrowArrow(negative2), Write(rule), FadeIn(hint), run_time=1.1)
        self.play(Transform(negative1, self.vector(plane, (-2.4, -2.4), BLUE_VECTOR, 4)),
                  Transform(negative2, self.vector(plane, (3.6, -3.6), GREEN_VECTOR, 4)), run_time=1.9)
        self.finish_cue()
        self.clear_stage()

    def summary(self):
        heading = self.heading("11", "记住：找方向，再看倍数")
        cards = VGroup()
        for center, letter, tex, color, rows in (
            (-3.25, "A", A_TEX, BLUE_VECTOR, ((2, (1, 0)), (3, (0, 1)))),
            (3.25, "B", B_TEX, GREEN_VECTOR, ((4, (1, 1)), (6, (-1, 1)))),
        ):
            box = RoundedRectangle(width=5.9, height=3.7, corner_radius=0.16,
                                   stroke_color=color, stroke_opacity=0.4, stroke_width=1.5,
                                   fill_color=PANEL, fill_opacity=0.75).move_to([center, 0.35, 0])
            matrix = self.math(letter + "=" + tex, 39, color).move_to([center, 1.4, 0])
            pairs = VGroup(*[self.math(rf"\lambda={value}:\quad\mathbf v=" + column(*vector), 34, color)
                             for value, vector in rows]).arrange(DOWN, buff=0.35).move_to([center, -0.35, 0])
            cards.add(VGroup(box, matrix, pairs))
        equation = self.math(r"\boxed{A\mathbf v=\lambda\mathbf v,\qquad\mathbf v\ne\mathbf0}", 47, ACCENT).set_y(-2.2)
        self.cue(27)
        self.play(FadeIn(heading), FadeIn(cards[0]), FadeIn(cards[1]), run_time=1.8)
        self.finish_cue()
        self.cue(28)
        self.play(Write(equation), run_time=1.6)
        self.finish_cue()

    def export_timeline(self):
        output = Path(config.media_dir).resolve() / "eigenvalues"
        output.mkdir(parents=True, exist_ok=True)
        duration = float(self.renderer.time)
        chapters = [dict(chapter, end=(self.chapters[i + 1]["start"] if i + 1 < len(self.chapters) else duration))
                    for i, chapter in enumerate(self.chapters)]
        timeline = {"scene": type(self).__name__, "duration": duration, "chapters": chapters,
                    "cues": self.cues, "subtitles": self.subtitle_events, "actions": self.observations}
        (output / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

        def timestamp(seconds):
            milliseconds = round(seconds * 1000)
            hours, milliseconds = divmod(milliseconds, 3_600_000)
            minutes, milliseconds = divmod(milliseconds, 60_000)
            whole_seconds, milliseconds = divmod(milliseconds, 1000)
            return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"

        subtitles = [f"{i}\n{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{cue['text']}\n"
                     for i, cue in enumerate(self.subtitle_events, 1)]
        (output / f"{type(self).__name__}.srt").write_text("\n".join(subtitles), encoding="utf-8-sig")


def export_narration():
    lines = ["# 特征值与特征向量：旁白文稿", "", f"与源文件 NARRATION 一一对应；可选配音文件放在 `配音/001.mp3` 至 `配音/{len(NARRATION):03d}.mp3`。", ""]
    for number, (text, duration) in enumerate(NARRATION, 1):
        lines.extend([f"{number:03d}（默认 {duration:g} 秒）", "", text, ""])
    destination = ROOT / "旁白文稿.md"
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    export_narration()
