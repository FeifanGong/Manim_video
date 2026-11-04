from manim import *
import numpy as np
from pathlib import Path


# Render example:
# manim -pqh Affine_Trans_manim.py AffineTransformEllipse
#
# The scene uses Chinese Text objects and ASCII-only MathTex formulas. If Chinese
# text does not render on your machine, replace CJK_FONT with another installed
# Chinese font, such as "SimHei" or "Microsoft JhengHei".
CJK_FONT = "Microsoft YaHei"

VOICE_LINES = [
    "今天我们换一个更直观的角度来理解椭圆。",
    "很多同学第一次看到椭圆公式时，会觉得它只是一个需要记住的方程。",
    "但其实，椭圆可以看成是圆被拉伸之后得到的图形。",
    "先从最熟悉的单位圆开始。",
    "单位圆的方程是，x 平方加 y 平方等于一。",
    "现在我们对圆上的每一个点都做同样的操作：横坐标乘以 a，纵坐标乘以 b。",
    "也就是说，原来的点小 x，小 y，会变成新的点大 X，大 Y，其中大 X 等于 a 乘小 x，大 Y 等于 b 乘小 y。",
    "如果 a 比较大，图形就会在横向被拉宽；如果 b 比较大，图形就会在纵向被拉高。",
    "横向和纵向拉伸的倍数不一样时，原来的圆就变成了椭圆。",
    "圆上的点 P，也会被送到椭圆上的点 P 撇。",
    "可以把这个过程想象成：我们拿着一个圆形橡皮膜，沿着水平方向和竖直方向分别拉伸。",
    "接下来看看方程为什么也会变成椭圆方程。",
    "因为大 X 等于 a 乘小 x，所以小 x 等于大 X 除以 a。",
    "同理，小 y 等于大 Y 除以 b。",
    "把这两个式子代回单位圆方程，原来的 x 平方加 y 平方等于一，就变成了，大 X 除以 a 的平方，加上大 Y 除以 b 的平方，等于一。",
    "整理一下，就得到大 X 平方除以 a 平方，加大 Y 平方除以 b 平方，等于一。",
    "这就是椭圆的标准方程。",
    "更重要的是，这个拉伸过程还会告诉我们，斜率会怎样变化。",
    "斜率本质上就是纵向变化量除以横向变化量。",
    "拉伸以后，横向变化量变成原来的 a 倍，纵向变化量变成原来的 b 倍。",
    "所以新的斜率 k 撇，等于 b 除以 a，再乘原来的斜率 k。",
    "也就是说，所有直线的斜率都会统一乘上 b 除以 a。",
    "有了这个斜率变化规律，我们就能把圆里的性质搬到椭圆上。",
    "在圆里，直径所对的圆周角是直角，所以从圆上一点连到直径两端，两条线互相垂直，它们的斜率乘积是负一。",
    "把圆拉伸成椭圆后，两条线的斜率都乘上 b 除以 a，因此斜率乘积就变成负的 b 平方除以 a 平方。",
    "中点弦结论也是类似的。",
    "圆里有垂径定理：圆心连到弦的中点，会垂直于这条弦。",
    "拉伸成椭圆后，垂直关系不一定还在，但斜率乘积仍然有固定规律。",
    "椭圆中一条弦的斜率，乘上中心到弦中点连线的斜率，结果仍然是负的 b 平方除以 a 平方。",
    "所以，理解椭圆时，不要只盯着公式。",
    "更好的图像是：椭圆就是被横向和纵向不同程度拉伸后的圆。",
    "圆里的直角、垂径定理和斜率关系，经过这个拉伸过程，就自然变成了椭圆里的相关结论。",
]

VOICE_DURATIONS = [
    3.384, 5.520, 4.200, 2.328, 3.912, 6.408, 10.656, 7.032,
    4.872, 3.528, 6.984, 3.432, 4.992, 3.024, 11.664, 6.792,
    2.016, 5.304, 3.864, 6.000, 4.704, 4.344, 4.800, 10.008,
    8.112, 2.112, 4.944, 6.144, 7.416, 3.336, 5.160, 7.032,
]


class AffineTransformEllipse(Scene):
    """A high-school friendly explanation of affine transforms and ellipses."""

    def construct(self):
        self.camera.background_color = "#10131A"
        self.voice_files = sorted(Path("配音").glob("*.mp3"))
        self.voice_index = 0
        self.current_subtitle = None
        self.intro()
        self.circle_to_ellipse()
        self.equation_derivation()
        self.slope_rule()
        self.slope_definition()
        self.midpoint_chord()
        self.summary()

    def zh(self, text, font_size=34, color=WHITE):
        return Text(text, font=CJK_FONT, font_size=font_size, color=color)

    def math(self, tex, font_size=42, color=WHITE):
        return MathTex(tex, font_size=font_size, color=color)

    def caption(self, text, font_size=28):
        # Legacy bottom captions are disabled; subtitles now come from the
        # voiceover text and are synchronized with the audio clips.
        return VGroup()

    def wrap_subtitle(self, text, max_chars=24):
        breaks = "，。；：、！？"
        lines = []
        rest = text
        while len(rest) > max_chars:
            split_at = -1
            for i in range(min(max_chars, len(rest)) - 1, max(10, max_chars - 10), -1):
                if rest[i] in breaks:
                    split_at = i + 1
                    break
            if split_at == -1:
                split_at = max_chars
            lines.append(rest[:split_at])
            rest = rest[split_at:]
        if rest:
            lines.append(rest)
        return "\n".join(lines)

    def make_subtitle(self, text):
        font_size = 27
        if len(text) > 42:
            font_size = 24
        if len(text) > 70:
            font_size = 22
        subtitle_text = self.zh(self.wrap_subtitle(text), font_size=font_size)
        subtitle_text.set_color(WHITE)
        subtitle_text.to_edge(DOWN, buff=0.22)
        if subtitle_text.width > config.frame_width - 0.8:
            subtitle_text.scale_to_fit_width(config.frame_width - 0.8)
            subtitle_text.to_edge(DOWN, buff=0.22)
        bg = BackgroundRectangle(subtitle_text, color=BLACK, fill_opacity=0.72, buff=0.16)
        return VGroup(bg, subtitle_text)

    def start_voice(self, line_index=None):
        if line_index is None:
            line_index = self.voice_index + 1
        idx = line_index - 1
        text = VOICE_LINES[idx]
        if self.current_subtitle is not None:
            self.remove(self.current_subtitle)
        self.current_subtitle = self.make_subtitle(text)
        self.add(self.current_subtitle)
        if idx < len(self.voice_files):
            self.add_sound(str(self.voice_files[idx]))
        self.voice_index = idx + 1
        self.voice_start_time = self.renderer.time
        self.voice_duration = VOICE_DURATIONS[idx]

    def finish_voice(self):
        elapsed = self.renderer.time - self.voice_start_time
        remaining = self.voice_duration - elapsed
        if remaining > 0:
            self.wait(remaining)

    def section_title(self, text):
        title = self.zh(text, font_size=42, color=YELLOW)
        title.to_edge(UP, buff=0.35)
        return title

    def clear_scene(self):
        self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=0.7)

    def make_axes(self):
        return Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.6, 1],
            x_length=8.0,
            y_length=4.4,
            axis_config={
                "include_ticks": False,
                "stroke_width": 2,
                "color": GREY_B,
            },
        )

    def ellipse_curve(self, axes, a=1.0, b=1.0, color=BLUE, width=5):
        return ParametricFunction(
            lambda t: axes.c2p(a * np.cos(t), b * np.sin(t)),
            t_range=[0, TAU],
            color=color,
            stroke_width=width,
        )

    def intro(self):
        title = self.zh("用仿射变换理解椭圆", font_size=52, color=YELLOW)
        subtitle = self.zh("一句话：把圆横向、纵向按不同倍数拉伸，就得到椭圆。", font_size=30)
        formula = self.math(r"(x,y)\longmapsto (X,Y)=(ax,by)", font_size=46, color=BLUE_B)
        group = VGroup(title, subtitle, formula).arrange(DOWN, buff=0.45)

        self.start_voice(1)
        self.play(FadeIn(title, shift=DOWN * 0.25))
        self.finish_voice()
        self.start_voice(2)
        self.play(Write(subtitle))
        self.finish_voice()
        self.start_voice(3)
        self.play(Write(formula))
        self.finish_voice()
        self.clear_scene()

    def circle_to_ellipse(self):
        title = self.section_title("第一步：先看图形怎么变")
        axes = self.make_axes().shift(DOWN * 0.25)

        circle = self.ellipse_curve(axes, 1, 1, BLUE)
        circle_label = self.math(r"x^2+y^2=1", font_size=36, color=BLUE).next_to(
            axes.c2p(-1.3, 1.05), LEFT, buff=0.1
        )

        caption1 = self.caption("先从最熟悉的单位圆开始。")
        self.start_voice(4)
        self.play(FadeIn(title), Create(axes), Create(circle), FadeIn(circle_label))
        self.finish_voice()
        self.start_voice(5)
        self.play(FadeIn(caption1))
        self.finish_voice()

        rule = self.math(r"X=ax,\qquad Y=by", font_size=44, color=YELLOW).next_to(
            title, DOWN, buff=0.25
        )
        caption2 = self.caption("规则很朴素：横坐标乘 a，纵坐标乘 b。")
        self.start_voice(6)
        self.play(ReplacementTransform(caption1, caption2), Write(rule))
        self.finish_voice()
        self.start_voice(7)
        self.finish_voice()

        ellipse = self.ellipse_curve(axes, 2.0, 0.85, RED)
        faded_circle = self.ellipse_curve(axes, 1, 1, BLUE, width=3).set_opacity(0.28)
        ellipse_label = self.math(
            r"\frac{X^2}{a^2}+\frac{Y^2}{b^2}=1",
            font_size=34,
            color=RED,
        ).move_to(axes.c2p(1.45, -1.2))

        caption3 = self.caption("横向拉开、纵向压一点，圆就变成了椭圆。")
        self.start_voice(8)
        self.play(Transform(circle, ellipse), ReplacementTransform(caption2, caption3))
        self.finish_voice()
        self.start_voice(9)
        self.play(FadeIn(faded_circle))
        self.finish_voice()

        theta = 52 * DEGREES
        p = axes.c2p(np.cos(theta), np.sin(theta))
        pp = axes.c2p(2.0 * np.cos(theta), 0.85 * np.sin(theta))
        dot_p = Dot(p, color=BLUE)
        dot_pp = Dot(pp, color=RED)
        arrow = Arrow(p, pp, buff=0.08, color=YELLOW)
        label_p = self.math(r"P(x,y)", font_size=28, color=BLUE).next_to(dot_p, UP + LEFT, buff=0.12)
        label_pp = self.math(r"P'(ax,by)", font_size=28, color=RED).move_to(axes.c2p(2.12, 0.95))
        leader_pp = DashedLine(
            dot_pp.get_center(),
            label_pp.get_left(),
            color=RED_B,
            stroke_width=2,
            dash_length=0.08,
        ).set_opacity(0.8)

        caption4 = self.caption("圆上的每个点 P，都会搬到椭圆上的点 P'。")
        self.start_voice(10)
        self.play(FadeIn(dot_p), FadeIn(label_p))
        self.play(
            GrowArrow(arrow),
            FadeIn(dot_pp),
            Create(leader_pp),
            FadeIn(label_pp),
            ReplacementTransform(caption3, caption4),
        )
        self.finish_voice()
        caption5 = self.caption("这些对应点形成的轨迹，就是椭圆方程。")
        self.start_voice(11)
        self.play(
            ReplacementTransform(circle_label, ellipse_label),
            ReplacementTransform(caption4, caption5),
        )
        self.finish_voice()
        self.clear_scene()

    def equation_derivation(self):
        title = self.section_title("第二步：方程为什么变成椭圆方程？")
        hint = self.zh("只做一件事：把圆方程里的 x 和 y 换掉。", font_size=30).next_to(
            title, DOWN, buff=0.25
        )

        e1 = self.math(r"x^2+y^2=1", font_size=46, color=BLUE)
        e2 = self.math(r"x=\frac{X}{a},\qquad y=\frac{Y}{b}", font_size=44, color=YELLOW)
        e3 = self.math(
            r"\left(\frac{X}{a}\right)^2+\left(\frac{Y}{b}\right)^2=1",
            font_size=44,
        )
        e4 = self.math(
            r"\frac{X^2}{a^2}+\frac{Y^2}{b^2}=1",
            font_size=50,
            color=RED,
        )
        equations = VGroup(e1, e2, e3, e4).arrange(DOWN, buff=0.45).shift(DOWN * 0.25)

        arrows = VGroup()
        for upper, lower in zip(equations[:-1], equations[1:]):
            arrows.add(Arrow(upper.get_bottom(), lower.get_top(), buff=0.08, color=GREY_B))

        cap = self.caption("所以，椭圆可以看作单位圆被拉伸后的结果。")
        self.start_voice(12)
        self.play(FadeIn(title), FadeIn(hint))
        self.play(Write(e1))
        self.finish_voice()
        self.start_voice(13)
        self.play(GrowArrow(arrows[0]), Write(e2))
        self.finish_voice()
        self.start_voice(14)
        self.finish_voice()
        self.start_voice(15)
        self.play(GrowArrow(arrows[1]), Write(e3))
        self.finish_voice()
        self.start_voice(16)
        self.play(GrowArrow(arrows[2]), Write(e4), FadeIn(cap))
        self.finish_voice()
        self.start_voice(17)
        self.play(Circumscribe(e4, color=YELLOW))
        self.finish_voice()
        self.clear_scene()

    def slope_rule(self):
        title = self.section_title("第三步：斜率会跟着怎么变？")
        cap1 = self.caption("斜率就是“纵向变化量 ÷ 横向变化量”。")

        left_base = LEFT * 4.2 + DOWN * 0.25
        dx = 1.75
        dy = 1.15
        before_end = left_base + RIGHT * dx + UP * dy
        before_line = Line(left_base, before_end, color=BLUE, stroke_width=6)
        before_dx = Arrow(left_base, left_base + RIGHT * dx, buff=0, color=BLUE_B)
        before_dy = Arrow(left_base + RIGHT * dx, before_end, buff=0, color=BLUE_B)
        before_label = self.zh("拉伸前", font_size=28, color=BLUE).next_to(before_line, UP, buff=0.3)
        dx_label = self.math(r"\Delta x", font_size=30, color=BLUE_B).next_to(before_dx, DOWN, buff=0.1)
        dy_label = self.math(r"\Delta y", font_size=30, color=BLUE_B).next_to(before_dy, RIGHT, buff=0.1)
        k_formula = self.math(r"k=\frac{\Delta y}{\Delta x}", font_size=40, color=BLUE).next_to(
            before_line, DOWN, buff=0.55
        )

        right_base = RIGHT * 0.9 + DOWN * 0.25
        after_dx = 2.8
        after_dy = 0.85
        after_end = right_base + RIGHT * after_dx + UP * after_dy
        after_line = Line(right_base, after_end, color=RED, stroke_width=6)
        after_x = Arrow(right_base, right_base + RIGHT * after_dx, buff=0, color=RED_B)
        after_y = Arrow(right_base + RIGHT * after_dx, after_end, buff=0, color=RED_B)
        after_label = self.zh("拉伸后", font_size=28, color=RED).next_to(after_line, UP, buff=0.3)
        ax_label = self.math(r"a\Delta x", font_size=30, color=RED_B).next_to(after_x, DOWN, buff=0.1)
        by_label = self.math(r"b\Delta y", font_size=30, color=RED_B).next_to(after_y, RIGHT, buff=0.1)
        kp_formula = self.math(
            r"k'=\frac{\Delta Y}{\Delta X}"
            r"=\frac{b\Delta y}{a\Delta x}"
            r"=\frac{b}{a}k",
            font_size=38,
            color=RED,
        ).next_to(after_line, DOWN, buff=0.55)

        arrow = Arrow(LEFT * 1.25 + UP * 0.2, RIGHT * 0.15 + UP * 0.2, color=YELLOW)
        rule = self.math(r"\boxed{k'=\frac{b}{a}k}", font_size=46, color=YELLOW)
        rule.to_edge(DOWN, buff=1.05)

        self.start_voice(18)
        self.play(FadeIn(title), FadeIn(cap1))
        self.finish_voice()
        self.start_voice(19)
        self.play(Create(before_line), GrowArrow(before_dx), GrowArrow(before_dy))
        self.play(FadeIn(before_label), Write(dx_label), Write(dy_label), Write(k_formula))
        self.finish_voice()
        cap2 = self.caption("横向变成 a 倍，纵向变成 b 倍，所以斜率多了一个 b/a。")
        self.start_voice(20)
        self.play(GrowArrow(arrow), ReplacementTransform(cap1, cap2))
        self.play(Create(after_line), GrowArrow(after_x), GrowArrow(after_y))
        self.finish_voice()
        self.start_voice(21)
        self.play(FadeIn(after_label), Write(ax_label), Write(by_label), Write(kp_formula))
        self.finish_voice()
        self.start_voice(22)
        self.play(Write(rule), Circumscribe(rule, color=YELLOW))
        self.finish_voice()
        self.clear_scene()

    def slope_definition(self):
        title = self.section_title("第四步：把圆里的直角搬到椭圆上")

        center = LEFT * 3.0 + DOWN * 0.2
        r = 1.35
        theta = 62 * DEGREES
        A = center + LEFT * r
        B = center + RIGHT * r
        P = center + r * np.array([np.cos(theta), np.sin(theta), 0])

        circle = Circle(radius=r, color=BLUE, stroke_width=5).move_to(center)
        dot_group = VGroup(Dot(A, color=WHITE), Dot(B, color=WHITE), Dot(P, color=YELLOW))
        labels = VGroup(
            self.math(r"A(-1,0)", font_size=26).next_to(A, DOWN, buff=0.12),
            self.math(r"B(1,0)", font_size=26).next_to(B, DOWN, buff=0.12),
            self.math(r"P", font_size=28, color=YELLOW).next_to(P, UP, buff=0.12),
        )
        pa = Line(P, A, color=YELLOW, stroke_width=4)
        pb = Line(P, B, color=YELLOW, stroke_width=4)
        right_angle = RightAngle(pa, pb, length=0.18, color=YELLOW)

        text1 = self.zh("圆里：直径 AB 对着 90°", font_size=30, color=BLUE).to_edge(RIGHT, buff=1.0).shift(UP * 1.0)
        f1 = self.math(r"k_{PA}\cdot k_{PB}=-1", font_size=44, color=BLUE).next_to(text1, DOWN, buff=0.45)
        cap1 = self.caption("这一步只用到高中熟悉的结论：直径所对的圆周角是直角。")

        self.start_voice(23)
        self.play(FadeIn(title), Create(circle), FadeIn(dot_group), FadeIn(labels))
        self.finish_voice()
        self.start_voice(24)
        self.play(Create(pa), Create(pb), FadeIn(right_angle), FadeIn(cap1))
        self.play(Write(text1), Write(f1))
        self.finish_voice()

        ellipse_center = LEFT * 3.0 + DOWN * 0.2
        a = 1.85
        b = 0.75
        A2 = ellipse_center + LEFT * a
        B2 = ellipse_center + RIGHT * a
        P2 = ellipse_center + np.array([a * np.cos(theta), b * np.sin(theta), 0])
        ellipse = Ellipse(width=2 * a, height=2 * b, color=RED, stroke_width=5).move_to(ellipse_center)
        dots2 = VGroup(Dot(A2, color=WHITE), Dot(B2, color=WHITE), Dot(P2, color=YELLOW))
        labels2 = VGroup(
            self.math(r"A'(-a,0)", font_size=26).next_to(A2, DOWN, buff=0.12),
            self.math(r"B'(a,0)", font_size=26).next_to(B2, DOWN, buff=0.12),
            self.math(r"P'", font_size=28, color=YELLOW).next_to(P2, UP, buff=0.12),
        )
        pa2 = Line(P2, A2, color=YELLOW, stroke_width=4)
        pb2 = Line(P2, B2, color=YELLOW, stroke_width=4)

        text2 = self.zh("椭圆里：斜率都乘上 b/a", font_size=30, color=RED).move_to(text1)
        f2 = self.math(
            r"k_{P'A'}\cdot k_{P'B'}"
            r"=\left(\frac{b}{a}\right)^2(-1)"
            r"=-\frac{b^2}{a^2}",
            font_size=36,
            color=RED,
        ).next_to(text2, DOWN, buff=0.45)
        result = self.math(
            r"\boxed{k_{P'A'}\cdot k_{P'B'}=-\frac{b^2}{a^2}}",
            font_size=40,
            color=YELLOW,
        ).next_to(f2, DOWN, buff=0.45)
        cap2 = self.caption("圆里的 -1，被横纵拉伸后，变成了椭圆里的 -b²/a²。")

        self.start_voice(25)
        self.play(
            Transform(circle, ellipse),
            Transform(dot_group, dots2),
            Transform(labels, labels2),
            Transform(pa, pa2),
            Transform(pb, pb2),
            FadeOut(right_angle),
            ReplacementTransform(cap1, cap2),
        )
        self.play(ReplacementTransform(text1, text2), ReplacementTransform(f1, f2))
        self.play(Write(result), Circumscribe(result, color=YELLOW))
        self.finish_voice()
        self.clear_scene()

    def midpoint_chord(self):
        title = self.section_title("第五步：中点弦结论也来自圆")

        center = LEFT * 3.1 + DOWN * 0.15
        r = 1.35
        t1 = 195 * DEGREES
        t2 = 75 * DEGREES
        A = center + r * np.array([np.cos(t1), np.sin(t1), 0])
        B = center + r * np.array([np.cos(t2), np.sin(t2), 0])
        M = (A + B) / 2
        O = center

        circle = Circle(radius=r, color=BLUE, stroke_width=5).move_to(center)
        chord = Line(A, B, color=YELLOW, stroke_width=5)
        radius_mid = Line(O, M, color=GREEN, stroke_width=5)
        dots = VGroup(Dot(A), Dot(B), Dot(M, color=GREEN), Dot(O, color=WHITE))
        labels = VGroup(
            self.math(r"A_1", font_size=26).next_to(A, LEFT, buff=0.08),
            self.math(r"B_1", font_size=26).next_to(B, RIGHT, buff=0.08),
            self.math(r"M_1", font_size=26, color=GREEN).next_to(M, UP, buff=0.08),
            self.math(r"O", font_size=26).next_to(O, DOWN, buff=0.08),
        )
        right_angle = RightAngle(chord, radius_mid, length=0.16, color=GREEN)

        text1 = self.zh("圆里：圆心连弦中点，垂直于弦", font_size=29, color=BLUE).to_edge(RIGHT, buff=0.55).shift(UP * 1.05)
        f1 = self.math(r"k_{OM_1}\cdot k_{A_1B_1}=-1", font_size=40, color=BLUE).next_to(text1, DOWN, buff=0.45)
        cap1 = self.caption("这就是垂径定理的斜率说法。")

        self.start_voice(26)
        self.play(FadeIn(title), Create(circle), Create(chord), Create(radius_mid))
        self.finish_voice()
        self.start_voice(27)
        self.play(FadeIn(dots), FadeIn(labels), FadeIn(right_angle), FadeIn(cap1))
        self.play(Write(text1), Write(f1))
        self.finish_voice()

        a = 1.75
        b = 0.72

        def stretch(point):
            v = point - center
            return center + np.array([a * v[0], b * v[1], 0])

        A2 = stretch(A)
        B2 = stretch(B)
        M2 = stretch(M)
        O2 = center
        ellipse = Ellipse(width=2 * a * r, height=2 * b * r, color=RED, stroke_width=5).move_to(center)
        chord2 = Line(A2, B2, color=YELLOW, stroke_width=5)
        radius_mid2 = Line(O2, M2, color=GREEN, stroke_width=5)
        dots2 = VGroup(Dot(A2), Dot(B2), Dot(M2, color=GREEN), Dot(O2, color=WHITE))
        labels2 = VGroup(
            self.math(r"A", font_size=26).next_to(A2, LEFT, buff=0.08),
            self.math(r"B", font_size=26).next_to(B2, RIGHT, buff=0.08),
            self.math(r"M", font_size=26, color=GREEN).next_to(M2, UP, buff=0.08),
            self.math(r"O", font_size=26).next_to(O2, DOWN, buff=0.08),
        )

        text2 = self.zh("椭圆里：不一定垂直，但斜率乘积固定", font_size=29, color=RED).move_to(text1)
        f2 = self.math(
            r"k_1=\frac{b}{a}k_{A_1B_1},\qquad "
            r"k_2=\frac{b}{a}k_{OM_1}",
            font_size=34,
            color=RED,
        ).next_to(text2, DOWN, buff=0.42)
        result = self.math(r"\boxed{k_1k_2=-\frac{b^2}{a^2}}", font_size=48, color=YELLOW).next_to(
            f2, DOWN, buff=0.45
        )
        cap2 = self.caption("所以，中点弦公式其实是垂径定理被拉伸后的版本。")

        self.start_voice(28)
        self.play(
            Transform(circle, ellipse),
            Transform(chord, chord2),
            Transform(radius_mid, radius_mid2),
            Transform(dots, dots2),
            Transform(labels, labels2),
            FadeOut(right_angle),
            ReplacementTransform(cap1, cap2),
        )
        self.play(ReplacementTransform(text1, text2), ReplacementTransform(f1, f2))
        self.finish_voice()
        self.start_voice(29)
        self.play(Write(result), Circumscribe(result, color=YELLOW))
        self.finish_voice()
        self.clear_scene()

    def summary(self):
        title = self.zh("最后，把主线串起来", font_size=48, color=YELLOW).to_edge(UP, buff=0.6)

        one = VGroup(
            self.zh("1", font_size=34, color=YELLOW),
            self.zh("圆经过横纵伸缩，变成椭圆", font_size=32),
            self.math(r"x^2+y^2=1\quad\Rightarrow\quad \frac{X^2}{a^2}+\frac{Y^2}{b^2}=1", font_size=34, color=BLUE_B),
        ).arrange(RIGHT, buff=0.35)

        two = VGroup(
            self.zh("2", font_size=34, color=YELLOW),
            self.zh("斜率会统一乘上", font_size=32),
            self.math(r"\frac{b}{a}", font_size=42, color=YELLOW),
        ).arrange(RIGHT, buff=0.35)

        three = VGroup(
            self.zh("3", font_size=34, color=YELLOW),
            self.zh("圆里的直角和垂径定理，会变成椭圆里的斜率乘积", font_size=32),
        ).arrange(RIGHT, buff=0.35)

        formulas = VGroup(
            self.math(r"k_{P'A'}k_{P'B'}=-\frac{b^2}{a^2}", font_size=40, color=RED),
            self.math(r"k_1k_2=-\frac{b^2}{a^2}", font_size=40, color=RED),
        ).arrange(RIGHT, buff=0.8)

        body = VGroup(one, two, three, formulas).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        body.next_to(title, DOWN, buff=0.55)
        body.shift(RIGHT * 0.15)

        self.start_voice(30)
        self.play(FadeIn(title))
        self.play(FadeIn(one, shift=RIGHT * 0.2))
        self.finish_voice()
        self.start_voice(31)
        self.play(FadeIn(two, shift=RIGHT * 0.2))
        self.play(FadeIn(three, shift=RIGHT * 0.2))
        self.finish_voice()
        self.start_voice(32)
        self.play(Write(formulas))
        self.finish_voice()
        if self.current_subtitle is not None:
            self.play(FadeOut(self.current_subtitle), run_time=0.3)
