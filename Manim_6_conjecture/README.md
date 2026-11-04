# 函数的奇偶拆分与双曲函数

参考当前目录 `Affine_Trans_manim.py`，沿用深色背景、微软雅黑、黄色章节标题、MathTex 公式、分段动画和底部字幕。参考文件保持原样。

主文件：`Odd_Even_manim.py`。完整场景：`OddEvenDecomposition`。

## 内容

1. 开篇直接提出：任何定义域关于原点对称的实值函数，都能拆成奇函数与偶函数之和。
2. 明确前提 `x ∈ D ⇔ -x ∈ D`；先假设 `f(x)=O(x)+E(x)`，其中 O 为奇函数、E 为偶函数。代入 -x 得到 `f(-x)=-O(x)+E(x)`，两式相减解出 `O(x)=[f(x)-f(-x)]/2`，两式相加解出 `E(x)=[f(x)+f(-x)]/2`；最后确认公式确实满足奇偶性及相加还原。
3. 展示 `e^x` 及其关于 y 轴的镜像 `e^(-x)`，引出 `sinh x` 和 `cosh x` 的定义及 `e^x = sinh x + cosh x`。
4. 并排绘制 sinh、cosh 图像，成对移动对称点；再在同一坐标系动态演示纵坐标相加。负 x 时也演示有向线段的相加。
5. 定义 `tanh x = sinh x / cosh x`，说明分母始终为正，证明 tanh 是奇函数，绘制图像并展示原点对称及两条渐近线。

## 渲染

使用已找到的虚拟环境 `D:\Software\conda\envs\manim`，无需重新安装。
在本目录的 PowerShell 中执行：

```powershell
# 480p 快速预览
.\render.ps1 -Quality l

# 1080p / 60 fps 完整视频（默认）
.\render.ps1

# 4K / 60 fps
.\render.ps1 -Quality k

# 渲染后打开播放器
.\render.ps1 -Quality m -Preview

# 单独渲染证明或例子
.\render.ps1 -Quality l -Scene DecompositionProof
.\render.ps1 -Quality l -Scene HyperbolicFunctions

# 使用另一个虚拟环境
.\render.ps1 -Python 'D:\your-env\Scripts\python.exe'
```

视频输出：`media/videos/Odd_Even_manim/<质量目录>/<场景名>.mp4`。
默认成片路径：`media/videos/Odd_Even_manim/1080p60/OddEvenDecomposition.mp4`。
本次配音完整版另存为 `media/videos/Odd_Even_manim/1080p60/OddEvenDecomposition_voiced.mp4`，方便直接辨认。
脚本临时补齐虚拟环境 PATH，并将 TeX 缓存放入系统临时目录中的英文路径，避免中文路径导致的公式转换问题。

如果系统提示禁止运行脚本，用以下命令；执行策略参数只作用于这次进程，不修改系统设置：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\render.ps1 -Quality l
```

## 字幕与可选配音

当前项目已接入 `peiyin` 文件夹中的 41 条 Manboo 配音。渲染时优先使用这些音频，按编号和句首与 24 个画面段落匹配。
`tools/prepare_voiceover.py` 自动生成 `media/voiceover/01.wav` 至 `24.wav` 以及 `manifest.json`；原始 MP3 保留在 `peiyin` 中。
`配音对应表.md` 列出每个源文件、对应画面段落及段内时间。关键动画按句子起点播放，例如“再除以二”时才显示求解结果。
字幕按 41 条语句逐句切换，使用 x、e 等正常数学记号替代语音文本的“艾克斯”“伊”。音频按原速播放；视频停留时间依据音频实际长度调整。

如果 `peiyin` 中没有音频，则支持以下传统编号方式；两种方式都没有音频时，渲染带字幕的无配音视频。
`配音文案.txt` 包含与 `NARRATION` 一致的 24 段文案。
需要配音时，在本目录新建 `配音` 文件夹，放入 `01.mp3` 至 `24.mp3`（也支持同名 `.wav`）。
程序按编号对应段落，读取音频实际时长；没有音频的段落按阅读时间停留。
如果音频短于动画，段落至少保留动画所需时间。不要放入 affine 项目的配音。

每次完整执行场景后，会导出对应场景的 SRT 字幕及章节/字幕/配音时间轴 JSON：
`media/subtitles/OddEvenDecomposition.srt`、`media/subtitles/OddEvenDecomposition.json`。
JSON 中 `cues` 对应 24 个画面段落，`subtitles` 和 `audio_clips` 对应 41 条语句，`animation_events` 记录动画实际起止时间。
字幕时间使用实际渲染时间，包括场景转换；配音修改后请重新渲染以刷新时间轴。

颜色约定：蓝色为奇函数/sinh，红色为偶函数/cosh，黄色为 e^x，青色为 tanh。
图像上的函数值由 NumPy 直接计算，sinh 与 cosh 的和不是曲线形状叠加，而是相同横坐标处的纵坐标相加。

## 检查已渲染的视频

`tools/inspect_render.py` 检查完整场景的 24 个画面段落、41 条音频及逐句字幕时间，提取关键帧并生成分镜总览：

```powershell
& 'D:\Software\conda\envs\manim\python.exe' .\tools\inspect_render.py .\media\videos\Odd_Even_manim\1080p60\OddEvenDecomposition.mp4

# 将成片中的实际音频与 41 个源文件逐一做波形比对
& 'D:\Software\conda\envs\manim\python.exe' .\tools\check_voiceover_sync.py .\media\videos\Odd_Even_manim\1080p60\OddEvenDecomposition.mp4
```

输出在 `media/verification/`。检查脚本使用当前 Manim 环境已有的 PyAV、Pillow、SciPy 和 FFmpeg。

本机已完成带配音的 480p 预览与 1080p/60 fps 完整成片渲染。配音版时长约 3 分 29 秒；24 个画面段落、41 条音频及逐句字幕时间均已核验，关键帧已检查。全部 41 个源文件已与成片音频做波形比对，最小相关系数超过 0.99，测得编码偏差约 21 毫秒。数学关系此前已在 [-10,10] 的 1001 个采样点上完成数值校验。
