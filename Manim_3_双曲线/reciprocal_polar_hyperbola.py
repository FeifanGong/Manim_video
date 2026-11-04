from manim import *
import numpy as np
from pathlib import Path


BG = "#03050b"
INK = "#f8fafc"
SOFT = "#cbd5e1"
MUTED = "#8b9bb0"
BLUE = "#48a8ff"
CYAN = "#25f2d0"
AMBER = "#ffc857"
RED = "#ff4d6d"
VIOLET = "#a78bfa"
PANEL = "#07111f"
GRID = "#253044"
CN_FONT = "Microsoft YaHei"

TEX_TEMPLATE = TexTemplate(tex_compiler="xelatex", output_format=".xdv")
TEX_TEMPLATE.add_to_preamble(r"\usepackage{amsmath,amssymb}")

USE_MANIM_AUDIO = False
VOICE_DIR = Path(__file__).resolve().parent / "\u914d\u97f3"
VOICE_DURATIONS = {
    1: 1.152,
    2: 5.016,
    3: 8.064,
    4: 3.864,
    5: 7.800,
    6: 6.192,
    7: 4.224,
    8: 3.144,
    9: 8.232,
    10: 4.728,
    11: 1.800,
    12: 6.864,
    13: 5.232,
    14: 3.312,
    15: 5.256,
}


def voice_path(number):
    matches = sorted(VOICE_DIR.glob(f"{number:04d}_*.mp3"))
    return matches[0] if matches else None


def cn(text, font_size=32, color=INK, weight=NORMAL, **kwargs):
    return Text(
        text,
        font=CN_FONT,
        font_size=font_size,
        color=color,
        weight=weight,
        **kwargs,
    )


def mt(tex, font_size=42, color=INK, tex_to_color_map=None):
    return MathTex(
        tex,
        tex_template=TEX_TEMPLATE,
        font_size=font_size,
        color=color,
        tex_to_color_map=tex_to_color_map or {},
    )


def stage_backdrop():
    base = Rectangle(
        width=config.frame_width,
        height=config.frame_height,
        fill_color=BG,
        fill_opacity=1,
        stroke_width=0,
    )

    folds = VGroup()
    strip_count = 34
    strip_w = config.frame_width / strip_count
    for i in range(strip_count):
        alpha = 0.18 + 0.17 * (0.5 + 0.5 * np.sin(i * 1.7))
        color = "#0a1020" if i % 2 else "#050814"
        strip = Rectangle(
            width=strip_w + 0.02,
            height=config.frame_height,
            stroke_width=0,
            fill_color=color,
            fill_opacity=alpha,
        )
        strip.move_to(LEFT * config.frame_width / 2 + RIGHT * strip_w * (i + 0.5))
        folds.add(strip)

    top_band = Rectangle(
        width=config.frame_width,
        height=0.58,
        stroke_width=0,
        fill_color="#050816",
        fill_opacity=0.96,
    ).to_edge(UP, buff=0)
    top_line = Line(
        LEFT * config.frame_width / 2 + DOWN * 0.32,
        RIGHT * config.frame_width / 2 + DOWN * 0.32,
        color="#17223a",
        stroke_width=2,
    ).to_edge(UP, buff=0.58)

    side_shadow = VGroup(
        Rectangle(
            width=1.1,
            height=config.frame_height,
            stroke_width=0,
            fill_color="#000000",
            fill_opacity=0.45,
        ).to_edge(LEFT, buff=0),
        Rectangle(
            width=1.1,
            height=config.frame_height,
            stroke_width=0,
            fill_color="#000000",
            fill_opacity=0.45,
        ).to_edge(RIGHT, buff=0),
    )

    glow = Ellipse(
        width=9.5,
        height=4.2,
        stroke_width=0,
        fill_color="#0b1e37",
        fill_opacity=0.18,
    ).shift(DOWN * 0.2)

    backdrop = VGroup(base, glow, folds, top_band, top_line, side_shadow)
    backdrop.set_z_index(-20)
    return backdrop


def subtitle(text):
    band = Rectangle(
        width=config.frame_width,
        height=0.64,
        stroke_width=0,
        fill_color="#020617",
        fill_opacity=0.74,
    ).to_edge(DOWN, buff=0)
    line = cn(text, font_size=25, color="#e5edf7").move_to(band)
    return VGroup(band, line)


def part_label(number, title):
    dot = Circle(radius=0.16, stroke_width=0, fill_color=BLUE, fill_opacity=1)
    num = cn(str(number), font_size=17, color=BG, weight=BOLD).move_to(dot)
    text = cn(title, font_size=24, color=SOFT)
    label = VGroup(dot, num, text).arrange(RIGHT, buff=0.12)
    label.to_edge(UP, buff=0.16).to_edge(LEFT, buff=0.45)
    return label


def formula_panel(items, buff=0.26, pad=0.28):
    stack = VGroup(*items).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    bg = RoundedRectangle(
        width=stack.width + pad * 2,
        height=stack.height + pad * 2,
        corner_radius=0.12,
        stroke_color="#1e3a5f",
        stroke_width=1.4,
        fill_color=PANEL,
        fill_opacity=0.82,
    )
    bg.move_to(stack)
    return VGroup(bg, stack)


def make_axes(x_length=6.4, y_length=4.2):
    axes = NumberPlane(
        x_range=[-4, 4, 1],
        y_range=[-3, 3, 1],
        x_length=x_length,
        y_length=y_length,
        background_line_style={
            "stroke_color": GRID,
            "stroke_width": 1,
            "stroke_opacity": 0.28,
        },
        axis_config={
            "color": "#718096",
            "stroke_width": 2,
            "include_ticks": False,
            "include_numbers": False,
        },
        faded_line_ratio=2,
    )
    labels = VGroup(
        mt("x", font_size=25, color=MUTED).next_to(axes.x_axis.get_end(), DOWN, buff=0.08),
        mt("y", font_size=25, color=MUTED).next_to(axes.y_axis.get_end(), LEFT, buff=0.08),
    )
    return axes, labels


def reciprocal_curve(axes, color=BLUE, stroke_width=4.5, x_min=0.34, x_max=4):
    positive = axes.plot(
        lambda x: 1 / x,
        x_range=[x_min, x_max],
        color=color,
        stroke_width=stroke_width,
        use_smoothing=False,
    )
    negative = axes.plot(
        lambda x: 1 / x,
        x_range=[-x_max, -x_min],
        color=color,
        stroke_width=stroke_width,
        use_smoothing=False,
    )
    return VGroup(positive, negative)


def standard_hyperbola(axes, color=BLUE, stroke_width=4.5):
    a = np.sqrt(2)
    t_max = np.arccosh(4 / a)

    right = axes.plot_parametric_curve(
        lambda t: np.array([a * np.cosh(t), a * np.sinh(t), 0]),
        t_range=[-t_max, t_max],
        color=color,
        stroke_width=stroke_width,
    )
    left = axes.plot_parametric_curve(
        lambda t: np.array([-a * np.cosh(t), a * np.sinh(t), 0]),
        t_range=[-t_max, t_max],
        color=color,
        stroke_width=stroke_width,
    )
    return VGroup(right, left)


def xy_asymptotes(axes):
    return VGroup(
        Line(axes.c2p(-4, 0), axes.c2p(4, 0), color=AMBER, stroke_width=3.2),
        Line(axes.c2p(0, -3), axes.c2p(0, 3), color=AMBER, stroke_width=3.2),
    )


def standard_asymptotes(axes):
    return VGroup(
        DashedLine(axes.c2p(-3, -3), axes.c2p(3, 3), color=AMBER, stroke_width=3.5, dash_length=0.18),
        DashedLine(axes.c2p(-3, 3), axes.c2p(3, -3), color=AMBER, stroke_width=3.5, dash_length=0.18),
    )


def glow_copy(mobject, color=BLUE, width=11, opacity=0.18):
    glow = mobject.copy()
    glow.set_stroke(color=color, width=width, opacity=opacity)
    glow.set_z_index(mobject.z_index - 1)
    return glow


class ReciprocalPolarHyperbola(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.backdrop = stage_backdrop()
        self.add(self.backdrop)

        self.intro()
        self.derive_polar()
        self.rotate_to_standard()
        self.finish()

    def clear_content(self):
        foreground = [mob for mob in self.mobjects if mob is not self.backdrop]
        if foreground:
            self.play(FadeOut(*foreground), run_time=0.65)

    def voice(self, number):
        path = voice_path(number)
        if USE_MANIM_AUDIO and path is not None:
            self.add_sound(str(path))
        return VOICE_DURATIONS.get(number, 0)

    def wait_voice(self, number, elapsed=0, extra=0):
        remaining = VOICE_DURATIONS.get(number, 0) + extra - elapsed
        if remaining > 0.01:
            self.wait(remaining)

    def intro(self):
        label = part_label(1, "引入")
        headline = VGroup(
            cn("你知道吗，反比例函数", font_size=33, weight=BOLD),
            mt(r"y=\frac{1}{x}", font_size=48, color=BLUE),
            cn("本质上是一条", font_size=33),
            cn("等轴双曲线", font_size=38, color=AMBER, weight=BOLD),
        ).arrange(RIGHT, buff=0.18)
        headline.to_edge(UP, buff=0.72)

        axes, labels = make_axes(x_length=7.4, y_length=4.7)
        graph = VGroup(axes, labels).shift(DOWN * 0.5)
        asym = xy_asymptotes(axes)
        curve = reciprocal_curve(axes)
        curve_glow = glow_copy(curve)

        origin = axes.c2p(0, 0)
        right_angle = RightAngle(
            Line(origin, axes.c2p(1, 0)),
            Line(origin, axes.c2p(0, 1)),
            length=0.28,
            quadrant=(1, 1),
            color=RED,
            stroke_width=3,
        )
        note = cn("两条渐近线互相垂直", font_size=23, color=RED)
        note.move_to(axes.c2p(-2.15, 1.15))
        sub = subtitle("先看图像：它像是斜着摆放，但双曲线的骨架已经出现了。")

        self.voice(1)
        self.play(FadeIn(label), run_time=0.65)
        self.wait_voice(1, elapsed=0.65, extra=0.2)

        self.voice(2)
        self.play(FadeIn(headline, shift=DOWN * 0.15), run_time=0.9)
        self.wait_voice(2, elapsed=0.9, extra=0.6)

        self.voice(3)
        self.play(Create(axes), FadeIn(labels), run_time=0.9)
        self.play(Create(asym), run_time=0.65)
        self.play(Create(curve_glow), Create(curve), run_time=1.25)
        self.play(Create(right_angle), FadeIn(note), FadeIn(sub), run_time=0.75)
        self.wait_voice(3, elapsed=3.55, extra=0.6)
        self.clear_content()

    def derive_polar(self):
        label = part_label(2, "导出极坐标形式")
        title = cn("从一个具体函数开始", font_size=36, weight=BOLD).to_edge(UP, buff=0.78)

        axes, labels = make_axes(x_length=5.6, y_length=3.8)
        graph = VGroup(axes, labels).to_edge(LEFT, buff=0.55).shift(DOWN * 0.08)
        curve = reciprocal_curve(axes, stroke_width=4)
        curve_glow = glow_copy(curve, width=9, opacity=0.16)

        x0 = 2.0
        y0 = 1 / x0
        point = axes.c2p(x0, y0)
        origin = axes.c2p(0, 0)
        dot = Dot(point, radius=0.07, color=RED)
        radius = Line(origin, point, color=RED, stroke_width=3.5)
        x_drop = DashedLine(point, axes.c2p(x0, 0), color=CYAN, stroke_width=2.5)
        y_drop = DashedLine(point, axes.c2p(0, y0), color=CYAN, stroke_width=2.5)
        angle = np.arctan2(y0, x0)
        arc = Arc(radius=0.58, start_angle=0, angle=angle, color=VIOLET, stroke_width=3)
        arc.move_arc_center_to(origin)
        p_label = mt(r"P(x,y)", font_size=27, color=RED).next_to(dot, UR, buff=0.12)
        r_label = mt(r"r", font_size=29, color=RED).next_to(radius, UP, buff=0.08)
        theta_label = mt(r"\theta", font_size=28, color=VIOLET).move_to(axes.c2p(0.86, 0.18))

        top_formula = VGroup(
            mt(r"y=\frac{1}{x}", font_size=43, color=BLUE),
            mt(r"\Longrightarrow", font_size=36, color=MUTED),
            mt(r"xy=1", font_size=43, color=BLUE),
        ).arrange(RIGHT, buff=0.18)

        steps = [
            mt(r"x=r\cos\theta,\qquad y=r\sin\theta", font_size=34),
            mt(r"(r\cos\theta)(r\sin\theta)=1", font_size=34),
            mt(r"r^2\sin\theta\cos\theta=1", font_size=34),
            mt(r"\boxed{r^2\sin 2\theta=2}", font_size=40, color=BLUE),
        ]
        panel = formula_panel([top_formula, *steps], buff=0.24, pad=0.32)
        panel.to_edge(RIGHT, buff=0.54).shift(DOWN * 0.08)
        sub = subtitle("极坐标只是在换一种记法：同一个点，用距离 r 和角度 θ 来描述。")

        self.voice(4)
        self.play(FadeIn(label), FadeIn(title, shift=DOWN * 0.12), run_time=0.8)
        self.play(Create(axes), FadeIn(labels), Create(curve_glow), Create(curve), run_time=1.0)
        self.play(FadeIn(panel[0]), Write(top_formula), run_time=0.9)
        self.wait_voice(4, elapsed=2.7, extra=0.3)

        self.voice(5)
        self.play(
            Create(radius),
            FadeIn(dot),
            Create(x_drop),
            Create(y_drop),
            Create(arc),
            FadeIn(p_label),
            FadeIn(r_label),
            FadeIn(theta_label),
            FadeIn(sub),
            run_time=1.1,
        )
        self.play(Write(steps[0]), run_time=0.72)
        self.wait_voice(5, elapsed=1.82, extra=1.0)

        self.voice(6)
        formula_elapsed = 0
        for step in steps[1:]:
            self.play(Write(step), run_time=0.72)
            self.wait(0.32)
            formula_elapsed += 1.04
        self.play(Indicate(steps[-1], scale_factor=1.04, color=BLUE), run_time=0.65)
        formula_elapsed += 0.65
        self.wait_voice(6, elapsed=formula_elapsed, extra=1.6)
        self.clear_content()

    def rotate_to_standard(self):
        label = part_label(3, "顺时针旋转 45°")
        title = cn("把斜着的曲线放正", font_size=36, weight=BOLD).to_edge(UP, buff=0.78)

        axes, labels = make_axes(x_length=6.4, y_length=4.8)
        graph = VGroup(axes, labels).shift(LEFT * 2.55).shift(DOWN * 0.04)
        curve = reciprocal_curve(axes, stroke_width=4.5, x_min=1 / 3.6, x_max=3.6)
        curve_glow = glow_copy(curve, width=10, opacity=0.16)
        asym = xy_asymptotes(axes)
        rotating = VGroup(curve_glow, curve, asym)

        before = mt(r"xy=1", font_size=35, color=BLUE).move_to(RIGHT * 2.35 + UP * 1.62)
        arrow = CurvedArrow(
            axes.c2p(2.25, 1.55),
            axes.c2p(2.85, -0.45),
            angle=-TAU / 5.5,
            color=RED,
            stroke_width=4,
        )
        arrow_text = cn("顺时针 45°", font_size=24, color=RED).next_to(arrow, RIGHT, buff=0.08)

        angle_explain = VGroup(
            cn("顺时针转：新角度比旧角度少 45°", font_size=22, color=SOFT),
            mt(r"\varphi=\theta-\frac{\pi}{4}\quad\Longleftrightarrow\quad\theta=\varphi+\frac{\pi}{4}", font_size=30, color=VIOLET),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        steps = [
            mt(r"r^2\sin 2\theta=2", font_size=34),
            angle_explain,
            mt(r"r^2\sin\!\left(2\varphi+\frac{\pi}{2}\right)=2", font_size=32),
            mt(r"\boxed{r^2\cos 2\varphi=2}", font_size=39, color=BLUE),
        ]
        panel = formula_panel(steps, buff=0.24, pad=0.3)
        panel.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.02)
        sub = subtitle("顺时针旋转 45° 后，同一个点的新角度 φ 比原来的 θ 少了 π/4。")
        sub2 = subtitle("所以代回原方程时，要写成 θ = φ + π/4；这里的“加”是在找回旧角度。")

        origin = axes.c2p(0, 0)
        self.voice(7)
        self.play(FadeIn(label), FadeIn(title, shift=DOWN * 0.12), run_time=0.8)
        self.play(Create(axes), FadeIn(labels), Create(asym), Create(curve_glow), Create(curve), FadeIn(before), run_time=1.15)
        self.play(FadeIn(arrow), FadeIn(arrow_text), FadeIn(sub), run_time=0.65)
        self.play(Rotate(rotating, angle=-PI / 4, about_point=origin), run_time=1.9, rate_func=smooth)
        self.wait_voice(7, elapsed=4.5, extra=0.6)

        self.voice(8)
        self.play(Transform(sub, sub2), run_time=0.65)
        standard_label = mt(r"X^2-Y^2=2", font_size=35, color=BLUE).move_to(before)
        self.play(FadeOut(arrow), FadeOut(arrow_text), Transform(before, standard_label), run_time=0.65)
        self.wait_voice(8, elapsed=1.3, extra=0.4)

        self.voice(9)
        self.play(FadeOut(before), FadeIn(panel[0]), run_time=0.35)
        self.play(Write(steps[0]), run_time=0.68)
        self.wait(0.25)
        self.play(Write(steps[1]), run_time=0.68)
        self.play(Indicate(steps[1], scale_factor=1.03, color=VIOLET), run_time=0.65)
        self.wait_voice(9, elapsed=2.56, extra=1.3)

        self.voice(10)
        formula_elapsed = 0
        for step in steps[2:]:
            self.play(Write(step), run_time=0.68)
            self.wait(0.32)
            formula_elapsed += 1.0
        self.play(Indicate(steps[-1], scale_factor=1.04, color=BLUE), run_time=0.65)
        formula_elapsed += 0.65
        self.wait_voice(10, elapsed=formula_elapsed, extra=1.5)
        self.clear_content()

    def finish(self):
        label = part_label(4, "得到标准双曲线")
        title = cn("标准形式出现了", font_size=36, weight=BOLD).to_edge(UP, buff=0.78)

        axes, labels = make_axes(x_length=6.15, y_length=4.61)
        graph = VGroup(axes, labels).to_edge(LEFT, buff=0.58).shift(DOWN * 0.18)
        curve = standard_hyperbola(axes, stroke_width=4.5)
        curve_glow = glow_copy(curve, width=10, opacity=0.16)
        asym = standard_asymptotes(axes)

        steps = [
            mt(r"r^2\cos 2\varphi=2", font_size=32),
            mt(r"r^2(\cos^2\varphi-\sin^2\varphi)=2", font_size=30),
            mt(r"X=r\cos\varphi,\quad Y=r\sin\varphi", font_size=30, color=CYAN),
            mt(r"\boxed{X^2-Y^2=2}", font_size=39, color=BLUE),
            mt(r"\frac{X^2}{2}-\frac{Y^2}{2}=1", font_size=39, color=BLUE),
            mt(r"\therefore\ a^2=b^2=2", font_size=30, color=RED),
        ]
        panel = formula_panel(steps, buff=0.14, pad=0.24)
        panel.to_edge(RIGHT, buff=0.48).shift(UP * 0.48)

        origin = axes.c2p(0, 0)
        a = np.sqrt(2)
        real_axis = Line(origin, axes.c2p(a, 0), color=RED, stroke_width=5)
        imag_axis = Line(origin, axes.c2p(0, a), color=RED, stroke_width=5)
        a_label = mt(r"\sqrt{2}", font_size=27, color=RED).next_to(real_axis, DOWN, buff=0.08)
        b_label = mt(r"\sqrt{2}", font_size=27, color=RED).next_to(imag_axis, LEFT, buff=0.08)
        sub = subtitle("于是，反比例函数就是一条等轴双曲线，只是原来斜放在坐标轴之间。")

        self.voice(11)
        self.play(FadeIn(label), FadeIn(title, shift=DOWN * 0.12), run_time=0.8)
        self.play(Create(axes), FadeIn(labels), Create(asym), run_time=0.85)
        self.play(Create(curve_glow), Create(curve), run_time=1.15)
        self.wait_voice(11, elapsed=2.8, extra=0.2)

        self.play(FadeIn(panel[0]), run_time=0.35)
        for step in steps[:2]:
            self.play(Write(step), run_time=0.62)
            self.wait(0.25)

        self.voice(12)
        self.play(Write(steps[2]), run_time=0.62)
        self.play(Indicate(steps[2], scale_factor=1.03, color=CYAN), run_time=0.55)
        self.wait_voice(12, elapsed=1.17, extra=0.1)

        self.voice(13)
        standard_elapsed = 0
        for step in steps[3:5]:
            self.play(Write(step), run_time=0.62)
            self.wait(0.3)
            standard_elapsed += 0.92
        self.play(Indicate(steps[4], scale_factor=1.03, color=BLUE), run_time=0.65)
        standard_elapsed += 0.65
        self.wait_voice(13, elapsed=standard_elapsed, extra=0.2)

        self.voice(14)
        self.play(Write(steps[5]), run_time=0.62)
        self.play(Create(real_axis), Create(imag_axis), FadeIn(a_label), FadeIn(b_label), run_time=0.75)
        self.play(Indicate(steps[5], scale_factor=1.03, color=RED), run_time=0.55)
        self.wait_voice(14, elapsed=1.92, extra=0.6)

        self.voice(15)
        self.play(FadeIn(sub), run_time=0.75)
        self.wait_voice(15, elapsed=0.75, extra=0.9)
