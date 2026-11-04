# 矩阵的特征值与特征向量

独立的 Manim Community 项目，参考 `Affine_Trans_manim.py` 的深色背景、黄色标题、中文讲解字幕与逐步公式动画。主场景为 `EigenvaluesAndEigenvectors`，源文件为 `Eigenvalues_manim.py`。默认约 3 分 11 秒，含中文字幕；未合成人声。

## 讲解内容

1. 开场直接说“今天我们来解释什么是矩阵的特征值和特征向量”，首屏就展示矩阵 A，约 3.5 秒后开始讲它对向量的作用。
2. 对角矩阵 `A = [[2,0],[0,3]]` 把 `(x,y)` 变成 `(2x,3y)`；用单位正方形和局部网格的整体变换说明横向乘 2、纵向乘 3。前 3 幕保留同一坐标系和矩阵。
3. 分别展示 `(1,0) → (2,0)`、`(0,1) → (0,3)`，两个方向只改变长度。再用图示对比 `(1,1)` 和 `(2,3)` 的方向，说明 `(1,1)` 不是 A 的特征向量。
4. 用约 17 秒给出定义 `Av=λv, v≠0`，再用 3 个小箭头动画区分正、负、零特征值。
5. 新矩阵 `B = [[5,-1],[-1,5]]` 把 `(1,0)` 变成 `(5,-1)`、`(0,1)` 变成 `(-1,5)`，所以坐标轴不再是特征方向。再把 8 个方向同时变换，淡出偏离原直线的箭头，突出两条对角线。
6. 由 `det(B-λI)=(5-λ)²-1=(λ-4)(λ-6)=0` 求得特征值 4、6；分别解出 `x=y`、`x=-y`，选取 `(1,1)`、`(-1,1)` 作代表。
7. 动态演示 `(1,1) → (4,4)`、`(-1,1) → (-6,6)`。第 8、9、10 幕共用同一个坐标系，单位长度保持 0.5；保留第一个箭头，直接比较 4 倍和 6 倍。细灰箭头表示原向量，彩色粗箭头表示变换后向量，沿线短刻度帮助比较倍数。

坐标图占画面宽度的一半以上，右侧突出当前公式。所有坐标图的横纵轴使用相同单位长度；变换时保留固定、淡色的参考网格，并用较亮的局部网格展示空间变形。

## 渲染

本机已有环境 `D:\Software\conda\envs\manim`，无需重新安装。直接在当前目录执行：

```powershell
# 1080p / 30 fps
& 'D:\Software\conda\envs\manim\python.exe' -m manim -qh --fps 30 --disable_caching .\Eigenvalues_manim.py EigenvaluesAndEigenvectors

# 快速预览，480p / 15 fps
& 'D:\Software\conda\envs\manim\python.exe' -m manim -ql --disable_caching .\Eigenvalues_manim.py EigenvaluesAndEigenvectors
```

如果 PowerShell 允许执行本地脚本，也可使用以下入口：

```powershell
.\render.ps1
.\render.ps1 -Quality l -Preview
.\render.ps1 -Quality m
.\render.ps1 -LastFrame
.\render.ps1 -Python 'D:\your-env\Scripts\python.exe'
```

脚本始终使用 30 fps；直接执行 Manim 时 `-ql` 使用 15 fps。示例命令与脚本均重新生成动画片段，使字幕与本次成片时间轴同步。增加 `-p` 可在渲染完成后打开播放器。

高清视频输出：`media/videos/Eigenvalues_manim/1080p30/EigenvaluesAndEigenvectors.mp4`。

## 字幕与可选配音

字幕中的数学数值使用阿拉伯数字，量词表达使用“一个矩阵”；向量使用 `(x,y)`、`(2x,3y)`、`(1,0)`、`(-1,1)` 等圆括号写法。28 段旁白对应 43 条画面字幕；涉及变换的段落随动作分句切换，结果坐标在箭头到达后显示。

每次完整渲染会生成：

- `media/eigenvalues/EigenvaluesAndEigenvectors.srt`：与本次渲染实际时间轴同步的字幕。
- `media/eigenvalues/timeline.json`：章节、28 段旁白、43 条分句字幕与关键动作的实际时间。

旁白文稿在 `旁白文稿.md`，也可从源文件重新导出：

```powershell
& 'D:\Software\conda\envs\manim\python.exe' .\Eigenvalues_manim.py
```

用于 Manboo 的口语配音稿见 `Manboo配音稿.txt`；带编号和参考时长的版本见 `Manboo配音稿_分段.md`，与当前动画的 28 段字幕顺序对应。

可在本目录创建 `配音` 文件夹，按文稿编号放入 `001.mp3` 至 `028.mp3`，然后重新渲染；同编号的 WAV、M4A 也支持。音频长于默认讲解时长时，会自动延长该段画面停留时间。未提供音频的段落仍显示字幕。

中文字体为 `Microsoft YaHei`，可修改源文件中的 `CJK_FONT`。数学公式使用 LaTeX，需要 `latex` 与 `dvisvgm`；本机均已安装。为避开 Windows 中文路径问题，TeX 中间文件写入系统临时目录 `manim_eigenvalues_tex`。

在其他电脑上，请安装 Python、LaTeX 与依赖 `requirements.txt`，并把脚本的 `-Python` 参数改为对应的解释器路径。
