from pathlib import Path

from manim import *
import numpy as np

try:
    from manimpango import list_fonts
except Exception:  # Only needed inside a full Manim runtime.
    list_fonts = None


BG = "#10131A"
PANEL = "#17212B"
PANEL_DARK = "#111923"
GRID = "#263544"
TEXT = "#EEF4FF"
MUTED = "#AEBCCD"
BLUE = "#67B7FF"
GREEN = "#70D993"
GOLD = "#F2C14E"
ORANGE = "#FFB86B"
RED = "#FF6B7A"
CYAN = "#77E6E2"
VOICEOVER_FILES = tuple(sorted(Path("配音").glob("*.mp3")))


def choose_font():
    if list_fonts is None:
        return "Microsoft YaHei"
    available = set(list_fonts())
    for font in (
        "Microsoft YaHei",
        "Microsoft JhengHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
    ):
        if font in available:
            return font
    return "sans-serif"


CN_FONT = choose_font()


def unit(vector):
    length = np.linalg.norm(vector)
    return vector / length


def fit_width(mob, max_width):
    if mob.width > max_width:
        mob.scale(max_width / mob.width)
    return mob


def ctext(content, size=30, color=TEXT, weight=NORMAL, **kwargs):
    mob = Text(content, font=CN_FONT, font_size=size, color=color, weight=weight, **kwargs)
    mob.set_z_index(5)
    return mob


def ftex(tex, size=42, color=TEXT, width=4.95):
    mob = MathTex(tex, font_size=size, color=color)
    mob.set_color_by_tex("S_1", BLUE)
    mob.set_color_by_tex("S_2", GREEN)
    mob.set_color_by_tex("BD", BLUE)
    mob.set_color_by_tex("DC", GREEN)
    mob.set_color_by_tex("AB", BLUE)
    mob.set_color_by_tex("AC", GREEN)
    mob.set_color_by_tex("AD", ORANGE)
    mob.set_color_by_tex(r"\alpha", GOLD)
    mob.set_color_by_tex("h", RED)
    mob.set_z_index(6)
    return fit_width(mob, width)


def angle_bisector_foot(a, b, c):
    direction = unit(b - a) + unit(c - a)
    base = c - b
    matrix = np.column_stack((direction[:2], -base[:2]))
    rhs = (b - a)[:2]
    s, _ = np.linalg.solve(matrix, rhs)
    return a + s * direction


def external_angle_bisector_foot(a, b, c):
    direction = unit(b - a) - unit(c - a)
    base = c - b
    matrix = np.column_stack((direction[:2], -base[:2]))
    rhs = (b - a)[:2]
    s, _ = np.linalg.solve(matrix, rhs)
    return a + s * direction


def project_point_to_line(point, line_start, line_end):
    direction = line_end - line_start
    t = np.dot(point - line_start, direction) / np.dot(direction, direction)
    return line_start + t * direction


def right_angle_marker(corner, side_point, height_point, size=0.2, color=RED):
    side_dir = unit(side_point - corner)
    height_dir = unit(height_point - corner)
    marker = VMobject(color=color, stroke_width=3)
    marker.set_points_as_corners(
        [
            corner,
            corner + side_dir * size,
            corner + side_dir * size + height_dir * size,
            corner + height_dir * size,
        ]
    )
    return marker


def short_delta(start, end):
    return (end - start + PI) % TAU - PI


def arc_between(center, p1, p2, radius, color):
    a1 = np.arctan2((p1 - center)[1], (p1 - center)[0])
    a2 = np.arctan2((p2 - center)[1], (p2 - center)[0])
    return Arc(
        radius=radius,
        start_angle=a1,
        angle=short_delta(a1, a2),
        arc_center=center,
        color=color,
        stroke_width=5,
    )


def mini_chip(text, color):
    label = ctext(text, size=22, color=color, weight=BOLD)
    box = RoundedRectangle(
        width=label.width + 0.46,
        height=0.44,
        corner_radius=0.08,
        stroke_width=1.5,
        stroke_color=color,
        fill_color=PANEL_DARK,
        fill_opacity=0.92,
    )
    label.move_to(box)
    return VGroup(box, label)


def proof_panel(title, lines, note=None, accent=GOLD, panel_width=5.55):
    inner_width = panel_width - 0.6
    header = ctext(title, size=27, color=accent, weight=BOLD)
    rule = Line(LEFT, RIGHT, color=accent, stroke_width=3).set_width(inner_width)
    formulas = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.21)
    parts = VGroup(header, rule, formulas).arrange(DOWN, aligned_edge=LEFT, buff=0.22)

    if note:
        note_mob = ctext(note, size=23, color=MUTED)
        note_mob = fit_width(note_mob, inner_width)
        parts.add(note_mob)
        parts.arrange(DOWN, aligned_edge=LEFT, buff=0.22)

    box = RoundedRectangle(
        width=panel_width,
        height=max(3.25, parts.height + 0.66),
        corner_radius=0.12,
        stroke_width=1.6,
        stroke_color=GRID,
        fill_color=PANEL,
        fill_opacity=0.95,
    )
    accent_bar = RoundedRectangle(
        width=0.08,
        height=box.height - 0.38,
        corner_radius=0.04,
        stroke_width=0,
        fill_color=accent,
        fill_opacity=1,
    )
    accent_bar.next_to(box, LEFT, buff=-0.18)
    parts.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.36)
    return VGroup(box, accent_bar, parts)


class AngleBisectorAreaProof(Scene):
    def voice(self, number):
        if number > len(VOICEOVER_FILES):
            raise FileNotFoundError(f"Missing voiceover file #{number:04d} in 配音")
        self.add_sound(str(VOICEOVER_FILES[number - 1]))

    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.setup_geometry()
        self.same_height_area_ratio()
        self.equal_distance_area_ratio()
        self.combine_results()
        self.fade_out_inner_scene()
        self.exterior_setup_geometry()
        self.exterior_same_height_area_ratio()
        self.exterior_equal_distance_area_ratio()
        self.exterior_combine_results()
        self.exterior_final_recap()

    def intro(self):
        title = ctext("内角平分线定理", size=46, color=GOLD, weight=BOLD)
        title.to_edge(UP, buff=0.55)

        a = np.array([-3.95, 1.05, 0.0])
        b = np.array([-5.25, -1.32, 0.0])
        c = np.array([-2.05, -1.32, 0.0])
        d = angle_bisector_foot(a, b, c)

        triangle_fill = Polygon(a, b, d, fill_color=BLUE, fill_opacity=0.18, stroke_width=0)
        triangle_fill_2 = Polygon(a, d, c, fill_color=GREEN, fill_opacity=0.16, stroke_width=0)
        sketch = VGroup(
            triangle_fill,
            triangle_fill_2,
            Polygon(a, b, c, color=TEXT, stroke_width=4),
            Line(a, d, color=ORANGE, stroke_width=4),
            arc_between(a, b, d, 0.28, GOLD),
            arc_between(a, d, c, 0.39, GOLD),
            Dot(a, radius=0.045, color=TEXT),
            Dot(b, radius=0.045, color=TEXT),
            Dot(c, radius=0.045, color=TEXT),
            Dot(d, radius=0.05, color=ORANGE),
            ctext("A", size=24).next_to(a, UP, buff=0.13),
            ctext("B", size=24).next_to(b, DOWN + LEFT, buff=0.1),
            ctext("C", size=24).next_to(c, DOWN + RIGHT, buff=0.1),
            ctext("D", size=24, color=ORANGE).next_to(d, DOWN, buff=0.12),
        )

        condition = ctext("如果 AD 平分 ∠A，且 D 在 BC 上", size=26, color=TEXT)
        condition.move_to(RIGHT * 2.2 + UP * 0.9)
        meaning = ctext("那么：对边两段的比 = 两条邻边的比", size=25, color=MUTED)
        meaning.next_to(condition, DOWN, buff=0.28)
        theorem = ftex(r"\boxed{\frac{BD}{DC}=\frac{AB}{AC}}", size=58, width=4.25)
        theorem.next_to(meaning, DOWN, buff=0.42)
        result = VGroup(condition, meaning, theorem)

        bg_card = RoundedRectangle(
            width=11.6,
            height=4.35,
            corner_radius=0.16,
            stroke_width=1.5,
            stroke_color=GRID,
            fill_color=PANEL,
            fill_opacity=0.86,
        )
        bg_card.shift(DOWN * 0.2)
        bg_card.set_z_index(0)

        prompt = ctext("接下来，用等面积法证明这个结论。", size=25, color=CYAN)
        prompt.next_to(bg_card, DOWN, buff=0.28)

        self.voice(1)
        self.play(FadeIn(bg_card, scale=0.98), Write(title))
        self.play(Create(sketch), FadeIn(result, shift=LEFT * 0.18))
        self.wait(1.45)
        self.voice(2)
        self.play(Circumscribe(theorem, color=GOLD), FadeIn(prompt, shift=UP * 0.12))
        self.wait(2.15)
        self.play(FadeOut(bg_card), FadeOut(title), FadeOut(sketch), FadeOut(result), FadeOut(prompt))

    def setup_geometry(self):
        self.title = ctext("等面积法证明", size=34, color=TEXT, weight=BOLD)
        self.title.to_edge(UP, buff=0.25).shift(LEFT * 3.6)
        self.subtitle = ctext("同一个面积比，换两种方式计算", size=22, color=MUTED)
        self.subtitle.next_to(self.title, DOWN, buff=0.08)

        a = np.array([-1.75, 2.05, 0.0])
        b = np.array([-6.05, -2.05, 0.0])
        c = np.array([0.75, -2.05, 0.0])
        d = angle_bisector_foot(a, b, c)
        h = np.array([a[0], b[1], 0.0])
        e = project_point_to_line(d, a, b)
        f = project_point_to_line(d, a, c)
        self.a, self.b, self.c, self.d, self.h, self.e, self.f = a, b, c, d, h, e, f

        self.left_area = Polygon(a, b, d, fill_color=BLUE, fill_opacity=0.27, stroke_width=0)
        self.right_area = Polygon(a, d, c, fill_color=GREEN, fill_opacity=0.25, stroke_width=0)
        self.triangle = Polygon(a, b, c, color=TEXT, stroke_width=5)
        self.ad = Line(a, d, color=ORANGE, stroke_width=5)
        self.bd = Line(b, d, color=BLUE, stroke_width=7)
        self.dc = Line(d, c, color=GREEN, stroke_width=7)

        self.side_ab = Line(a, b, color=BLUE, stroke_width=7)
        self.side_ac = Line(a, c, color=GREEN, stroke_width=7)

        self.angle_left = arc_between(a, b, d, 0.46, GOLD)
        self.angle_right = arc_between(a, d, c, 0.64, GOLD)
        alpha_l_pos = a + unit(unit(b - a) + unit(d - a)) * 0.82
        alpha_r_pos = a + unit(unit(d - a) + unit(c - a)) * 1.04
        self.alpha_left = ftex(r"\alpha", size=31, color=GOLD, width=1.0).move_to(alpha_l_pos)
        self.alpha_right = ftex(r"\alpha", size=31, color=GOLD, width=1.0).move_to(alpha_r_pos)

        self.height = DashedLine(a, h, color=RED, dash_length=0.12, stroke_width=4)
        self.height_label = VGroup(
            ftex("h", size=30, color=RED, width=0.7),
            ctext("同高", size=20, color=RED, weight=BOLD),
        ).arrange(DOWN, buff=0.02)
        self.height_label.next_to(self.height, RIGHT, buff=0.24).shift(UP * 0.2)
        self.right_angle = VMobject(color=RED, stroke_width=3)
        self.right_angle.set_points_as_corners(
            [h, h + UP * 0.22, h + UP * 0.22 + RIGHT * 0.22, h + RIGHT * 0.22]
        )

        self.dist_to_ab = DashedLine(d, e, color=RED, dash_length=0.1, stroke_width=4)
        self.dist_to_ac = DashedLine(d, f, color=RED, dash_length=0.1, stroke_width=4)
        self.dist_angle_ab = right_angle_marker(e, a, d, size=0.18, color=RED)
        self.dist_angle_ac = right_angle_marker(f, c, d, size=0.18, color=RED)
        self.dist_ab_label = ftex("h", size=29, color=RED, width=0.7)
        self.dist_ab_label.move_to((d + e) / 2 + LEFT * 0.26 + UP * 0.06)
        self.dist_ac_label = ftex("h", size=29, color=RED, width=0.7)
        self.dist_ac_label.move_to((d + f) / 2 + RIGHT * 0.28 + UP * 0.02)
        self.equal_height_group = VGroup(
            self.dist_to_ab,
            self.dist_to_ac,
            self.dist_angle_ab,
            self.dist_angle_ac,
            self.dist_ab_label,
            self.dist_ac_label,
        )

        self.dots = VGroup(
            Dot(a, radius=0.06, color=TEXT),
            Dot(b, radius=0.06, color=TEXT),
            Dot(c, radius=0.06, color=TEXT),
            Dot(d, radius=0.065, color=ORANGE),
        )
        self.labels = VGroup(
            ctext("A", size=27, color=TEXT).next_to(a, UP, buff=0.18),
            ctext("B", size=27, color=TEXT).next_to(b, DOWN + LEFT, buff=0.14),
            ctext("C", size=27, color=TEXT).next_to(c, DOWN + RIGHT, buff=0.14),
            ctext("D", size=27, color=ORANGE).next_to(d, DOWN, buff=0.18),
        )

        self.brace_bd = BraceBetweenPoints(b, d, direction=DOWN, color=BLUE)
        self.brace_dc = BraceBetweenPoints(d, c, direction=DOWN, color=GREEN)
        self.bd_label = ftex("BD", size=29, color=BLUE, width=1.0).next_to(self.brace_bd, DOWN, buff=0.04)
        self.dc_label = ftex("DC", size=29, color=GREEN, width=1.0).next_to(self.brace_dc, DOWN, buff=0.04)

        self.ab_label = ftex("AB", size=29, color=BLUE, width=1.0)
        self.ab_label.move_to((a + b) / 2 + LEFT * 0.55 + UP * 0.15)
        self.ac_label = ftex("AC", size=29, color=GREEN, width=1.0)
        self.ac_label.move_to((a + c) / 2 + RIGHT * 0.52 + UP * 0.17)

        self.s1_label = ftex(r"S_1", size=35, color=BLUE, width=0.9)
        self.s1_label.move_to((a + b + d) / 3 + RIGHT * 0.34 + DOWN * 0.02)
        self.s2_label = ftex(r"S_2", size=35, color=GREEN, width=0.9)
        self.s2_label.move_to((a + d + c) / 3 + RIGHT * 0.42 + DOWN * 0.05)

        opening_panel = proof_panel(
            "命题",
            [
                ctext("条件：AD 平分 ∠A，D 在 BC 上", size=27, color=TEXT),
                VGroup(
                    ctext("结论：", size=27, color=TEXT),
                    ftex(r"\frac{BD}{DC}=\frac{AB}{AC}", size=34, width=3.4),
                ).arrange(RIGHT, buff=0.12),
            ],
            note="思想：用不同的方法计算面积",
            accent=CYAN,
            panel_width=6.05,
        )
        self.current_panel = opening_panel.to_edge(RIGHT, buff=0.43).shift(DOWN * 0.1)

        self.progress = VGroup(
            mini_chip("1 共高看底边", BLUE),
            mini_chip("2 等距作高", GOLD),
            mini_chip("3 合并比例", RED),
        ).arrange(RIGHT, buff=0.18)
        self.progress.to_edge(DOWN, buff=0.26).shift(LEFT * 0.45)

        self.play(FadeIn(self.title, shift=DOWN * 0.12), FadeIn(self.subtitle, shift=DOWN * 0.12))
        self.wait(0.2)
        self.voice(3)
        self.play(Create(self.triangle), FadeIn(self.dots), Write(self.labels))
        self.play(Create(self.ad), Create(self.angle_left), Create(self.angle_right))
        self.play(Write(self.alpha_left), Write(self.alpha_right))
        self.voice(4)
        self.play(FadeIn(self.current_panel, shift=LEFT * 0.2), FadeIn(self.progress, shift=UP * 0.15))
        self.wait(3.0)
        self.voice(5)

    def same_height_area_ratio(self):
        panel = proof_panel(
            "第一种算法：共高",
            [
                ftex(r"S_1=\frac12\cdot BD\cdot h", size=35),
                ftex(r"S_2=\frac12\cdot DC\cdot h", size=35),
                ftex(r"\frac{S_1}{S_2}=\frac{BD}{DC}", size=44),
            ],
            note="两个小三角形的高都是从 A 到 BC 的 h",
            accent=BLUE,
        )
        panel.to_edge(RIGHT, buff=0.43).shift(DOWN * 0.1)

        self.play(FadeOut(self.current_panel, shift=LEFT * 0.12), FadeIn(panel, shift=LEFT * 0.12))
        self.current_panel = panel
        self.play(FadeIn(self.left_area), FadeIn(self.right_area))
        self.play(FadeIn(self.s1_label), FadeIn(self.s2_label))
        self.play(Create(self.height), Create(self.right_angle), FadeIn(self.height_label))
        self.play(GrowFromCenter(self.brace_bd), GrowFromCenter(self.brace_dc))
        self.play(Write(self.bd_label), Write(self.dc_label))
        self.voice(6)
        self.play(Create(self.bd), Create(self.dc))
        self.play(Indicate(self.progress[0], color=BLUE), Circumscribe(self.height, color=RED))
        self.wait(7.3)

    def equal_distance_area_ratio(self):
        panel = proof_panel(
            "第二种算法：等距作高",
            [
                ftex(r"d(D,AB)=d(D,AC)=h", size=31),
                ftex(r"S_1=\frac12\cdot AB\cdot h", size=32),
                ftex(r"S_2=\frac12\cdot AC\cdot h", size=32),
                ftex(r"\frac{S_1}{S_2}=\frac{AB}{AC}", size=44),
            ],
            note="角平分线上一点到两边距离相等，把这个距离当成高",
            accent=GOLD,
        )
        panel.to_edge(RIGHT, buff=0.43).shift(DOWN * 0.1)

        self.voice(7)
        self.play(FadeOut(self.current_panel, shift=LEFT * 0.12), FadeIn(panel, shift=LEFT * 0.12))
        self.current_panel = panel
        self.play(FadeOut(self.height), FadeOut(self.right_angle), FadeOut(self.height_label))
        self.play(FadeOut(self.bd), FadeOut(self.dc), FadeOut(self.brace_bd), FadeOut(self.brace_dc))
        self.voice(8)
        self.play(FadeOut(self.bd_label), FadeOut(self.dc_label))
        self.play(Create(self.side_ab), Create(self.side_ac))
        self.play(Write(self.ab_label), Write(self.ac_label))
        self.play(Indicate(self.ad, color=ORANGE), Indicate(self.angle_left, color=GOLD), Indicate(self.angle_right, color=GOLD))
        self.play(Create(self.dist_to_ab), Create(self.dist_to_ac))
        self.play(Create(self.dist_angle_ab), Create(self.dist_angle_ac), Write(self.dist_ab_label), Write(self.dist_ac_label))
        self.voice(9)
        self.play(Indicate(self.equal_height_group, color=RED))
        self.play(Indicate(self.progress[1], color=GOLD))
        self.wait(3.5)

    def combine_results(self):
        panel = proof_panel(
            "合并：同一个面积比",
            [
                ftex(r"\frac{S_1}{S_2}=\frac{BD}{DC}", size=39),
                ftex(r"\frac{S_1}{S_2}=\frac{AB}{AC}", size=39),
                ftex(r"\therefore\quad \frac{BD}{DC}=\frac{AB}{AC}", size=47),
            ],
            note="这就是三角形内角平分线定理",
            accent=RED,
        )
        panel.to_edge(RIGHT, buff=0.43).shift(DOWN * 0.1)

        self.voice(10)
        self.play(FadeOut(self.current_panel, shift=LEFT * 0.12), FadeIn(panel, shift=LEFT * 0.12))
        self.current_panel = panel
        self.play(FadeOut(self.equal_height_group))
        self.play(FadeOut(self.side_ab), FadeOut(self.side_ac))
        self.play(FadeOut(self.ab_label), FadeOut(self.ac_label))
        self.play(
            Create(self.bd),
            Create(self.dc),
            Create(self.side_ab),
            Create(self.side_ac),
        )
        self.play(
            Circumscribe(self.bd, color=BLUE),
            Circumscribe(self.dc, color=GREEN),
            Circumscribe(self.side_ab, color=BLUE),
            Circumscribe(self.side_ac, color=GREEN),
        )
        self.voice(11)
        self.play(Indicate(self.progress[2], color=RED))
        self.wait(1.6)

    def fade_out_inner_scene(self):
        everything = VGroup(
            self.title,
            self.subtitle,
            self.current_panel,
            self.progress,
            self.left_area,
            self.right_area,
            self.triangle,
            self.ad,
            self.bd,
            self.dc,
            self.side_ab,
            self.side_ac,
            self.angle_left,
            self.angle_right,
            self.alpha_left,
            self.alpha_right,
            self.dots,
            self.labels,
            self.s1_label,
            self.s2_label,
        )
        self.play(FadeOut(everything, shift=DOWN * 0.15))

    def exterior_setup_geometry(self):
        self.ext_title = ctext("外角平分线定理证明", size=34, color=TEXT, weight=BOLD)
        self.ext_title.to_edge(UP, buff=0.25).shift(LEFT * 3.2)
        self.ext_subtitle = ctext("证明思路和内角情形一致", size=22, color=MUTED)
        self.ext_subtitle.next_to(self.ext_title, DOWN, buff=0.08)

        a = np.array([-3.3, 0.75, 0.0])
        b = np.array([-6.5, -1.4, 0.0])
        c = np.array([-3.7, -1.4, 0.0])
        d = external_angle_bisector_foot(a, b, c)
        h = np.array([a[0], b[1], 0.0])
        e = project_point_to_line(d, a, b)
        f = project_point_to_line(d, a, c)
        ab_ext = a - unit(b - a) * 1.6
        self.ext_a, self.ext_b, self.ext_c, self.ext_d = a, b, c, d

        self.ext_left_area = Polygon(a, b, d, fill_color=BLUE, fill_opacity=0.22, stroke_width=0)
        self.ext_right_area = Polygon(a, c, d, fill_color=GREEN, fill_opacity=0.27, stroke_width=0)
        self.ext_triangle = VGroup(
            Polygon(a, b, c, color=TEXT, stroke_width=5),
            Line(c, d, color=TEXT, stroke_width=5),
        )
        self.ext_ad = Line(a, d, color=ORANGE, stroke_width=5)
        self.ext_ab_extension = DashedLine(a, ab_ext, color=MUTED, dash_length=0.12, stroke_width=3)

        self.ext_bd = Line(b, d, color=BLUE, stroke_width=7)
        self.ext_dc = Line(c, d, color=GREEN, stroke_width=7)
        self.ext_side_ab = Line(a, b, color=BLUE, stroke_width=7)
        self.ext_side_ac = Line(a, c, color=GREEN, stroke_width=7)

        self.ext_angle_1 = arc_between(a, ab_ext, d, 0.43, GOLD)
        self.ext_angle_2 = arc_between(a, d, c, 0.58, GOLD)
        beta_1_pos = a + unit(unit(ab_ext - a) + unit(d - a)) * 0.72
        beta_2_pos = a + unit(unit(d - a) + unit(c - a)) * 0.87
        self.ext_beta_1 = ftex(r"\beta", size=31, color=GOLD, width=1.0).move_to(beta_1_pos)
        self.ext_beta_2 = ftex(r"\beta", size=31, color=GOLD, width=1.0).move_to(beta_2_pos)

        self.ext_height = DashedLine(a, h, color=RED, dash_length=0.12, stroke_width=4)
        self.ext_height_label = VGroup(
            ftex("h", size=30, color=RED, width=0.7),
            ctext("同高", size=20, color=RED, weight=BOLD),
        ).arrange(DOWN, buff=0.02)
        self.ext_height_label.next_to(self.ext_height, RIGHT, buff=0.16).shift(DOWN * 0.18)
        self.ext_right_angle = right_angle_marker(h, d, a, size=0.2, color=RED)

        self.ext_dist_to_ab = DashedLine(d, e, color=RED, dash_length=0.1, stroke_width=4)
        self.ext_dist_to_ac = DashedLine(d, f, color=RED, dash_length=0.1, stroke_width=4)
        self.ext_dist_angle_ab = right_angle_marker(e, a, d, size=0.18, color=RED)
        self.ext_dist_angle_ac = right_angle_marker(f, a, d, size=0.18, color=RED)
        self.ext_dist_ab_label = ftex("h", size=29, color=RED, width=0.7)
        self.ext_dist_ab_label.move_to((d + e) / 2 + RIGHT * 0.24 + UP * 0.08)
        self.ext_dist_ac_label = ftex("h", size=29, color=RED, width=0.7)
        self.ext_dist_ac_label.move_to((d + f) / 2 + DOWN * 0.22)
        self.ext_equal_height_group = VGroup(
            self.ext_dist_to_ab,
            self.ext_dist_to_ac,
            self.ext_dist_angle_ab,
            self.ext_dist_angle_ac,
            self.ext_dist_ab_label,
            self.ext_dist_ac_label,
        )

        self.ext_dots = VGroup(
            Dot(a, radius=0.06, color=TEXT),
            Dot(b, radius=0.06, color=TEXT),
            Dot(c, radius=0.06, color=TEXT),
            Dot(d, radius=0.065, color=ORANGE),
        )
        self.ext_labels = VGroup(
            ctext("A", size=27, color=TEXT).next_to(a, UP, buff=0.16),
            ctext("B", size=27, color=TEXT).next_to(b, DOWN + LEFT, buff=0.14),
            ctext("C", size=27, color=TEXT).next_to(c, DOWN, buff=0.14),
            ctext("D", size=27, color=ORANGE).next_to(d, DOWN + RIGHT, buff=0.14),
        )

        self.ext_brace_bd = BraceBetweenPoints(b, d, direction=DOWN, color=BLUE)
        self.ext_brace_dc = BraceBetweenPoints(c, d, direction=UP, color=GREEN)
        self.ext_bd_label = ftex("BD", size=29, color=BLUE, width=1.0).next_to(self.ext_brace_bd, DOWN, buff=0.04)
        self.ext_dc_label = ftex("DC", size=29, color=GREEN, width=1.0).next_to(self.ext_brace_dc, UP, buff=0.04)

        self.ext_ab_label = ftex("AB", size=29, color=BLUE, width=1.0)
        self.ext_ab_label.move_to((a + b) / 2 + LEFT * 0.34 + UP * 0.16)
        self.ext_ac_label = ftex("AC", size=29, color=GREEN, width=1.0)
        self.ext_ac_label.move_to((a + c) / 2 + RIGHT * 0.32 + DOWN * 0.02)

        self.ext_s1_label = ftex(r"S_1", size=35, color=BLUE, width=0.9)
        self.ext_s1_label.move_to((a + b + d) / 3 + LEFT * 0.74 + UP * 0.1)
        self.ext_s2_label = ftex(r"S_2", size=35, color=GREEN, width=0.9)
        self.ext_s2_label.move_to((a + c + d) / 3 + RIGHT * 0.78 + UP * 0.23)

        opening_panel = proof_panel(
            "外角命题",
            [
                ctext("条件：AD 平分 ∠A 的外角", size=26, color=TEXT),
                ctext("D 在 BC 的延长线上", size=26, color=TEXT),
                VGroup(
                    ctext("结论：", size=26, color=TEXT),
                    ftex(r"\frac{BD}{DC}=\frac{AB}{AC}", size=34, width=3.35),
                ).arrange(RIGHT, buff=0.12),
            ],
            note="思想：仍然用不同的方法计算面积",
            accent=CYAN,
            panel_width=6.05,
        )
        self.ext_current_panel = opening_panel.to_edge(RIGHT, buff=0.28).shift(DOWN * 0.1)

        self.ext_progress = VGroup(
            mini_chip("1 共高看底边", BLUE),
            mini_chip("2 等距作高", GOLD),
            mini_chip("3 合并比例", RED),
        ).arrange(RIGHT, buff=0.18)
        self.ext_progress.to_edge(DOWN, buff=0.26).shift(LEFT * 0.45)

        self.voice(12)
        self.play(FadeIn(self.ext_title, shift=DOWN * 0.12), FadeIn(self.ext_subtitle, shift=DOWN * 0.12))
        self.play(Create(self.ext_triangle), FadeIn(self.ext_dots), Write(self.ext_labels))
        self.voice(13)
        self.play(Create(self.ext_ab_extension), Create(self.ext_ad), Create(self.ext_angle_1), Create(self.ext_angle_2))
        self.play(Write(self.ext_beta_1), Write(self.ext_beta_2))
        self.play(FadeIn(self.ext_current_panel, shift=LEFT * 0.2), FadeIn(self.ext_progress, shift=UP * 0.15))
        self.wait(1.3)
        self.voice(14)

    def exterior_same_height_area_ratio(self):
        panel = proof_panel(
            "第一种算法：共高",
            [
                ftex(r"S_1=\frac12\cdot BD\cdot h", size=35),
                ftex(r"S_2=\frac12\cdot DC\cdot h", size=35),
                ftex(r"\frac{S_1}{S_2}=\frac{BD}{DC}", size=44),
            ],
            note="两个三角形都用从 A 到 BC 所在直线的高",
            accent=BLUE,
        )
        panel.to_edge(RIGHT, buff=0.43).shift(DOWN * 0.1)

        self.play(FadeOut(self.ext_current_panel, shift=LEFT * 0.12), FadeIn(panel, shift=LEFT * 0.12))
        self.ext_current_panel = panel
        self.play(FadeIn(self.ext_left_area), FadeIn(self.ext_right_area))
        self.voice(15)
        self.play(FadeIn(self.ext_s1_label), FadeIn(self.ext_s2_label))
        self.play(Create(self.ext_height), Create(self.ext_right_angle), FadeIn(self.ext_height_label))
        self.play(GrowFromCenter(self.ext_brace_bd), GrowFromCenter(self.ext_brace_dc))
        self.play(Write(self.ext_bd_label), Write(self.ext_dc_label))
        self.play(Create(self.ext_bd), Create(self.ext_dc))
        self.play(Indicate(self.ext_progress[0], color=BLUE), Circumscribe(self.ext_height, color=RED))
        self.wait(2.1)

    def exterior_equal_distance_area_ratio(self):
        panel = proof_panel(
            "第二种算法：等距作高",
            [
                ftex(r"d(D,AB)=d(D,AC)=h", size=31),
                ftex(r"S_1=\frac12\cdot AB\cdot h", size=32),
                ftex(r"S_2=\frac12\cdot AC\cdot h", size=32),
                ftex(r"\frac{S_1}{S_2}=\frac{AB}{AC}", size=44),
            ],
            note="D 在外角平分线上，到两边距离相等",
            accent=GOLD,
        )
        panel.to_edge(RIGHT, buff=0.43).shift(DOWN * 0.1)

        self.voice(16)
        self.play(FadeOut(self.ext_current_panel, shift=LEFT * 0.12), FadeIn(panel, shift=LEFT * 0.12))
        self.ext_current_panel = panel
        self.play(FadeOut(self.ext_height), FadeOut(self.ext_right_angle), FadeOut(self.ext_height_label))
        self.play(FadeOut(self.ext_bd), FadeOut(self.ext_dc), FadeOut(self.ext_brace_bd), FadeOut(self.ext_brace_dc))
        self.play(FadeOut(self.ext_bd_label), FadeOut(self.ext_dc_label))
        self.play(Create(self.ext_side_ab), Create(self.ext_side_ac))
        self.play(Write(self.ext_ab_label), Write(self.ext_ac_label))
        self.play(Indicate(self.ext_ad, color=ORANGE), Indicate(self.ext_angle_1, color=GOLD), Indicate(self.ext_angle_2, color=GOLD))
        self.play(Create(self.ext_dist_to_ab), Create(self.ext_dist_to_ac))
        self.play(
            Create(self.ext_dist_angle_ab),
            Create(self.ext_dist_angle_ac),
            Write(self.ext_dist_ab_label),
            Write(self.ext_dist_ac_label),
        )
        self.play(Indicate(self.ext_equal_height_group, color=RED))
        self.play(Indicate(self.ext_progress[1], color=GOLD))
        self.wait(2.1)

    def exterior_combine_results(self):
        panel = proof_panel(
            "合并：同一个面积比",
            [
                ftex(r"\frac{S_1}{S_2}=\frac{BD}{DC}", size=39),
                ftex(r"\frac{S_1}{S_2}=\frac{AB}{AC}", size=39),
                ftex(r"\therefore\quad \frac{BD}{DC}=\frac{AB}{AC}", size=47),
            ],
            note="这就是三角形外角平分线定理",
            accent=RED,
        )
        panel.to_edge(RIGHT, buff=0.43).shift(DOWN * 0.1)

        self.voice(17)
        self.play(FadeOut(self.ext_current_panel, shift=LEFT * 0.12), FadeIn(panel, shift=LEFT * 0.12))
        self.ext_current_panel = panel
        self.play(FadeOut(self.ext_equal_height_group))
        self.play(FadeOut(self.ext_side_ab), FadeOut(self.ext_side_ac))
        self.play(FadeOut(self.ext_ab_label), FadeOut(self.ext_ac_label))
        self.play(
            Create(self.ext_bd),
            Create(self.ext_dc),
            Create(self.ext_side_ab),
            Create(self.ext_side_ac),
        )
        self.play(
            Circumscribe(self.ext_bd, color=BLUE),
            Circumscribe(self.ext_dc, color=GREEN),
            Circumscribe(self.ext_side_ab, color=BLUE),
            Circumscribe(self.ext_side_ac, color=GREEN),
        )
        self.play(Indicate(self.ext_progress[2], color=RED))
        self.wait(2.6)

    def exterior_final_recap(self):
        recap = VGroup(
            ctext("外角平分线定理", size=30, color=GOLD, weight=BOLD),
            ctext("证明结构和内角情形完全平行。", size=31, color=TEXT, weight=BOLD),
            ctext("共高给出 BD:DC，等距作高给出 AB:AC。", size=25, color=MUTED),
            ftex(r"\boxed{\frac{BD}{DC}=\frac{AB}{AC}}", size=50, width=5.2),
        ).arrange(DOWN, buff=0.18)
        box = RoundedRectangle(
            width=6.75,
            height=recap.height + 0.7,
            corner_radius=0.14,
            stroke_width=2,
            stroke_color=GOLD,
            fill_color=PANEL,
            fill_opacity=0.96,
        )
        recap.move_to(box)
        final_card = VGroup(box, recap).move_to(ORIGIN)

        everything = VGroup(
            self.ext_title,
            self.ext_subtitle,
            self.ext_current_panel,
            self.ext_progress,
            self.ext_left_area,
            self.ext_right_area,
            self.ext_triangle,
            self.ext_ab_extension,
            self.ext_ad,
            self.ext_bd,
            self.ext_dc,
            self.ext_side_ab,
            self.ext_side_ac,
            self.ext_angle_1,
            self.ext_angle_2,
            self.ext_beta_1,
            self.ext_beta_2,
            self.ext_dots,
            self.ext_labels,
            self.ext_s1_label,
            self.ext_s2_label,
        )
        self.voice(18)
        self.play(FadeOut(everything, shift=DOWN * 0.15))
        self.play(FadeIn(final_card, scale=0.98))
        self.wait(6.0)
