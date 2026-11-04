# Achilles and the Tortoise Manim Project

这个 Manim 项目演示“阿基里斯永远追不上乌龟”的芝诺悖论，并在动画结尾解释为什么现实中阿基里斯仍然会追上乌龟。

## 场景

- 文件：`achilles_tortoise.py`
- 场景类：`AchillesTortoiseParadox`

动画设置：

- 乌龟先跑 6 米。
- 阿基里斯速度是乌龟的 2 倍。
- 每一步都让阿基里斯跑到乌龟上一步的位置。
- 剩余距离依次变为 `3, 1.5, 0.75, ...`，看起来“永远还有一点”。
- 结论：无限阶段的时间和距离是收敛的，所以阿基里斯会在有限时间、有限距离处追上乌龟。

## 渲染命令

在包含 Manim 的虚拟环境里运行：

```powershell
manim -pql achilles_tortoise.py AchillesTortoiseParadox
```

本机已验证的虚拟环境入口：

```powershell
& "D:\Software\conda\envs\manim\Scripts\manim.exe" -pql .\achilles_tortoise.py AchillesTortoiseParadox
```

如果以后在项目内新建 `.venv`，也可以直接调用项目虚拟环境里的 `manim.exe`：

```powershell
.\.venv\Scripts\manim.exe -pql achilles_tortoise.py AchillesTortoiseParadox
```

渲染产物会输出到 `media/videos/achilles_tortoise/`。
