# 三角形内角平分线定理：等面积法证明

这个 Manim 项目会生成一个面向高中生的讲解视频，用「同一对面积，从两种角度计算面积比」证明：

```text
BD / DC = AB / AC
```

## 文件

- `angle_bisector_area_proof.py`：主场景脚本
- `manim.cfg`：Manim 默认渲染配置
- `render.ps1`：Windows PowerShell 渲染入口
- `requirements.txt`：Python 依赖

## 渲染

本机已检测到可用环境：

```text
D:\Software\conda\envs\manim\python.exe
Manim Community v0.20.1
TeX Live 2026
```

所以可以直接渲染：

```powershell
.\render.ps1
```

当前项目路径含中文，`render.ps1` 会临时把项目挂到一个纯英文盘符下渲染，避免 `dvisvgm` 处理中文路径时报错。渲染结束后盘符会自动移除，视频仍然输出在本目录的 `media` 文件夹里。

低清快速预览：

```powershell
.\render.ps1 -Quality low
```

如果 PowerShell 提示脚本执行策略限制，改用：

```powershell
powershell -ExecutionPolicy Bypass -File .\render.ps1 -Quality low
```

高清渲染：

```powershell
.\render.ps1 -Quality high
```

如果换机器运行，再创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m manim -qm angle_bisector_area_proof.py AngleBisectorAreaProof
```

也可以直接运行：

```powershell
python -m manim -pqm angle_bisector_area_proof.py AngleBisectorAreaProof
```

生成的视频通常位于：

```text
media/videos/angle_bisector_area_proof/720p30/AngleBisectorAreaProof.mp4
```

## 讲解主线

1. 设 `AD` 是 `∠A` 的内角平分线，`D` 在 `BC` 上。
2. 三角形 `ABD` 和 `ACD` 共用从 `A` 到 `BC` 的高，所以面积比等于底边比：`BD / DC`。
3. 因为 `D` 在角平分线 `AD` 上，所以 `D` 到 `AB`、`AC` 的距离相等；把这段距离当作两个三角形分别以 `AB`、`AC` 为底时的高，面积比等于邻边比：`AB / AC`。
4. 同一个面积比等于两个式子，因此 `BD / DC = AB / AC`。
