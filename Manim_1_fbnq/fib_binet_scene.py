from manim import *
from pathlib import Path

try:
    from manimpango import list_fonts
except Exception:  # pragma: no cover - only used inside Manim runtime
    list_fonts = None


BG = "#0F1417"
PANEL = "#172126"
GOLD = "#F2C14E"
TEAL = "#6EE7D8"
BLUE = "#7AA2F7"
ROSE = "#F7768E"
GREEN = "#9ECE6A"
MUTED = "#B9C4CC"
VOICE_DIR = Path(__file__).resolve().parent / "配音文件"


def choose_font():
    if list_fonts is None:
        return "Microsoft YaHei"
    available = set(list_fonts())
    for font in ("Microsoft YaHei", "Microsoft JhengHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC"):
        if font in available:
            return font
    return "sans-serif"


CN_FONT = choose_font()


def ctext(content, size=32, color=WHITE, weight=NORMAL, **kwargs):
    return Text(content, font=CN_FONT, font_size=size, color=color, weight=weight, **kwargs)


def mathtex(*parts, size=42, color=WHITE):
    tex = MathTex(*parts, font_size=size, color=color)
    tex.set_z_index(2)
    return tex


def fit_width(mob, max_width=12.2):
    if mob.width > max_width:
        mob.scale(max_width / mob.width)
    return mob


def caption(text):
    box = RoundedRectangle(
        corner_radius=0.08,
        width=12.7,
        height=0.74,
        stroke_width=0,
        fill_color=PANEL,
        fill_opacity=0.92,
    )
    label = ctext(text, size=28, color=MUTED)
    label.move_to(box)
    return VGroup(box, label).to_edge(DOWN, buff=0.25)


def teaching_card(lines, accent=GOLD, width=11.8, font_size=25, align=LEFT):
    if isinstance(lines, str):
        lines = [lines]
    text_group = VGroup(
        *[ctext(line, size=font_size, color=WHITE if i == 0 else MUTED) for i, line in enumerate(lines)]
    ).arrange(DOWN, aligned_edge=align, buff=0.12)
    box = RoundedRectangle(
        width=width,
        height=text_group.height + 0.42,
        corner_radius=0.08,
        stroke_width=2,
        stroke_color=accent,
        fill_color=PANEL,
        fill_opacity=0.88,
    )
    text_group.move_to(box).align_to(box, align).shift(RIGHT * 0.32)
    return VGroup(box, text_group)


def small_badge(text, color=GOLD):
    label = ctext(text, size=22, color=BG, weight=BOLD)
    rect = RoundedRectangle(
        width=label.width + 0.38,
        height=0.42,
        corner_radius=0.08,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )
    label.move_to(rect)
    return VGroup(rect, label)


class FibonacciBinetDerivation(Scene):
    # Keep the full rendered video close to 120 seconds while preserving the
    # relative pacing of all animations and pauses.
    TIME_SCALE = 2.794
    VOICE_SCHEDULE = (
        ("0001", 0.4),
        ("0002", 4.0),
        ("0003", 10.0),
        ("0004", 12.6),
        ("0005", 16.8),
        ("0006", 21.5),
        ("0007", 27.9),
        ("0008", 32.3),
        ("0009", 38.9),
        ("0010", 43.5),
        ("0011", 50.0),
        ("0012", 53.1),
        ("0013", 60.5),
        ("0014", 65.5),
        ("0015", 70.0),
        ("0016", 77.3),
        ("0017", 83.2),
        ("0018", 88.9),
        ("0019", 94.2),
        ("0020", 98.4),
        ("0021", 104.5),
        ("0022", 113.1),
    )

    def play(self, *animations, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 1.0) * self.TIME_SCALE
        return super().play(*animations, **kwargs)

    def wait(self, duration=1.0, stop_condition=None, frozen_frame=None):
        return super().wait(
            duration * self.TIME_SCALE,
            stop_condition=stop_condition,
            frozen_frame=frozen_frame,
        )

    def schedule_voiceovers(self):
        for prefix, start_time in self.VOICE_SCHEDULE:
            matches = sorted(VOICE_DIR.glob(f"{prefix}_*.mp3"))
            if matches:
                self.add_sound(str(matches[0]), time_offset=start_time)

    def construct(self):
        self.camera.background_color = BG
        self.schedule_voiceovers()
        self.intro()
        self.step_construct()
        self.step_roots()
        self.step_geometric()
        self.step_eliminate()
        self.summary()

    def show_header(self, step, title, color=GOLD):
        header = VGroup(
            ctext(step, size=24, color=color, weight=BOLD),
            ctext(title, size=34, color=WHITE, weight=BOLD),
        ).arrange(RIGHT, buff=0.35)
        header.to_edge(UP, buff=0.35).to_edge(LEFT, buff=0.55)
        underline = Line(header.get_left(), header.get_right(), color=color, stroke_width=4)
        underline.next_to(header, DOWN, buff=0.12)
        group = VGroup(header, underline)
        self.play(FadeIn(header, shift=DOWN * 0.18), Create(underline), run_time=0.7)
        return group

    def clear_with(self, *kept):
        kept_ids = {id(item) for item in kept}
        to_remove = [mob for mob in self.mobjects if id(mob) not in kept_ids]
        if to_remove:
            self.play(FadeOut(*to_remove, shift=DOWN * 0.15), run_time=0.45)

    def intro(self):
        title = ctext("斐波那契数列通项公式推导", size=44, color=WHITE, weight=BOLD)
        subtitle = ctext("核心想法：把二阶递推，改造成会写通项的等比数列", size=25, color=MUTED)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.22).to_edge(UP, buff=0.55)

        recurrence = mathtex(
            r"F_0=0,\quad F_1=1,\qquad F_{n+2}=F_{n+1}+F_n\quad(n\ge 0)",
            size=42,
        )
        recurrence.next_to(title_group, DOWN, buff=0.68)
        recurrence_box = SurroundingRectangle(recurrence, color=TEAL, buff=0.28, stroke_width=3)

        values = [0, 1, 1, 2, 3, 5, 8, 13]
        cells = VGroup()
        for i, value in enumerate(values):
            rect = RoundedRectangle(
                width=1.1,
                height=0.72,
                corner_radius=0.08,
                stroke_color=TEAL if i > 1 else GOLD,
                stroke_width=2,
                fill_color="#12242A",
                fill_opacity=0.82,
            )
            num = mathtex(str(value), size=32, color=WHITE)
            idx = mathtex(f"F_{{{i}}}", size=22, color=MUTED)
            idx.next_to(rect, DOWN, buff=0.12)
            num.move_to(rect)
            cells.add(VGroup(rect, num, idx))
        cells.arrange(RIGHT, buff=0.16).next_to(recurrence, DOWN, buff=0.75)

        sum_arrows = VGroup()
        for i in (3, 4, 5):
            arrow_1 = Arrow(cells[i - 2].get_top(), cells[i].get_top(), buff=0.18, stroke_width=3, color=BLUE)
            arrow_2 = Arrow(cells[i - 1].get_top(), cells[i].get_top(), buff=0.18, stroke_width=3, color=GREEN)
            sum_arrows.add(arrow_1, arrow_2)

        question = mathtex(r"F_n=?", size=54, color=GOLD).next_to(cells, DOWN, buff=0.45)
        route = teaching_card(
            ["高中数列里，等比数列最容易写通项。", "接下来要做的事：构造一个新的等比数列。"],
            accent=GOLD,
            width=9.9,
            font_size=25,
        )
        route.next_to(question, DOWN, buff=0.35)

        self.play(FadeIn(title_group, shift=DOWN * 0.25), run_time=0.8)
        self.play(Write(recurrence), Create(recurrence_box), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(cell, shift=UP * 0.2) for cell in cells], lag_ratio=0.08), run_time=1.1)
        self.play(LaggedStart(*[Create(arrow) for arrow in sum_arrows], lag_ratio=0.08), run_time=0.9)
        self.play(Write(question), question.animate.scale(1.08), run_time=0.8)
        self.play(FadeIn(route, shift=UP * 0.15), run_time=0.65)
        self.wait(0.7)
        self.clear_with()

    def step_construct(self):
        header = self.show_header("第一步", "把二阶递推变成一阶递推", TEAL)

        idea = teaching_card(
            ["先不要硬猜 Fₙ。换一个更容易的目标：", "找一个新数列 Gₙ，让它满足 Gₙ₊₁ = βGₙ。"],
            accent=TEAL,
            width=10.5,
            font_size=26,
        )
        idea.next_to(header, DOWN, buff=0.45)
        idea.set_x(0)

        g_def = mathtex(r"G_n=F_{n+1}-\alpha F_n", size=47, color=GOLD)
        g_next = mathtex(r"G_{n+1}=F_{n+2}-\alpha F_{n+1}", size=42, color=GOLD)
        g_group = VGroup(g_def, g_next).arrange(DOWN, buff=0.28)
        g_group.next_to(idea, DOWN, buff=0.45)

        target = VGroup(
            small_badge("目标", TEAL),
            mathtex(r"G_{n+1}=\beta G_n", size=44, color=TEAL),
        ).arrange(RIGHT, buff=0.25)
        target.next_to(g_group, DOWN, buff=0.38)

        construct_eq = mathtex(
            r"F_{n+2}-\alpha F_{n+1}",
            r"=",
            r"\beta\left(F_{n+1}-\alpha F_n\right)",
            size=45,
        )
        construct_eq.next_to(target, DOWN, buff=0.4)
        construct_eq[0].set_color(GOLD)
        construct_eq[2].set_color(TEAL)

        note = caption("这不是魔法：只是把 Gₙ 和 Gₙ₊₁ 代回目标式。")

        self.play(FadeIn(idea, shift=UP * 0.12), run_time=0.6)
        self.play(Write(g_def), Write(g_next), run_time=0.9)
        self.play(FadeIn(target, shift=UP * 0.12), run_time=0.6)
        self.play(TransformFromCopy(VGroup(g_group, target), construct_eq), FadeIn(note, shift=UP * 0.12), run_time=1.05)
        self.wait(0.5)
        self.clear_with(header)
        self.add(header)

        explain = teaching_card(
            ["现在把构造式展开，并与原递推比较系数。", "这是高中常用的“对应项系数相等”。"],
            accent=BLUE,
            width=10.8,
            font_size=25,
        )
        explain.next_to(header, DOWN, buff=0.45)
        explain.set_x(0)
        expanded = mathtex(
            r"F_{n+2}",
            r"=",
            r"(\alpha+\beta)F_{n+1}-\alpha\beta F_n",
            size=44,
        ).next_to(explain, DOWN, buff=0.5)
        expanded[2].set_color(BLUE)

        original = mathtex(r"F_{n+2}=1\cdot F_{n+1}+1\cdot F_n", size=39, color=WHITE)
        original.next_to(expanded, DOWN, buff=0.38)

        compare = VGroup(
            mathtex(r"\alpha+\beta=1", size=40, color=GOLD),
            mathtex(r"\alpha\beta=-1", size=40, color=GOLD),
        ).arrange(RIGHT, buff=0.85)
        compare.next_to(original, DOWN, buff=0.45)

        char_eq = mathtex(r"x^2-x-1=0", size=54, color=TEAL)
        char_label = ctext("特征方程", size=26, color=TEAL, weight=BOLD)
        char_tip = ctext("和为 1，积为 -1 的两个数，就是这个方程的两个根", size=24, color=MUTED)
        char = VGroup(char_label, char_eq, char_tip).arrange(DOWN, buff=0.14)
        char.next_to(compare, DOWN, buff=0.35)
        char_box = SurroundingRectangle(char, color=TEAL, buff=0.28, stroke_width=3)

        self.play(FadeIn(explain, shift=UP * 0.12), run_time=0.6)
        self.play(Write(expanded), run_time=0.8)
        self.play(Write(original), run_time=0.7)
        self.play(LaggedStart(*[Write(eq) for eq in compare], lag_ratio=0.18), run_time=0.9)
        self.play(FadeIn(char_label, shift=DOWN * 0.15), TransformFromCopy(compare, char_eq), FadeIn(char_tip), Create(char_box), run_time=1.0)
        self.wait(0.9)
        self.clear_with()

    def step_roots(self):
        header = self.show_header("第二步", "解出两个待定常数", GOLD)

        tip = teaching_card(
            ["到这里，问题已经变成熟悉的一元二次方程。", "用求根公式即可，不需要额外工具。"],
            accent=GOLD,
            width=10.2,
            font_size=23,
        )
        tip.next_to(header, DOWN, buff=0.34)
        tip.set_x(0)

        char_eq = mathtex(r"x^2-x-1=0", size=49, color=TEAL)
        char_eq.next_to(tip, DOWN, buff=0.3)

        formula = mathtex(r"x=\frac{1\pm\sqrt{1+4}}{2}=\frac{1\pm\sqrt5}{2}", size=36, color=WHITE)
        formula.next_to(char_eq, DOWN, buff=0.28)

        roots = VGroup(
            mathtex(r"\alpha=\frac{1+\sqrt5}{2}", size=38, color=GOLD),
            mathtex(r"\beta=\frac{1-\sqrt5}{2}", size=38, color=BLUE),
        ).arrange(RIGHT, buff=0.85)
        roots.next_to(formula, DOWN, buff=0.34)

        checks = VGroup(
            mathtex(r"\alpha+\beta=1", size=30, color=WHITE),
            mathtex(r"\alpha\beta=-1", size=30, color=WHITE),
            mathtex(r"\alpha-\beta=\sqrt5", size=30, color=WHITE),
        ).arrange(RIGHT, buff=0.55)
        checks.next_to(roots, DOWN, buff=0.28)

        phi_panel = RoundedRectangle(
            width=10.2,
            height=0.82,
            corner_radius=0.08,
            stroke_width=2,
            stroke_color=GOLD,
            fill_color="#231D10",
            fill_opacity=0.55,
        )
        phi_text = ctext("后面真正要用的是：α−β=√5", size=25, color=WHITE)
        phi_group = VGroup(phi_panel, phi_text).next_to(checks, DOWN, buff=0.28)
        phi_text.move_to(phi_panel)

        self.play(FadeIn(tip, shift=UP * 0.12), run_time=0.6)
        self.play(Write(char_eq), run_time=0.65)
        self.play(Write(formula), run_time=0.75)
        self.play(LaggedStart(*[FadeIn(root, shift=UP * 0.2) for root in roots], lag_ratio=0.18), run_time=0.9)
        self.play(LaggedStart(*[Write(check) for check in checks], lag_ratio=0.18), run_time=0.9)
        self.play(FadeIn(phi_group, shift=UP * 0.2), run_time=0.65)
        self.wait(0.9)
        self.clear_with()

    def step_geometric(self):
        header = self.show_header("第三步", "得到两个等比数列", BLUE)

        tip = teaching_card(
            ["用初值 F₀=0，F₁=1，先求出两个新数列的首项。", "首项是 1，所以等比通项会特别干净。"],
            accent=BLUE,
            width=11.0,
            font_size=25,
        )
        tip.next_to(header, DOWN, buff=0.42)
        tip.set_x(0)

        card_a = self.geometric_reason_card(
            "数列 A",
            TEAL,
            [
                r"A_n=F_{n+1}-\alpha F_n",
                r"A_{n+1}=\beta A_n",
                r"A_0=F_1-\alpha F_0=1",
                r"A_n=\beta^n",
            ],
        )
        card_b = self.geometric_reason_card(
            "数列 B",
            GOLD,
            [
                r"B_n=F_{n+1}-\beta F_n",
                r"B_{n+1}=\alpha B_n",
                r"B_0=F_1-\beta F_0=1",
                r"B_n=\alpha^n",
            ],
        )
        cards = VGroup(card_a, card_b).arrange(RIGHT, buff=0.35)
        cards.next_to(tip, DOWN, buff=0.28)

        system = mathtex(
            r"\begin{cases}"
            r"F_{n+1}-\alpha F_n=\beta^n\\[4pt]"
            r"F_{n+1}-\beta F_n=\alpha^n"
            r"\end{cases}",
            size=35,
            color=WHITE,
        )
        system.next_to(cards, DOWN, buff=0.25)
        system.shift(LEFT * 1.15)
        sys_box = SurroundingRectangle(system, color=BLUE, buff=0.28, stroke_width=3)
        sys_label = ctext("把 Aₙ、Bₙ 换回 F 的表达式", size=24, color=BLUE)
        sys_label.next_to(sys_box, RIGHT, buff=0.28)

        self.play(FadeIn(tip, shift=UP * 0.12), run_time=0.6)
        self.play(FadeIn(card_a, shift=RIGHT * 0.15), run_time=0.8)
        self.play(FadeIn(card_b, shift=LEFT * 0.15), run_time=0.8)
        self.play(FadeIn(sys_label), Write(system), Create(sys_box), run_time=1.0)
        self.wait(0.9)
        self.clear_with()

    def geometric_reason_card(self, title, color, formulas):
        title_group = VGroup(small_badge(title, color), ctext("等比数列", size=24, color=WHITE, weight=BOLD))
        title_group.arrange(RIGHT, buff=0.18)
        lines = VGroup(*[mathtex(formula, size=25 if i < 3 else 30, color=WHITE) for i, formula in enumerate(formulas)])
        lines[-1].set_color(color)
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        content = VGroup(title_group, lines).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        box = RoundedRectangle(
            width=6.05,
            height=2.8,
            corner_radius=0.08,
            stroke_color=color,
            stroke_width=2.5,
            fill_color="#111B1F",
            fill_opacity=0.9,
        )
        content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.28)
        return VGroup(box, content)

    def sequence_strip(self, entries, color, label):
        label_tex = mathtex(label, size=27, color=color)
        cells = VGroup()
        for entry in entries:
            rect = RoundedRectangle(
                width=1.05 if entry != r"\cdots" else 0.82,
                height=0.62,
                corner_radius=0.08,
                stroke_color=color,
                stroke_width=2,
                fill_color="#111B1F",
                fill_opacity=0.88,
            )
            formula = mathtex(entry, size=27, color=WHITE)
            formula.move_to(rect)
            cells.add(VGroup(rect, formula))
        cells.arrange(RIGHT, buff=0.14)
        arrow = Arrow(label_tex.get_right(), cells.get_left(), buff=0.18, color=color, stroke_width=3)
        strip = VGroup(label_tex, arrow, cells).arrange(RIGHT, buff=0.22)
        return strip

    def step_eliminate(self):
        header = self.show_header("第四步", "相减消元，求出 Fₙ", GREEN)

        tip = teaching_card(
            ["目标是 Fₙ，但方程组里还混着 Fₙ₊₁。", "两式相减，Fₙ₊₁ 正好抵消。"],
            accent=GREEN,
            width=10.3,
            font_size=25,
        )
        tip.next_to(header, DOWN, buff=0.4)
        tip.set_x(0)

        system = mathtex(
            r"\begin{cases}"
            r"F_{n+1}-\alpha F_n=\beta^n\\[4pt]"
            r"F_{n+1}-\beta F_n=\alpha^n"
            r"\end{cases}",
            size=38,
        )
        system.next_to(tip, DOWN, buff=0.34)

        subtract = mathtex(r"(\beta-\alpha)F_n=\beta^n-\alpha^n", size=40, color=TEAL)
        subtract.next_to(system, DOWN, buff=0.42)
        arrow = Arrow(system.get_bottom(), subtract.get_top(), buff=0.18, color=GREEN, stroke_width=4)
        arrow_label = ctext("两式相减", size=24, color=GREEN, weight=BOLD).next_to(arrow, RIGHT, buff=0.15)
        cancel_note = ctext("Fₙ₊₁ − Fₙ₊₁ = 0", size=22, color=MUTED)
        cancel_note.next_to(subtract, RIGHT, buff=0.45)

        relation = mathtex(r"\alpha-\beta=\sqrt5", size=35, color=GOLD)
        relation.next_to(subtract, DOWN, buff=0.35)

        solved = mathtex(r"F_n=\frac{\alpha^n-\beta^n}{\sqrt5}", size=42, color=WHITE)
        solved.next_to(relation, DOWN, buff=0.35)

        final_formula = mathtex(
            r"F_n=\frac{1}{\sqrt5}\left["
            r"\left(\frac{1+\sqrt5}{2}\right)^n"
            r"-"
            r"\left(\frac{1-\sqrt5}{2}\right)^n"
            r"\right]",
            size=37,
        )
        fit_width(final_formula, 11.4)
        final_formula.move_to(DOWN * 1.0)
        final_box = SurroundingRectangle(final_formula, color=GOLD, buff=0.28, stroke_width=4)
        label = ctext("比内公式", size=30, color=GOLD, weight=BOLD)
        label.next_to(final_box, LEFT, buff=0.28)

        self.play(FadeIn(tip, shift=UP * 0.12), run_time=0.6)
        self.play(Write(system), run_time=0.8)
        self.play(Create(arrow), FadeIn(arrow_label, shift=LEFT * 0.12), Write(subtract), FadeIn(cancel_note), run_time=0.95)
        self.play(Write(relation), run_time=0.55)
        self.play(Write(solved), run_time=0.8)
        self.wait(0.45)
        self.play(
            FadeOut(tip, system, subtract, arrow, arrow_label, cancel_note, relation, solved, shift=UP * 0.12),
            run_time=0.5,
        )
        final_tip = teaching_card(
            ["最后把 α、β 的具体值代回去。", "这就是斐波那契数列的通项公式。"],
            accent=GOLD,
            width=9.6,
            font_size=25,
        )
        final_tip.next_to(header, DOWN, buff=0.5)
        final_tip.set_x(0)
        self.play(FadeIn(final_tip, shift=UP * 0.12), run_time=0.55)
        self.play(FadeIn(label, shift=DOWN * 0.12), Write(final_formula), Create(final_box), run_time=1.15)
        self.wait(1.0)
        self.clear_with()

    def summary(self):
        title = ctext("四句话记住推导路线", size=40, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.55)

        steps = [
            ("1", "先造新数列", r"G_n=F_{n+1}-\alpha F_n", TEAL),
            ("2", "让系数对上", r"\alpha+\beta=1,\quad \alpha\beta=-1", GOLD),
            ("3", "写等比通项", r"A_n=\beta^n,\quad B_n=\alpha^n", BLUE),
            ("4", "相减消元", r"F_{n+1}-F_{n+1}=0", GREEN),
        ]

        cards = VGroup()
        for number, name, formula, color in steps:
            card = RoundedRectangle(
                width=5.8,
                height=1.65,
                corner_radius=0.08,
                stroke_color=color,
                stroke_width=2.5,
                fill_color="#121B20",
                fill_opacity=0.92,
            )
            badge = Circle(radius=0.23, color=color, fill_color=color, fill_opacity=1)
            badge_num = ctext(number, size=22, color=BG, weight=BOLD).move_to(badge)
            name_text = ctext(name, size=27, color=WHITE, weight=BOLD)
            formula_tex = mathtex(formula, size=24, color=MUTED)
            fit_width(formula_tex, 4.95)
            content = VGroup(VGroup(badge, badge_num), name_text, formula_tex)
            content.arrange(DOWN, buff=0.13)
            content.move_to(card)
            cards.add(VGroup(card, content))
        cards.arrange_in_grid(rows=2, cols=2, buff=0.32).next_to(title, DOWN, buff=0.55)

        final = mathtex(
            r"\boxed{F_n=\frac{1}{\sqrt5}\left[\left(\frac{1+\sqrt5}{2}\right)^n-\left(\frac{1-\sqrt5}{2}\right)^n\right]}",
            size=38,
            color=GOLD,
        )
        fit_width(final, 12.2)
        final.next_to(cards, DOWN, buff=0.55)

        ending = ctext("这就是从递推到通项的高中数列路线。", size=28, color=MUTED)
        ending.next_to(final, DOWN, buff=0.32)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.18) for card in cards], lag_ratio=0.16), run_time=1.2)
        self.play(Write(final), run_time=1.0)
        self.play(FadeIn(ending, shift=UP * 0.12), run_time=0.55)
        self.wait(1.2)
