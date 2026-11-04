# -*- coding: utf-8 -*-
from math import sqrt
from pathlib import Path
import shutil
import subprocess
import sys

from manim import *


FONT = "Microsoft YaHei"
BG = "#0f172a"
BLUE = "#60a5fa"
GREEN = "#34d399"
YELLOW = "#fbbf24"
RED = "#fb7185"
MUTED = "#94a3b8"
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}


class SymmetricSubstitutionMax(Scene):
    def text(self, content, size=34, color=WHITE, weight="NORMAL"):
        return Text(content, font=FONT, font_size=size, color=color, weight=weight)

    def construct(self):
        self.camera.background_color = BG
        self.load_voiceovers()

        self.opening()
        self.direct_substitution()
        self.symmetric_substitution()
        self.simplify_expression()
        self.maximize_in_u()
        self.final_answer()

    def ffprobe_path(self):
        found = shutil.which("ffprobe") or shutil.which("ffprobe.exe")
        if found:
            return found

        env_ffprobe = (
            Path(sys.executable).resolve().parent
            / "Library"
            / "bin"
            / "ffprobe.exe"
        )
        if env_ffprobe.exists():
            return str(env_ffprobe)

        raise FileNotFoundError("未找到 ffprobe，无法读取配音时长。")

    def audio_duration(self, path):
        result = subprocess.run(
            [
                self.ffprobe_path(),
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return float(result.stdout.strip().splitlines()[0])

    def load_voiceovers(self):
        voice_dir = Path(__file__).resolve().parent / "配音"
        if not voice_dir.exists():
            raise FileNotFoundError(f"未找到配音文件夹：{voice_dir}")

        voice_files = sorted(
            path
            for path in voice_dir.iterdir()
            if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
        )
        if not voice_files:
            raise FileNotFoundError(f"配音文件夹里没有可用音频：{voice_dir}")

        self.voiceovers = [(path, self.audio_duration(path)) for path in voice_files]
        self.voice_index = 0

    def narrate(self, *animations, run_time=None):
        if self.voice_index >= len(self.voiceovers):
            raise IndexError("配音条数不足，当前动画还需要更多音频。")

        path, duration = self.voiceovers[self.voice_index]
        self.voice_index += 1

        start_time = self.time
        self.add_sound(str(path))

        if animations:
            animation_time = run_time
            if animation_time is None:
                animation_time = min(1.0, max(0.25, duration - 0.12))
            else:
                animation_time = min(animation_time, max(0.25, duration - 0.12))
            self.play(*animations, run_time=animation_time)

        remaining = duration - (self.time - start_time)
        if remaining > 0:
            self.wait(remaining)

    def transition_out(self, *mobjects):
        self.play(*[FadeOut(mob) for mob in mobjects], run_time=0.35)

    def opening(self):
        title = self.text("我们来看一道求最值的题目", 44, YELLOW, "BOLD").to_edge(UP)
        condition = MathTex(r"x+y=2", font_size=56, color=BLUE)
        target = MathTex(
            r"S=\frac{1}{1+x^2}+\frac{1}{1+y^2}",
            font_size=52,
            color=WHITE,
        )
        question = self.text("在这个条件下，S 的最大值是多少？", 32, color=WHITE)

        group = VGroup(condition, target, question).arrange(DOWN, buff=0.5).move_to(ORIGIN)
        box = SurroundingRectangle(target, color=YELLOW, buff=0.2)

        self.narrate(Write(title))
        self.narrate(Write(condition), Write(target), Create(box), FadeIn(question, shift=UP * 0.15))
        self.transition_out(group, box, title)

    def direct_substitution(self):
        title = self.text("第一反应：把 y 换成 2-x", 38, YELLOW, "BOLD").to_edge(UP)
        sub = MathTex(r"y=2-x", font_size=54, color=BLUE).shift(UP * 1.5)
        expr = MathTex(
            r"S=\frac{1}{1+x^2}+\frac{1}{1+(2-x)^2}",
            font_size=46,
            color=WHITE,
        ).next_to(sub, DOWN, buff=0.5)
        expanded = MathTex(
            r"S=\frac{1}{1+x^2}+\frac{1}{x^2-4x+5}",
            font_size=43,
            color=WHITE,
        ).next_to(expr, DOWN, buff=0.5)
        ok_note = self.text("这个想法没有问题。", 30, GREEN).next_to(expanded, DOWN, buff=0.55)
        hard_note = self.text("继续展开，后面会越来越不好算。", 30, MUTED).move_to(ok_note)
        why = self.text("为什么会这样？", 32, YELLOW, "BOLD").move_to(ok_note)
        symmetry_note = self.text("因为直接消元，破坏了题目原本的对称性。", 29, RED).move_to(ok_note)
        symmetry_question = self.text("有没有换元方法，可以保留这种对称性？", 30, YELLOW).move_to(ok_note)

        self.narrate(Write(title), Write(sub))
        self.narrate(FadeIn(ok_note, shift=UP * 0.1))
        self.narrate(Write(expr))
        self.narrate(ReplacementTransform(expr.copy(), expanded), ReplacementTransform(ok_note, hard_note))
        self.narrate(ReplacementTransform(hard_note, why))
        self.narrate(ReplacementTransform(why, symmetry_note))
        self.narrate(ReplacementTransform(symmetry_note, symmetry_question))
        self.transition_out(title, sub, expr, expanded, symmetry_question)

    def symmetric_substitution(self):
        answer = self.text("有的，兄弟，有的。", 42, GREEN, "BOLD").move_to(ORIGIN)
        title = self.text("看见 x+y=2，就看见中心 1", 38, YELLOW, "BOLD").to_edge(UP)
        line = NumberLine(
            x_range=[-1, 3, 1],
            length=8,
            color=MUTED,
            include_numbers=True,
            font_size=28,
        ).shift(DOWN * 0.2)
        center_dot = Dot(line.n2p(1), color=YELLOW)
        center_label = self.text("中心", 26, YELLOW).next_to(center_dot, UP)

        left_dot = Dot(line.n2p(0.25), color=GREEN)
        right_dot = Dot(line.n2p(1.75), color=GREEN)
        left_label = MathTex(r"x=1-t", font_size=34, color=GREEN).next_to(left_dot, DOWN, buff=0.45)
        right_label = MathTex(r"y=1+t", font_size=34, color=GREEN).next_to(right_dot, DOWN, buff=0.45)
        brace_left = DoubleArrow(line.n2p(0.25), line.n2p(1), buff=0.05, color=GREEN)
        brace_right = DoubleArrow(line.n2p(1), line.n2p(1.75), buff=0.05, color=GREEN)
        t_left = MathTex(r"t", font_size=32, color=GREEN).next_to(brace_left, UP)
        t_right = MathTex(r"t", font_size=32, color=GREEN).next_to(brace_right, UP)

        sub = MathTex(r"x=1-t,\qquad y=1+t", font_size=50, color=WHITE).to_edge(DOWN)
        check = MathTex(
            r"(1-t)+(1+t)=2",
            font_size=44,
            color=BLUE,
        ).next_to(sub, UP, buff=0.55)

        self.narrate(FadeIn(answer, scale=1.05))
        self.narrate(ReplacementTransform(answer, title), Create(line), FadeIn(center_dot), FadeIn(center_label))
        self.narrate(
            FadeIn(left_dot),
            FadeIn(right_dot),
            GrowArrow(brace_left),
            GrowArrow(brace_right),
            Write(t_left),
            Write(t_right),
        )
        self.narrate(Write(left_label), Write(right_label), Write(sub))
        self.narrate(Write(check))
        self.narrate(Indicate(center_dot), Indicate(left_label), Indicate(right_label))
        self.transition_out(
            title,
            line,
            center_dot,
            center_label,
            left_dot,
            right_dot,
            left_label,
            right_label,
            brace_left,
            brace_right,
            t_left,
            t_right,
            sub,
            check,
        )

    def simplify_expression(self):
        title = self.text("把对称性保留下来", 38, YELLOW, "BOLD").to_edge(UP)
        step1 = MathTex(
            r"S=\frac{1}{1+(1-t)^2}+\frac{1}{1+(1+t)^2}",
            font_size=42,
            color=WHITE,
        )
        step2 = MathTex(
            r"S=\frac{1}{t^2-2t+2}+\frac{1}{t^2+2t+2}",
            font_size=42,
            color=WHITE,
        )
        step3 = MathTex(
            r"S=\frac{2(t^2+2)}{(t^2+2)^2-4t^2}",
            font_size=48,
            color=GREEN,
        )
        note = self.text("一次项 +2t 和 -2t 成对出现，通分后会抵消。", 30, MUTED)

        group = VGroup(step1, step2, step3, note).arrange(DOWN, buff=0.5).move_to(ORIGIN)

        self.narrate(Write(title))
        self.narrate(Write(step1))
        self.narrate(TransformMatchingTex(step1.copy(), step2))
        self.narrate(FadeIn(note, shift=UP * 0.1))
        self.narrate(TransformMatchingTex(step2.copy(), step3), Indicate(note))
        self.transition_out(title, group)

    def maximize_in_u(self):
        title = self.text("继续换元", 38, YELLOW, "BOLD").to_edge(UP)
        reciprocal_title = self.text("倒过来：求 1/S 的最小值", 38, YELLOW, "BOLD").to_edge(UP)
        sub = MathTex(r"u=t^2+2,\qquad u\ge 2", font_size=44, color=BLUE)
        range_note = self.text("因为 t²≥0，所以这里不是任意实数，而是 u≥2。", 25, MUTED)
        f = MathTex(
            r"S=\frac{2u}{u^2-4u+8}",
            font_size=48,
            color=WHITE,
        )
        reciprocal1 = MathTex(
            r"\frac{1}{S}=\frac{u^2-4u+8}{2u}",
            font_size=38,
            color=WHITE,
        )
        reciprocal2 = MathTex(
            r"=\frac{1}{2}\left(u+\frac{8}{u}-4\right)",
            font_size=38,
            color=WHITE,
        )
        reciprocal = VGroup(reciprocal1, reciprocal2).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        hook = VGroup(
            self.text("先看对勾函数", 25, MUTED),
            MathTex(r"u+\frac{8}{u}", font_size=30, color=YELLOW),
        ).arrange(RIGHT, buff=0.12)
        root_eq = MathTex(
            r"u=\frac{8}{u}",
            font_size=40,
            color=GREEN,
        )
        root_sol = MathTex(
            r"\Rightarrow\quad u=2\sqrt2",
            font_size=40,
            color=GREEN,
        )
        root = VGroup(root_eq, root_sol).arrange(RIGHT, buff=0.18)
        attainable = self.text("2√2 ≥ 2，所以这个最小值可以取到。", 25, MUTED)
        hook_min = MathTex(
            r"\left(u+\frac{8}{u}\right)_{\min}=4\sqrt2",
            font_size=38,
            color=GREEN,
        )
        min_value = MathTex(
            r"\left(\frac{1}{S}\right)_{\min}"
            r"=\frac{1}{2}(4\sqrt2-4)=2\sqrt2-2",
            font_size=36,
            color=GREEN,
        )

        left_group = VGroup(
            sub,
            range_note,
            f,
            reciprocal,
            hook,
            root,
            attainable,
            hook_min,
            min_value,
        ).arrange(DOWN, buff=0.16).scale(0.72)
        left_group.to_edge(LEFT, buff=0.38).shift(DOWN * 0.38)

        axes = Axes(
            x_range=[-6, 7, 2],
            y_range=[-10, 12, 5],
            x_length=5.4,
            y_length=3.8,
            tips=False,
            axis_config={"color": MUTED, "stroke_width": 2, "include_numbers": True},
            x_axis_config={
                "numbers_to_include": [-6, -4, -2, 0, 2, 4, 6],
                "font_size": 20,
                "decimal_number_config": {"num_decimal_places": 0},
            },
            y_axis_config={
                "numbers_to_include": [-10, -5, 0, 5, 10],
                "font_size": 20,
                "decimal_number_config": {"num_decimal_places": 0},
            },
        )
        axes.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.2)
        labels = axes.get_axis_labels(
            MathTex("u", font_size=28, color=MUTED),
            MathTex(r"v=u+\frac{8}{u}", font_size=28, color=MUTED),
        )
        left_branch = axes.plot(lambda u: u + 8 / u, x_range=[-6, -0.85], color=BLUE)
        right_branch = axes.plot(lambda u: u + 8 / u, x_range=[0.85, 7], color=YELLOW)
        asymptote = DashedLine(axes.c2p(0, -10), axes.c2p(0, 12), color=RED, stroke_width=2)
        asymptote_label = VGroup(
            MathTex(r"u=0", font_size=24, color=RED),
            self.text("不取", 20, RED),
        ).arrange(RIGHT, buff=0.08).next_to(axes.c2p(0, 10), RIGHT, buff=0.12)
        u_star = 2 * sqrt(2)
        hook_min_y = 4 * sqrt(2)
        dot = Dot(axes.c2p(u_star, hook_min_y), color=RED)
        guide_v = DashedLine(axes.c2p(u_star, 0), axes.c2p(u_star, hook_min_y), color=RED)
        guide_h = DashedLine(axes.c2p(0, hook_min_y), axes.c2p(u_star, hook_min_y), color=RED)
        max_label = MathTex(r"\min", font_size=32, color=RED).next_to(dot, DOWN, buff=0.1)
        graph_note = VGroup(
            self.text("先找到", 25, YELLOW),
            MathTex(r"u+\frac{8}{u}", font_size=32, color=YELLOW),
            self.text("的最小值", 25, YELLOW),
        ).arrange(RIGHT, buff=0.12).next_to(axes, DOWN, buff=0.25)

        self.narrate(Write(title))
        self.narrate(Write(sub))
        self.narrate(FadeIn(range_note, shift=UP * 0.1))
        self.narrate(Indicate(sub), Indicate(range_note))
        self.narrate(Write(f))
        self.narrate(Indicate(f))
        self.narrate(Indicate(f, color=RED))
        self.narrate(ReplacementTransform(title, reciprocal_title))
        self.narrate(Write(reciprocal1))
        self.narrate(Write(reciprocal2))
        self.narrate(
            FadeIn(hook, shift=UP * 0.1),
            Create(axes),
            Write(labels),
            Create(asymptote),
            Write(asymptote_label),
        )
        self.narrate(Create(left_branch), Create(right_branch))
        self.narrate(Create(guide_v), Create(guide_h), FadeIn(dot), Write(max_label), FadeIn(graph_note))
        self.narrate(Write(root_eq))
        self.narrate(Write(root_sol))
        self.narrate(FadeIn(attainable, shift=UP * 0.1))
        self.narrate(Write(hook_min))
        self.narrate(Indicate(reciprocal))
        self.narrate(Write(min_value))
        self.narrate(Indicate(min_value), Indicate(reciprocal_title))
        self.transition_out(
            reciprocal_title,
            left_group,
            axes,
            labels,
            left_branch,
            right_branch,
            asymptote,
            asymptote_label,
            dot,
            guide_v,
            guide_h,
            max_label,
            graph_note,
        )

    def final_answer(self):
        title = self.text("倒过来，得到 S 的最大值", 38, YELLOW, "BOLD").to_edge(UP)
        value = MathTex(
            r"S_{\max}=\frac{1}{2\sqrt2-2}=\frac{1+\sqrt2}{2}",
            font_size=54,
            color=GREEN,
        )
        summary1 = self.text("关键不是急着消元。", 32, YELLOW, "BOLD")
        summary2 = self.text("而是先看出 x、y 关于 1 对称。", 32, WHITE)
        summary3 = self.text("把对称性保留下来，后面的计算就更加容易。", 32, YELLOW, "BOLD")

        group = VGroup(value, summary1, summary2, summary3).arrange(DOWN, buff=0.5).move_to(ORIGIN)
        box = SurroundingRectangle(value, color=GREEN, buff=0.24)

        self.narrate(Write(title))
        self.narrate(Write(value), Create(box))
        self.narrate(FadeIn(summary1, shift=UP * 0.15))
        self.narrate(FadeIn(summary2, shift=UP * 0.15))
        self.narrate(FadeIn(summary3, shift=UP * 0.15))
