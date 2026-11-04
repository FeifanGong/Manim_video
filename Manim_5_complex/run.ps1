<#
.SYNOPSIS
    Manim 项目快捷运行脚本
.DESCRIPTION
    激活 conda manim 环境并渲染当前项目的场景。
    用法:
      .\run.ps1                     - 预览 ComplexPlaneIntro 场景
      .\run.ps1 EulersFormula       - 预览指定场景
      .\run.ps1 -q -s EulersFormula - 高质量渲染指定场景
.PARAMETER Scene
    要渲染的场景类名（默认: ComplexPlaneIntro）
.PARAMETER Quality
    渲染质量: p=预览, q=低清, h=高清, k=4K（默认: p）
.PARAMETER Save
    只保存不预览（默认: 预览）
#>

param(
    [string]$Scene = "ComplexPlaneIntro",
    [ValidateSet("p", "q", "h", "k")]
    [string]$Quality = "p",
    [switch]$Save
)

$CONDA_PYTHON = "D:\Software\conda\envs\manim\python.exe"
$CONDA_MANIM = "D:\Software\conda\envs\manim\Scripts\manim.exe"
$SCENE_FILE = "scene.py"

# 检查环境
if (-not (Test-Path $CONDA_MANIM)) {
    Write-Host "[错误] 找不到 Manim: $CONDA_MANIM" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $SCENE_FILE)) {
    Write-Host "[错误] 找不到场景文件: $SCENE_FILE" -ForegroundColor Red
    exit 1
}

# 质量参数映射
$flag = switch ($Quality) {
    "p" { "-p" }    # 预览 (低清 + 播放)
    "q" { "-ql" }   # 低清
    "h" { "-qh" }   # 高清
    "k" { "-sk" }   # 4K
}

$saveFlag = if ($Save) { "-s" } else { "" }

Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        Manim 渲染引擎                    ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║ 场景: $($Scene.PadRight(30))║" -ForegroundColor Cyan
Write-Host "║ 质量: $Quality (预览模式)               ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 执行渲染
$cmd = "& '$CONDA_MANIM' $flag $saveFlag '$SCENE_FILE' $Scene"
Write-Host "> $cmd" -ForegroundColor Yellow
Write-Host ""

Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ 渲染完成！" -ForegroundColor Green
} else {
    Write-Host "`n❌ 渲染出错，请检查错误信息。" -ForegroundColor Red
}