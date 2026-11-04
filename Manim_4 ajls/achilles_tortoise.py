from __future__ import annotations

import numpy as np

from manim import *


FONT = "Microsoft YaHei"
BACKGROUND = "#111722"
TEXT_PRIMARY = "#f6efe3"
TEXT_SECONDARY = "#c2cfda"
TRACK_COLOR = "#96a7b8"
ACHILLES_COLOR = "#7bc8ff"
ACHILLES_FILL = "#4da7e8"
ACHILLES_LABEL = "#b9e3ff"
TORTOISE_COLOR = "#b6df7a"
TORTOISE_FILL = "#77ad50"
TORTOISE_LIGHT = "#b6d98a"
TORTOISE_LABEL = "#c9f0a3"
HEAD_START_COLOR = "#f4a261"
GAP_COLOR = "#ff9a76"
CATCH_COLOR = "#ffd166"
FORMULA_COLOR = "#a8e6b2"
CONCLUSION_COLOR = "#ffc1a6"


class AchillesTortoiseParadox(Scene):
    """Animate Zeno's Achilles and the tortoise paradox."""

    def construct(self) -> None:
        self.camera.background_color = BACKGROUND

        title = Text("阿基里斯为什么“追不上”乌龟？", font=FONT, color=TEXT_PRIMARY)
        subtitle = Text(
            "芝诺悖论：每次追到乌龟刚才的位置，乌龟又向前了一小段",
            font=FONT,
            font_size=30,
            color=TEXT_SECONDARY,
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.18).to_edge(UP, buff=0.35)

        track = NumberLine(
            x_range=[0, 10, 1],
            length=10.5,
            include_numbers=True,
            font_size=24,
            decimal_number_config={"num_decimal_places": 0},
        )
        track.set_color(TRACK_COLOR)
        track.shift(DOWN * 1.15)

        achilles = self.make_achilles()
        tortoise = self.make_tortoise()
        achilles_label = Text("阿基里斯", font=FONT, font_size=26, color=ACHILLES_LABEL)
        tortoise_label = Text("乌龟", font=FONT, font_size=26, color=TORTOISE_LABEL)

        def pos_to_point(x: float, offset: float = 0.0) -> np.ndarray:
            # Values past the labeled track are compressed so later steps stay in frame.
            visible_x = min(x, 10)
            point = track.n2p(visible_x)
            if x > 10:
                point += RIGHT * ((x - 10) * 0.2)
            return point + UP * offset

        def fit_to_width(mobject: Mobject, max_width: float = 12.6) -> Mobject:
            if mobject.width > max_width:
                mobject.scale(max_width / mobject.width)
            return mobject

        achilles.move_to(pos_to_point(0, 0.58))
        tortoise.move_to(pos_to_point(6, 0.58))
        achilles_label.next_to(achilles, DOWN, buff=0.18)
        tortoise_label.next_to(tortoise, UP, buff=0.12)

        start_marker = self.label_marker("起点", ACHILLES_LABEL).next_to(track.n2p(0), DOWN, buff=0.5)
        head_start_marker = self.label_marker("乌龟先跑 6 米", TORTOISE_LABEL).next_to(
            track.n2p(6), DOWN, buff=0.5
        )
        head_start = Line(track.n2p(0), track.n2p(6), color=HEAD_START_COLOR, stroke_width=8)
        head_start.shift(DOWN * 0.38)

        self.play(Write(header))
        self.play(Create(track), FadeIn(achilles), FadeIn(tortoise))
        self.play(Write(achilles_label), Write(tortoise_label))
        achilles_label.add_updater(lambda mob: mob.next_to(achilles, DOWN, buff=0.18))
        tortoise_label.add_updater(lambda mob: mob.next_to(tortoise, UP, buff=0.12))
        self.play(Create(head_start), FadeIn(start_marker), FadeIn(head_start_marker))
        self.wait(0.8)

        setup_note = Text(
            "为了算得简单：阿基里斯每秒 2 米，乌龟每秒 1 米。",
            font=FONT,
            font_size=30,
            color=TEXT_PRIMARY,
        ).next_to(header, DOWN, buff=0.45)
        self.play(FadeIn(setup_note, shift=DOWN * 0.2))
        self.wait(0.8)

        stages = [
            (1, 0, 6, 9, "第 1 步：阿基里斯跑到 6 米，乌龟已到 9 米"),
            (2, 6, 9, 10.5, "第 2 步：阿基里斯跑到 9 米，乌龟已到 10.5 米"),
            (3, 9, 10.5, 11.25, "第 3 步：阿基里斯跑到 10.5 米，乌龟已到 11.25 米"),
            (4, 10.5, 11.25, 11.625, "再切下去：0.375、0.1875……看起来总差一点"),
        ]

        stage_text = Text(" ", font=FONT, font_size=28, color=TEXT_PRIMARY)
        stage_text.next_to(setup_note, DOWN, buff=0.35)
        gap_text = Text(" ", font=FONT, font_size=25, color=GAP_COLOR)
        gap_text.next_to(stage_text, DOWN, buff=0.22)

        self.play(FadeIn(stage_text), FadeIn(gap_text))

        gap_lines = VGroup()
        path_lines = VGroup()
        current_achilles_x = 0.0
        current_tortoise_x = 6.0

        for _index, _old_achilles_x, target_x, new_tortoise_x, caption in stages:
            target_point = pos_to_point(target_x, 0.58)
            tortoise_point = pos_to_point(new_tortoise_x, 0.58)

            new_stage_text = Text(caption, font=FONT, font_size=28, color=TEXT_PRIMARY)
            fit_to_width(new_stage_text)
            new_stage_text.next_to(setup_note, DOWN, buff=0.35)

            gap = new_tortoise_x - target_x
            new_gap_text = Text(
                f"剩余差距：{gap:g} 米",
                font=FONT,
                font_size=25,
                color=GAP_COLOR,
            )
            new_gap_text.next_to(new_stage_text, DOWN, buff=0.22)

            achilles_path = Line(
                pos_to_point(current_achilles_x, 0.58),
                target_point,
                color=ACHILLES_COLOR,
                stroke_width=6,
            )
            tortoise_path = Line(
                pos_to_point(current_tortoise_x, 0.58),
                tortoise_point,
                color=TORTOISE_COLOR,
                stroke_width=5,
            )
            path_lines.add(achilles_path, tortoise_path)

            self.play(
                ReplacementTransform(stage_text, new_stage_text),
                ReplacementTransform(gap_text, new_gap_text),
                run_time=0.5,
            )
            stage_text = new_stage_text
            gap_text = new_gap_text

            self.play(Create(achilles_path), achilles.animate.move_to(target_point), run_time=1.05)
            self.play(Create(tortoise_path), tortoise.animate.move_to(tortoise_point), run_time=0.75)

            gap_line = DashedLine(
                target_point + DOWN * 0.28,
                tortoise_point + DOWN * 0.28,
                color=GAP_COLOR,
                stroke_width=4,
            )
            gap_label = Text(f"{gap:g}", font=FONT, font_size=22, color=GAP_COLOR)
            gap_label.next_to(gap_line, DOWN, buff=0.12)
            gap_lines.add(gap_line, gap_label)
            self.play(Create(gap_line), FadeIn(gap_label), run_time=0.45)
            self.wait(0.35)

            current_achilles_x = target_x
            current_tortoise_x = new_tortoise_x

        real_time_text = Text(
            "换个看法：不要把路程切碎，让他们按真实时间一直跑。",
            font=FONT,
            font_size=28,
            color=TEXT_PRIMARY,
        )
        fit_to_width(real_time_text)
        real_time_text.next_to(setup_note, DOWN, buff=0.35)

        catch_point = pos_to_point(12, 0)
        catch_line = DashedLine(
            catch_point + DOWN * 0.45,
            catch_point + UP * 1.18,
            color=CATCH_COLOR,
            stroke_width=4,
        )
        catch_marker = self.label_marker("追上点：12 米", CATCH_COLOR)
        catch_marker.next_to(catch_point, DOWN, buff=0.5)
        catch_note = Text(
            "6 秒后，他们站在同一条 12 米竖线上：现实中已经追上。",
            font=FONT,
            font_size=26,
            color=CONCLUSION_COLOR,
        )
        fit_to_width(catch_note, 12.0)
        catch_note.next_to(real_time_text, DOWN, buff=0.22)

        self.play(
            ReplacementTransform(stage_text, real_time_text),
            FadeOut(gap_text),
            FadeOut(gap_lines),
            FadeOut(path_lines),
            run_time=0.6,
        )
        stage_text = real_time_text
        self.play(Create(catch_line), FadeIn(catch_marker), run_time=0.6)
        self.play(
            achilles.animate.move_to(pos_to_point(12, 0.42)),
            tortoise.animate.move_to(pos_to_point(12, 0.98)),
            run_time=1.5,
            rate_func=smooth,
        )
        self.play(FadeIn(catch_note, shift=UP * 0.12), run_time=0.5)
        self.wait(0.9)

        explanation = VGroup(
            Text("悖论的关键：把追赶拆成无限多个阶段。", font=FONT, font_size=30, color=TEXT_PRIMARY),
            Text("每个阶段都是真的：追到旧位置时，乌龟又前进了。", font=FONT, font_size=28, color=TEXT_SECONDARY),
            Text("但无限多个阶段的总时间可以是有限的。", font=FONT, font_size=28, color=TEXT_SECONDARY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        formula = VGroup(
            Text("时间：3 + 1.5 + 0.75 + ... = 6 秒", font=FONT, font_size=30, color=FORMULA_COLOR),
            Text("距离：6 + 3 + 1.5 + ... = 12 米", font=FONT, font_size=30, color=FORMULA_COLOR),
            Text("所以现实中阿基里斯会在 12 米处追上乌龟。", font=FONT, font_size=30, color=TEXT_PRIMARY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        final_notes = VGroup(explanation, formula).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        fit_to_width(final_notes, 12.2)
        final_notes.next_to(header, DOWN, buff=0.5)

        achilles_label.clear_updaters()
        tortoise_label.clear_updaters()
        self.play(
            FadeOut(head_start),
            FadeOut(start_marker),
            FadeOut(head_start_marker),
            FadeOut(setup_note),
            FadeOut(stage_text),
            FadeOut(catch_note),
            FadeOut(catch_line),
            FadeOut(catch_marker),
            FadeOut(track),
            FadeOut(achilles),
            FadeOut(tortoise),
            FadeOut(achilles_label),
            FadeOut(tortoise_label),
        )
        self.play(FadeIn(final_notes, shift=UP * 0.15))
        self.wait(1.2)

        conclusion = VGroup(
            Text("“永远追不上”只发生在这种无限分割的叙述里；", font=FONT, font_size=28, color=CONCLUSION_COLOR),
            Text("数学求和后，追上时间是有限的。", font=FONT, font_size=28, color=CONCLUSION_COLOR),
        ).arrange(DOWN, buff=0.1)
        fit_to_width(conclusion, 12.2)
        conclusion.to_edge(DOWN, buff=0.45)
        self.play(Write(conclusion))
        self.wait(2)

    def make_achilles(self) -> VGroup:
        skin = "#f6c98d"
        tunic = ACHILLES_FILL
        outline = ACHILLES_COLOR
        gold = CATCH_COLOR
        sandal = "#d69b6a"

        cape = Polygon(
            LEFT * 0.16 + UP * 0.16,
            LEFT * 0.52 + UP * 0.02,
            LEFT * 0.34 + DOWN * 0.28,
            LEFT * 0.08 + DOWN * 0.16,
            color="#ffb3a0",
            fill_color="#d85f57",
            fill_opacity=0.92,
            stroke_width=2,
        )
        body = Polygon(
            LEFT * 0.18 + UP * 0.18,
            RIGHT * 0.18 + UP * 0.18,
            RIGHT * 0.14 + DOWN * 0.2,
            LEFT * 0.14 + DOWN * 0.2,
            color=outline,
            fill_color=tunic,
            fill_opacity=1,
            stroke_width=3,
        )
        belt = Line(LEFT * 0.15 + DOWN * 0.02, RIGHT * 0.15 + DOWN * 0.02, color=gold, stroke_width=4)
        head = Circle(radius=0.14, color="#ffe0b5", fill_color=skin, fill_opacity=1, stroke_width=2)
        head.shift(UP * 0.42)
        hair = ArcBetweenPoints(
            head.get_left() + UP * 0.04,
            head.get_right() + UP * 0.04,
            angle=-PI / 2,
            color="#f0a14e",
            stroke_width=5,
        )
        eye = Dot(head.get_center() + RIGHT * 0.05 + UP * 0.02, radius=0.012, color=BACKGROUND)

        arm_back = Line(LEFT * 0.12 + UP * 0.1, LEFT * 0.4 + DOWN * 0.04, color=skin, stroke_width=6)
        arm_front = Line(RIGHT * 0.12 + UP * 0.08, RIGHT * 0.38 + UP * 0.22, color=skin, stroke_width=6)
        wrist = Dot(RIGHT * 0.41 + UP * 0.23, radius=0.035, color=skin)

        leg_back = Line(LEFT * 0.08 + DOWN * 0.18, LEFT * 0.34 + DOWN * 0.5, color=skin, stroke_width=7)
        leg_front = Line(RIGHT * 0.08 + DOWN * 0.18, RIGHT * 0.36 + DOWN * 0.43, color=skin, stroke_width=7)
        back_foot = Line(LEFT * 0.34 + DOWN * 0.5, LEFT * 0.52 + DOWN * 0.49, color=sandal, stroke_width=5)
        front_foot = Line(RIGHT * 0.36 + DOWN * 0.43, RIGHT * 0.58 + DOWN * 0.43, color=sandal, stroke_width=5)

        return VGroup(
            cape,
            arm_back,
            leg_back,
            back_foot,
            body,
            belt,
            leg_front,
            front_foot,
            arm_front,
            wrist,
            head,
            hair,
            eye,
        )

    def make_tortoise(self) -> VGroup:
        shell = Ellipse(
            width=0.78,
            height=0.46,
            color=TORTOISE_COLOR,
            fill_color=TORTOISE_FILL,
            fill_opacity=1,
            stroke_width=3,
        )
        shell_rim = Ellipse(width=0.62, height=0.32, color=CATCH_COLOR, stroke_width=2)
        shell_rib = Line(LEFT * 0.26, RIGHT * 0.26, color=CATCH_COLOR, stroke_width=2)
        shell_cut_1 = Line(LEFT * 0.08 + UP * 0.16, LEFT * 0.08 + DOWN * 0.16, color=CATCH_COLOR, stroke_width=2)
        shell_cut_2 = Line(RIGHT * 0.08 + UP * 0.16, RIGHT * 0.08 + DOWN * 0.16, color=CATCH_COLOR, stroke_width=2)

        head = Ellipse(
            width=0.25,
            height=0.2,
            color=TORTOISE_COLOR,
            fill_color=TORTOISE_LIGHT,
            fill_opacity=1,
            stroke_width=3,
        )
        head.next_to(shell, RIGHT, buff=-0.03)
        eye = Dot(head.get_center() + RIGHT * 0.04 + UP * 0.04, radius=0.018, color=BACKGROUND)
        smile = ArcBetweenPoints(
            head.get_center() + RIGHT * 0.02 + DOWN * 0.02,
            head.get_center() + RIGHT * 0.1 + DOWN * 0.02,
            angle=PI / 3,
            color="#3d6b2d",
            stroke_width=2,
        )
        tail = Triangle(color=TORTOISE_COLOR, fill_color=TORTOISE_LIGHT, fill_opacity=1, stroke_width=2)
        tail.scale(0.08).rotate(PI / 2)
        tail.next_to(shell, LEFT, buff=-0.02)
        legs = VGroup(
            Ellipse(width=0.15, height=0.09, color=TORTOISE_COLOR, fill_color=TORTOISE_LIGHT, fill_opacity=1)
            .move_to(shell.get_corner(DL) + RIGHT * 0.12 + DOWN * 0.02)
            .rotate(-PI / 8),
            Ellipse(width=0.15, height=0.09, color=TORTOISE_COLOR, fill_color=TORTOISE_LIGHT, fill_opacity=1)
            .move_to(shell.get_corner(DR) + LEFT * 0.12 + DOWN * 0.02)
            .rotate(PI / 8),
            Ellipse(width=0.15, height=0.09, color=TORTOISE_COLOR, fill_color=TORTOISE_LIGHT, fill_opacity=1)
            .move_to(shell.get_corner(UL) + RIGHT * 0.12 + UP * 0.02)
            .rotate(PI / 8),
            Ellipse(width=0.15, height=0.09, color=TORTOISE_COLOR, fill_color=TORTOISE_LIGHT, fill_opacity=1)
            .move_to(shell.get_corner(UR) + LEFT * 0.12 + UP * 0.02)
            .rotate(-PI / 8),
        )
        return VGroup(tail, legs, shell, shell_rim, shell_rib, shell_cut_1, shell_cut_2, head, eye, smile)

    def label_marker(self, text: str, color: str) -> VGroup:
        marker = Triangle(color=color, fill_color=color, fill_opacity=1).scale(0.14).rotate(PI)
        label = Text(text, font=FONT, font_size=22, color=color)
        return VGroup(marker, label).arrange(DOWN, buff=0.08)
