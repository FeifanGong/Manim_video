from manim import *
import numpy as np


class ComplexPolarConcept(Scene):
    def construct(self):
        # =====================
        # 镜头1：复平面与向量
        # =====================
        plane = ComplexPlane(
            x_range=[-1, 5, 1],
            y_range=[-1, 4, 1],
            x_length=6.5,
            y_length=5.5,
        ).add_coordinates()

        self.play(Create(plane), run_time=1.5)
        self.wait(0.5)

        # 复数 z = 3 + 2i 对应的点
        z_point = plane.coords_to_point(3, 2)

        vector_z = Arrow(
            plane.coords_to_point(0, 0),
            z_point,
            buff=0,
            color=BLUE,
            stroke_width=5,
        )
        dot_z = Dot(z_point, color=YELLOW)
        label_z = MathTex("z=3+2i").next_to(z_point, UR, buff=0.1)

        self.play(
            GrowArrow(vector_z),
            FadeIn(dot_z),
            Write(label_z),
            run_time=1.5,
        )
        self.wait(0.8)

        # =====================
        # 镜头2：投影与幅值
        # =====================
        x_proj = plane.coords_to_point(3, 0)
        y_proj = plane.coords_to_point(0, 2)

        dashed_x = DashedLine(z_point, x_proj, color=GRAY)
        dashed_y = DashedLine(z_point, y_proj, color=GRAY)

        label_3 = MathTex("3").next_to(x_proj, DOWN, buff=0.15)
        label_2 = MathTex("2").next_to(y_proj, LEFT, buff=0.15)

        self.play(
            Create(dashed_x),
            Create(dashed_y),
            FadeIn(label_3),
            FadeIn(label_2),
            run_time=1.2,
        )
        self.wait(0.5)

        # 幅值 r = √13
        r_label = MathTex(
            "r=\\sqrt{3^2+2^2}=\\sqrt{13}",
            color=YELLOW,
        ).next_to(vector_z, UP, buff=0.3)

        self.play(
            vector_z.animate.set_color(YELLOW),
            Write(r_label),
            run_time=1.2,
        )
        self.wait(1.0)

        # =====================
        # 镜头3：辐角
        # =====================
        theta = np.arctan2(2, 3)   # 约 0.588 rad

        # 弧线半径使用坐标轴单位长度
        x_unit = plane.get_x_axis().get_unit_size()
        arc_radius = 0.9 * x_unit

        arc = Arc(
            radius=arc_radius,
            start_angle=0,
            angle=theta,
            arc_center=plane.coords_to_point(0, 0),
            color=GREEN,
            stroke_width=5,
        )

        theta_label = MathTex("\\theta", color=GREEN).move_to(
            plane.coords_to_point(
                1.1 * np.cos(theta / 2),
                1.1 * np.sin(theta / 2),
            )
        )

        theta_value_label = MathTex(
            "\\approx 33.7^\\circ",
            color=GREEN,
        ).next_to(arc, RIGHT, buff=0.3)

        self.play(Create(arc), Write(theta_label), run_time=1.2)
        self.wait(0.3)
        self.play(Write(theta_value_label), run_time=0.8)
        self.wait(0.8)

        # =====================
        # 镜头4：极坐标公式
        # =====================
        formula = MathTex(
            "z",
            "=",
            "r(",
            "\\cos\\theta",
            "+",
            "i\\sin\\theta",
            ")",
            "=",
            "\\sqrt{13}(",
            "\\cos 33.7^\\circ",
            "+",
            "i\\sin 33.7^\\circ",
            ")",
        ).to_edge(DOWN, buff=0.6)

        self.play(Write(formula), run_time=1.5)
        self.wait(2)


class RotationDemo(Scene):
    def construct(self):
        # =====================
        # 镜头5：单位圆上的旋转
        # =====================
        plane = ComplexPlane(
            x_range=[-2, 2, 1],
            y_range=[-2, 2, 1],
            x_length=6.5,
            y_length=6.5,
        ).add_coordinates()

        self.play(Create(plane), run_time=1.5)
        self.wait(0.5)

        # 单位圆
        unit_circle = Circle(
            radius=plane.get_x_axis().get_unit_size(),
            arc_center=plane.coords_to_point(0, 0),
            color=GREY_A,
            stroke_width=3,
        )
        self.play(Create(unit_circle), run_time=1.0)
        self.wait(0.3)

        # 标题
        title = Text("单位圆上的旋转", font_size=36).to_corner(UL)
        self.play(Write(title), run_time=0.8)

        # 角度跟踪器
        angle = ValueTracker(0)

        def get_end_point():
            theta = angle.get_value()
            return plane.coords_to_point(np.cos(theta), np.sin(theta))

        # 旋转向量
        vec = always_redraw(
            lambda: Arrow(
                start=plane.coords_to_point(0, 0),
                end=get_end_point(),
                buff=0,
                color=BLUE,
                stroke_width=5,
            )
        )

        # 终点
        dot = always_redraw(
            lambda: Dot(get_end_point(), color=YELLOW, radius=0.06)
        )

        # 轨迹
        trace = TracedPath(
            dot.get_center,
            stroke_color=YELLOW,
            stroke_width=3,
        )

        # 实时角度显示
        theta_tex = MathTex("\\theta =").next_to(
            title, DOWN, aligned_edge=LEFT
        )

        angle_display = DecimalNumber(
            0,
            num_decimal_places=2,
            unit=" rad",
            font_size=30,
        ).next_to(theta_tex, RIGHT, buff=0.15)

        angle_display.add_updater(
            lambda m: m.set_value(angle.get_value())
        )

        # 欧拉公式
        euler_formula = MathTex(
            "e^{i\\theta}=\\cos\\theta+i\\sin\\theta",
            font_size=36,
        ).next_to(theta_tex, DOWN, aligned_edge=LEFT)

        self.add(trace, vec, dot)
        self.play(
            Write(theta_tex),
            Write(angle_display),
            Write(euler_formula),
            run_time=1.0,
        )
        self.wait(0.5)

        # 连续旋转一周，轨迹画出单位圆
        self.play(
            angle.animate.set_value(TAU),
            run_time=6,
            rate_func=linear,
        )
        self.wait(1.0)

        # =====================
        # 镜头6：复数乘法的几何意义
        # =====================
        product_formula = MathTex(
            "z_1 z_2",
            "=",
            "r_1 r_2",
            "e^{i(\\theta_1+\\theta_2)}",
            font_size=40,
        ).to_edge(DOWN, buff=0.6)

        self.play(Write(product_formula), run_time=1.5)
        self.wait(2.0)