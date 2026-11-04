from manim import *
import numpy as np
from pathlib import Path
from pydub import AudioSegment
import json


# Render with the existing virtual environment (see render.ps1).
# Chinese text uses Text; formulas use ASCII-only MathTex.
CJK_FONT = "Microsoft YaHei"
ROOT = Path(__file__).resolve().parent

VOICE_LINES = [
    "今天我们来讲圆在某点的切线方程：已知这个圆，它在 P 点的切线方程是什么？",
    "设圆心为 C，半径为 r，切点为 P。",
    "P 在圆上，圆的半径为 r。",
    "连接圆心 C 和切点 P。",
    "圆的切线垂直于经过切点的半径，所以 CP 垂直于切线。",
    "现在我们在切线上任取一点 Q，连接 CQ。",
    "从 Q 向 CP 所在直线作垂线，垂足就是 P。",
    "让 Q 沿着切线移动。",
    "虽然 CQ 的长度在变，但垂足始终是 P。",
    "因此，CQ 在 CP 方向上的投影长度不变，一直等于半径 r。",
    "设向量 CQ 和向量 CP 的夹角为 θ。",
    "由直角三角形可知，CQ 乘以 θ 角的余弦，等于 CP，也就是 r。",
    "根据数量积公式，向量 CQ 与向量 CP 的内积，等于它们的长度之积，再乘以夹角的余弦。",
    "其中，CQ 乘以夹角的余弦等于 r，CP 也等于 r。",
    "所以内积等于 r 的平方。",
    "Q 与 P 重合时也成立。",
    "接下来，用坐标法计算内积。",
    "把两个向量写成坐标，对应分量相乘，再相加。",
    "令结果等于 r 的平方，就得到框中的切线方程。",
    "我们反过来验证一下：满足这个方程的点，是不是都在切线上呢？",
    "因为 P 在圆上，向量 CP 与自身的内积等于 r 的平方。",
    "两式相减，就得到向量 PQ 与向量 CP 的内积为零。",
    "这说明 Q 在过 P 且垂直于 CP 的直线上。",
    "再由勾股定理，CQ 的平方等于 r 的平方加 PQ 的平方。",
    "只有 Q 与 P 重合时，Q 才在圆上。",
    "因此，这条直线就是所求的切线。",
]


class CircleTangentProjection(Scene):
    """Prove the tangent equation using an invariant vector projection."""

    def construct(self):
        self.camera.background_color = "#10131A"
        self.current_subtitle = None
        self.voice_files = {}
        for path in (ROOT / "peiyin").glob("*.mp3"):
            number = int(path.name.split("_", 1)[0])
            if number in self.voice_files:
                raise ValueError(f"Duplicate narration number: {number}")
            self.voice_files[number] = path
        if set(self.voice_files) != set(range(1, 27)):
            raise ValueError("peiyin must contain exactly one MP3 for each number 0001 to 0026")
        self.voice_durations = {
            number: AudioSegment.from_file(path).duration_seconds
            for number, path in self.voice_files.items()
        }
        self.voice_timeline = []
        self.intro()
        self.projection_geometry()
        self.coordinate_equation()
        self.converse()
        timeline = Path(config.media_dir) / "narration_timeline.json"
        timeline.write_text(json.dumps(self.voice_timeline, ensure_ascii=False, indent=2), encoding="utf-8")

    def zh(self, text, font_size=32, color=WHITE):
        return Text(text, font=CJK_FONT, font_size=font_size, color=color)

    def math(self, tex, font_size=38, color=WHITE):
        return MathTex(tex, font_size=font_size, color=color)

    def section_title(self, text):
        return self.zh(text, 42, YELLOW).to_edge(UP, buff=0.35)

    def start_voice(self, number):
        if self.current_subtitle is not None:
            self.remove(self.current_subtitle)
        text = VOICE_LINES[number - 1]
        lines = self.wrap_subtitle(text)
        label = self.zh(lines, 25).to_edge(DOWN, buff=0.23)
        label.scale_to_fit_width(min(label.width, config.frame_width - 1))
        self.current_subtitle = VGroup(
            BackgroundRectangle(label, color=BLACK, fill_opacity=0.75, buff=0.13), label
        ).set_z_index(20)
        self.add(self.current_subtitle)
        audio = self.voice_files[number]
        self.add_sound(str(audio))
        self.voice_start_time = self.renderer.time
        self.voice_duration = self.voice_durations[number]
        self.voice_timeline.append({"number": number, "file": audio.name,
                                    "start": float(self.voice_start_time),
                                    "duration": self.voice_duration, "subtitle": text})

    def wrap_subtitle(self, text, max_chars=30):
        lines = []
        while len(text) > max_chars:
            cut = max_chars
            for i in range(max_chars - 1, 14, -1):
                if text[i] in "，。；：？":
                    cut = i + 1
                    break
            lines.append(text[:cut])
            text = text[cut:]
        return "\n".join(lines + [text])

    def finish_voice(self):
        remaining = self.voice_duration + 0.15 - (self.renderer.time - self.voice_start_time)
        if remaining > 0:
            self.wait(remaining)

    def clear_scene(self):
        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=0.7)
        self.current_subtitle = None

    def intro(self):
        self.c = np.array([-3.6, -0.25, 0.0])
        self.radius = 1.65
        self.normal = np.array([0.8, 0.6, 0.0])
        self.tangent = np.array([-0.6, 0.8, 0.0])
        self.p = self.c + self.radius * self.normal
        self.circle = Circle(radius=self.radius, color=BLUE, stroke_width=4).move_to(self.c)
        self.tangent_line = Line(self.p - 2.2 * self.tangent,
                                 self.p + 2.0 * self.tangent, color=GREEN, stroke_width=4)
        self.p_dot = Dot(self.p, color=YELLOW)
        self.p_label = self.math("P(x_0,y_0)", 27, YELLOW).next_to(
            self.p, UP + RIGHT, buff=0.24)
        title = self.section_title("圆在 P 点的切线方程是什么？")
        formula = self.math(r"(x-a)^2+(y-b)^2=r^2", 36, BLUE_B).move_to([3.2, 1.6, 0])
        question = self.zh("过 P 点的这条切线\n方程怎么求？", 34, YELLOW).move_to([3.2, 0, 0])
        self.play(Create(self.circle), Create(self.tangent_line),
                  FadeIn(self.p_dot), FadeIn(self.p_label), run_time=1.2)
        self.start_voice(1)
        self.play(FadeIn(title), Write(formula), FadeIn(question))
        self.finish_voice()
        self.play(FadeOut(title), FadeOut(formula), FadeOut(question), run_time=0.5)

    def projection_geometry(self):
        title = self.section_title("几何法：利用投影计算内积")
        # Geometry is drawn at a uniform scale so perpendicularity is preserved.
        c, p = self.c, self.p
        radius, normal, tangent = self.radius, self.normal, self.tangent
        cp = Arrow(c, p, buff=0, color=YELLOW, stroke_width=5)
        center_dot = Dot(c)
        labels = VGroup(
            self.math("C(a,b)", 27).next_to(c, DOWN + LEFT, buff=0.12),
            self.math("r", 30, YELLOW).move_to(c + 0.5 * radius * normal + UP * 0.22),
        )
        given = VGroup(
            self.math(r"(x-a)^2+(y-b)^2=r^2", 33, BLUE_B),
            self.math(r"(x_0-a)^2+(y_0-b)^2=r^2", 33, YELLOW),
        ).arrange(DOWN, buff=0.35).move_to([3.2, 1.8, 0])
        self.start_voice(2)
        self.play(FadeIn(title), FadeIn(center_dot), FadeIn(labels), Write(given))
        self.finish_voice()
        self.start_voice(3)
        self.play(Indicate(self.p_dot))
        self.finish_voice()

        corner = VMobject(color=WHITE, stroke_width=2).set_points_as_corners([
            p - 0.2 * normal, p - 0.2 * normal + 0.2 * tangent, p + 0.2 * tangent
        ])
        self.start_voice(4)
        self.play(GrowArrow(cp))
        self.finish_voice()
        self.start_voice(5)
        self.play(Create(corner))
        self.finish_voice()

        tracker = ValueTracker(1.5)
        q_pos = lambda: p + tracker.get_value() * tangent
        q = Dot(q_pos(), color=RED)
        q.add_updater(lambda mob: mob.move_to(q_pos()))
        q_label = self.math("Q(x,y)", 27, RED)
        q_label.add_updater(lambda mob: mob.next_to(q, LEFT, buff=0.15))
        cq = always_redraw(lambda: Arrow(c, q_pos(), buff=0, color=RED, stroke_width=4))
        drop = always_redraw(lambda: DashedLine(q_pos(), p, color=WHITE, stroke_width=3))
        self.start_voice(6)
        self.play(FadeIn(q), FadeIn(q_label), GrowArrow(cq))
        self.finish_voice()
        self.start_voice(7)
        self.play(Create(drop))
        self.play(Indicate(self.p_dot, color=YELLOW))
        self.finish_voice()

        projection = self.zh("CQ 在 CP 方向上的投影长度", 27).move_to([3.2, 0.5, 0])
        note = self.zh("始终等于 CP，也就是 r", 28, YELLOW).next_to(projection, DOWN, buff=0.35)
        self.start_voice(8)
        self.play(tracker.animate.set_value(-1.6), run_time=min(3, self.voice_duration))
        self.finish_voice()
        self.start_voice(9)
        self.play(tracker.animate.set_value(1.1), run_time=min(3, self.voice_duration))
        self.finish_voice()
        self.start_voice(10)
        self.play(Write(projection), FadeIn(note))
        self.finish_voice()

        angle_size = np.arctan2(tracker.get_value(), radius)
        angle_start = np.arctan2(normal[1], normal[0])
        angle = Arc(radius=0.48, start_angle=angle_start, angle=angle_size,
                    arc_center=c, color=GREEN)
        theta = self.math(r"\theta", 26, GREEN).move_to(
            c + 0.74 * np.array([np.cos(angle_start + angle_size / 2),
                                 np.sin(angle_start + angle_size / 2), 0]))
        unit = self.math(r"CQ\cos\theta=CP=r", 39, GREEN).move_to([3.2, -1.05, 0])
        self.start_voice(11)
        self.play(Create(angle), FadeIn(theta))
        self.finish_voice()
        self.start_voice(12)
        self.play(Write(unit), Indicate(cp))
        self.finish_voice()

        self.play(FadeOut(given), FadeOut(projection), FadeOut(note),
                  unit.animate.move_to([3.2, 1.8, 0]))
        product = self.math(r"\overrightarrow{CQ}\cdot\overrightarrow{CP}"
                            r"=CQ\cdot CP\cos\theta", 33).move_to([3.2, 0.6, 0])
        calculation = self.math(r"=(CQ\cos\theta)\cdot CP=r\cdot r=r^2", 33, YELLOW).move_to([3.2, -0.35, 0])
        special = self.zh("Q 与 P 重合时，数量积同样为 r²", 24).move_to([3.2, -1.3, 0])
        self.start_voice(13)
        self.play(Write(product))
        self.finish_voice()
        self.start_voice(14)
        self.play(Write(calculation))
        self.finish_voice()
        self.start_voice(15)
        self.play(Circumscribe(calculation, color=YELLOW))
        self.finish_voice()
        self.start_voice(16)
        self.play(FadeIn(special))
        self.finish_voice()
        self.clear_scene()

    def coordinate_equation(self):
        title = self.section_title("坐标法计算内积")
        equations = VGroup(
            self.math(r"\overrightarrow{CQ}\cdot\overrightarrow{CP}=r^2", 44, YELLOW),
            self.math(r"\overrightarrow{CQ}=(x-a,y-b),\quad"
                      r"\overrightarrow{CP}=(x_0-a,y_0-b)", 35, BLUE_B),
            self.math(r"(x_0-a)(x-a)+(y_0-b)(y-b)=r^2", 44, YELLOW),
        ).arrange(DOWN, buff=0.55).move_to(UP * 0.1)
        self.add(title)
        self.start_voice(17)
        self.play(Write(equations[0]))
        self.finish_voice()
        self.start_voice(18)
        self.play(Write(equations[1]))
        self.finish_voice()
        self.start_voice(19)
        self.play(Write(equations[2]))
        self.play(Create(SurroundingRectangle(equations[2], color=YELLOW, buff=0.2)))
        self.finish_voice()
        self.clear_scene()

    def converse(self):
        title = self.section_title("第三步：验证它恰好就是切线")
        rows = VGroup(
            self.math(r"\overrightarrow{CQ}\cdot\overrightarrow{CP}=r^2"
                      r"=\overrightarrow{CP}\cdot\overrightarrow{CP}", 38),
            self.math(r"(\overrightarrow{CQ}-\overrightarrow{CP})\cdot\overrightarrow{CP}=0", 38),
            self.math(r"\overrightarrow{PQ}\cdot\overrightarrow{CP}=0", 42, YELLOW),
            self.zh("轨迹是过 P 且垂直于 CP 的直线", 30, GREEN),
            self.math(r"CQ^2=CP^2+PQ^2=r^2+PQ^2\geq r^2", 38),
            self.zh("等号仅在 Q = P 时成立，因此与圆只有一个公共点", 28),
        ).arrange(DOWN, buff=0.33).move_to(UP * 0.05)
        self.add(title)
        self.start_voice(20)
        self.finish_voice()
        self.start_voice(21)
        self.play(Write(rows[0]))
        self.finish_voice()
        self.start_voice(22)
        self.play(Write(rows[1]), run_time=1.5)
        self.play(Write(rows[2]))
        self.finish_voice()
        self.start_voice(23)
        self.play(FadeIn(rows[3], shift=UP * 0.1))
        self.finish_voice()
        self.start_voice(24)
        self.play(FadeIn(rows[4], shift=UP * 0.1))
        self.finish_voice()
        self.start_voice(25)
        self.play(FadeIn(rows[5], shift=UP * 0.1))
        self.finish_voice()
        self.start_voice(26)
        self.play(Circumscribe(rows[3], color=GREEN))
        self.finish_voice()
        self.clear_scene()
