$Ffmpeg = "D:\Software\conda\envs\manim\Library\bin\ffmpeg.exe"
if (-not (Test-Path $Ffmpeg)) { $Ffmpeg = "ffmpeg" }

$Video = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"

& $Ffmpeg -y -ss 00:00:20.8 -i $Video -frames:v 1 -update 1 "qa_angle_explain_20_8s.png"
& $Ffmpeg -y -ss 00:00:23.0 -i $Video -frames:v 1 -update 1 "qa_angle_explain_23_0s.png"
& $Ffmpeg -y -ss 00:00:25.0 -i $Video -frames:v 1 -update 1 "qa_angle_explain_25_0s.png"
& $Ffmpeg -y -ss 00:00:26.2 -i $Video -frames:v 1 -update 1 "qa_angle_explain_26_2s.png"
& $Ffmpeg -y -sseof -1 -i $Video -frames:v 1 -update 1 "qa_final_no_summary.png"
