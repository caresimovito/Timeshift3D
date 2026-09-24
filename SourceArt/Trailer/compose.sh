#!/bin/sh
set -e
FR="C:/repos/Unreal Projects/Timeshift3D/Saved/GameFrames/frame.%04d.png"
OUT="C:/repos/Unreal Projects/Timeshift3D/Trailer_Chronoshift.mp4"
F="C\:/Windows/Fonts/arialbd.ttf"

# narration, each line delayed to sit over the shot it describes
ffmpeg -y -v error \
 -i vo_01.wav -i vo_02.wav -i vo_03.wav -i vo_04.wav -i vo_05.wav -i vo_06.wav -i vo_07.wav \
 -filter_complex "\
 [0:a]adelay=1000|1000[a0];\
 [1:a]adelay=4200|4200[a1];\
 [2:a]adelay=10500|10500[a2];\
 [3:a]adelay=16500|16500[a3];\
 [4:a]adelay=25500|25500[a4];\
 [5:a]adelay=38500|38500[a5];\
 [6:a]adelay=44000|44000[a6];\
 [a0][a1][a2][a3][a4][a5][a6]amix=inputs=7:duration=longest:normalize=0,\
 volume=1.6,aresample=48000[vo]" \
 -map "[vo]" -c:a pcm_s16le narration_mix.wav

ffmpeg -y -v error -framerate 30 -i "$FR" -i narration_mix.wav \
 -filter_complex "\
 [0:v]fade=t=in:st=0:d=1.2,\
 drawtext=fontfile='$F':text='CHRONOSHIFT':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=h*0.40:alpha='if(lt(t,1.2),0,if(lt(t,2.0),(t-1.2)/0.8,if(lt(t,4.4),1,if(lt(t,5.2),(5.2-t)/0.8,0))))',\
 drawtext=fontfile='$F':text='ERA ONE  \:  THE PREHISTORIC AGE':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=h*0.52:alpha='if(lt(t,10.6),0,if(lt(t,11.4),(t-10.6)/0.8,if(lt(t,14.6),1,if(lt(t,15.4),(15.4-t)/0.8,0))))',\
 drawtext=fontfile='$F':text='CHRONOSHIFT':fontcolor=white:fontsize=104:x=(w-text_w)/2:y=h*0.38:alpha='if(lt(t,45.5),0,if(lt(t,46.5),(t-45.5),1))',\
 drawtext=fontfile='$F':text='ERA ONE  \:  THE PREHISTORIC AGE':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=h*0.52:alpha='if(lt(t,46.5),0,if(lt(t,47.5),(t-46.5),1))',\
 fade=t=out:st=49.3:d=1.2[v]" \
 -map "[v]" -map 1:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
 -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "wrote $OUT"
