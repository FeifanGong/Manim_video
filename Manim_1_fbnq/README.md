# Fibonacci Binet Formula Animation

这个 Manim 项目把 `fbnq.tex` 中“用高中数列方法推导斐波那契数列通项公式”的内容改写成动画。

## Render

当前机器的 Manim 在 Conda 环境 `manim` 中：

```powershell
& "D:\Software\conda\envs\manim\Scripts\manim.exe" -pql fib_binet_scene.py FibonacciBinetDerivation
```

已经生成的 720p30 成品在：

```text
media/videos/fib_binet_scene/720p30/FibonacciBinetDerivation.mp4
```

重新导出 720p30：

```powershell
& "D:\Software\conda\envs\manim\Scripts\manim.exe" -qm fib_binet_scene.py FibonacciBinetDerivation
```

高清导出可以改用：

```powershell
& "D:\Software\conda\envs\manim\Scripts\manim.exe" -pqh fib_binet_scene.py FibonacciBinetDerivation
```

输出视频会生成在 `media/videos/fib_binet_scene/` 下。
