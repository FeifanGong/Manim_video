# 用柯西不等式证明椭圆切线方程

参考本目录 `Affine_Trans_manim.py` 的深色背景、黄色标题、中文讲解字幕和逐步公式动画。新场景独立运行，成片时长随当前配音文件自动调整。开场先画出椭圆、切点和切线，再引入柯西不等式证明的主题，最后在第 5 幕切线演示结束后收尾。

已使用现有虚拟环境 `D:\Software\conda\envs\manim`（Manim Community 0.20.1），无需重新安装。

## 渲染

本机 PowerShell 默认禁用了 `.ps1` 脚本。直接调用虚拟环境中的 Python 即可渲染，无需激活环境或修改执行策略：

```powershell
& 'D:\Software\conda\envs\manim\python.exe' -m manim -qh --fps 30 .\Cauchy_Tangent_manim.py CauchyEllipseTangent
```

将 `-qh` 改成 `-ql` 可快速预览，改成 `-qm` 可输出 720p；增加 `-p` 可在完成后打开播放器。

如果当前 PowerShell 允许执行本地脚本，也可以使用以下入口：

```powershell
# 1080p / 30 fps
.\render.ps1

# 快速预览：480p / 30 fps，完成后打开播放器
.\render.ps1 -Quality l -Preview

# 720p / 30 fps
.\render.ps1 -Quality m

# 使用其他虚拟环境
.\render.ps1 -Python 'D:\your-env\Scripts\python.exe'
```

高清视频：`media/videos/Cauchy_Tangent_manim/1080p30/CauchyEllipseTangent.mp4`。

## 内容

1. 对椭圆 $E:x^2/a^2+y^2/b^2=1$，已知 $P(x_0,y_0)\in E$，提出候选直线 $\ell:xx_0/a^2+yy_0/b^2=1$。
2. 对任意 $Q(x,y)\in E$，取单位向量 $u=(x/a,y/b)$、$v=(x_0/a,y_0/b)$。柯西给出 $(u\cdot v)^2\le1$，因此 $F(Q)=u\cdot v\le1$。
3. 动态演示：Q 在椭圆上运动，F(Q) 始终不超过 1；对径点的值是 −1，P 点的值是 1。整个椭圆位于直线 F=1 的同侧。
4. 若 Q 在候选直线上，$u\cdot v=1$。柯西取等条件给出 $u=\lambda v$；单位长度给出 $\lambda=\pm1$，而正向内积选出 $\lambda=1$，故 Q=P。
5. 同侧且只在 P 接触，证明该直线是 P 点处的切线。动态演示切点变化和四个轴端点的水平、竖直切线。

仅要求 $a,b>0$；不除以切点的坐标，也不依赖斜率存在，故四个轴端点也适用。示意图取 a=2.8、b=1.65，公式与证明保持一般形式。

## 字幕与配音

视频已接入 `配音文件` 文件夹中的 Manboo 人声。字幕中的数学量直接使用 λ、x₀、y₀、±1 等符号；适合朗读的口语文稿见 `配音文案_Manboo.txt`。源文件 `NARRATION` 保存显示字幕，也可直接导出：

```powershell
& 'D:\Software\conda\envs\manim\python.exe' .\Cauchy_Tangent_manim.py
```

当前 `配音文件` 中有 29 个音频，对应 23 段字幕。程序根据源文件中的 `MANBOO_GROUPS` 将被拆开的句子归回同一段，例如音频 0004、0005 对应第 4 段字幕，音频 0010、0011 对应第 9 段字幕。所有音频均按编号使用一次，原文件保持不变；供渲染使用的 WAV 文件生成在 `media/cauchy_tangent/voiceover/`。

各段按实际录音时长加约 0.25 秒停顿安排字幕和动画，第一句从开场图画完后的 3.6 秒开始。候选直线的证明目标和不等式上界的出现时间也会对齐相应句子。

若没有 `配音文件`，仍支持原来的 `配音/001.mp3` 到 `配音/023.mp3` 方式，以及同名 WAV、M4A 文件。无录音的段落使用默认停留时间。

每次渲染同时生成：

- `media/cauchy_tangent/CauchyEllipseTangent.srt`：与实际时间轴同步的字幕。
- `media/cauchy_tangent/timeline.json`：章节、讲解段落及起止时间。
- `media/cauchy_tangent/voiceover_manifest.json`：29 个原始音频对应的字幕段落和成片起止时间。

中文使用 `Microsoft YaHei`；如需更换字体，修改源文件中的 `CJK_FONT`。为避开 Windows 下中文路径的 LaTeX 转换问题，TeX 中间缓存保存在系统临时目录 `manim_cauchy_tangent_tex`。
