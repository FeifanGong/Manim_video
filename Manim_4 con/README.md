# Symmetric Substitution Manim Project

This Manim scene explains how to maximize

```tex
\frac{1}{1+x^2}+\frac{1}{1+y^2}
```

under the condition `x+y=2`, using the symmetric substitution
`x=1+t, y=1-t`.

## Render

```powershell
.\render.ps1 -Quality m
```

If PowerShell blocks local scripts on this machine, use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\render.ps1 -Quality m
```

The script uses:

```text
D:\Software\conda\envs\manim\python.exe
```

To preview after rendering:

```powershell
.\render.ps1 -Quality m -Preview
```
