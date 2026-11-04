# 圆的切线方程：向量投影证明

主文件：`Circle_Tangent_manim.py`，场景：`CircleTangentProjection`。
沿用 `Affine_Trans_manim.py` 的深色背景、微软雅黑、黄色章节标题、MathTex 公式、分段方法和字幕组织方式。

## 渲染

使用已安装 Manim Community 0.20.1 的虚拟环境 `D:\Software\conda\envs\manim`：

```powershell
# 1080p / 60 fps
.\render.ps1
# Manim 最高预设：4K / 60 fps，包含 peiyin 配音
.\render.ps1 -Quality k
# 480p / 15 fps，快速预览
.\render.ps1 -Quality l
# 渲染后打开视频
.\render.ps1 -Quality h -Preview
# 若系统默认禁止运行 .ps1，使用仅对本次进程生效的方式
powershell -NoProfile -ExecutionPolicy Bypass -File .\render.ps1 -Quality l
```

脚本临时为当前进程补充虚拟环境的 DLL / FFmpeg 路径。需要现有的 LaTeX、dvisvgm 和 Microsoft YaHei 字体。
视频输出到 `media/videos/Circle_Tangent_manim/` 下对应的质量目录。

## 证明思路

圆心 C=(a,b)，半径 r>0，切点 P=(x₀,y₀) 满足圆方程。
开场直接画圆、切点 P 和切线，提出“圆在 P 点的切线方程是什么？”。
在切线上任取 Q=(x,y)，连接 CQ、CP。半径 CP 垂直于切线。
设向量 CQ 和 CP 的夹角为 θ，由直角三角形可得 CQ cosθ=CP=r。
使用高中数量积公式：向量 CQ·向量 CP=CQ×CP×cosθ=(CQ cosθ)×CP=r²。
Q=P 时数量积同样为 r²。动画不使用投影算子或单位向量符号。展开坐标即得：

**(x₀−a)(x−a)+(y₀−b)(y−b)=r²。**

反过来，这个方程等价于 PQ·CP=0，其轨迹为过 P 且垂直于 CP 的直线。
由 CQ²=r²+PQ²，直线与圆唯一的公共点为 P。推导包含竖直切线。
动画图形按等比例绘制，右侧坐标为一般符号，不将示意图位置当作实际坐标。

## 字幕与配音

当前自动读取 `peiyin` 中以 `0001_` 至 `0026_` 开头的 26 段 MP3，逐句配合动画播放。
使用原始配音音色和语速，自动读取实际音频时长，片段后留 0.15 秒间隔。
字幕位于 `VOICE_LINES`，按音频分成 26 段。末尾保留反向验证，已删除结论章节。
缺失或重复的编号会报错，避免误配或漏配。
每次渲染同时生成 `media/narration_timeline.json`，记录每段音频的起点、时长和字幕。
4K 成片位于 `media/videos/Circle_Tangent_manim/2160p60/CircleTangentProjection.mp4`。
