# 反比例函数与等轴双曲线 Manim 项目

这个项目把 `inverse_function_polar_hyperbola.tex` 中的推导改编成一个 Manim 动画视频。新版使用黑底幕布风格，并使用真正的 LaTeX/MathTex 渲染数学公式。

视频主线：

1. 引入：反比例函数其实是一条等轴双曲线。
2. 给出 \(y=1/x\)，推导极坐标形式 \(r^2\sin 2\theta=2\)。
3. 顺时针旋转 \(45^\circ\)，把曲线放正。
4. 得到标准形式 \(X^2-Y^2=2\)，说明它是等轴双曲线。

渲染命令：

```powershell
.\render.ps1 -Quality medium
```

如果 PowerShell 提示脚本执行被禁用，用下面这个一次性命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\render.ps1 -Quality medium
```

输出视频位于：

```text
media/videos/reciprocal_polar_hyperbola/720p30/ReciprocalPolarHyperbola.mp4
```

说明：当前项目路径包含中文，`dvisvgm` 在中文路径下容易导致公式 SVG 转换失败。`render.ps1` 会自动把源码复制到 `D:\manim_render_reciprocal` 这个英文临时目录渲染，然后把生成的视频复制回当前项目。

检查预览拼图：

```powershell
powershell -ExecutionPolicy Bypass -File .\make_preview.ps1
```
