#!/bin/sh
set -e
# The opening hero shot (frames 0-179) is cut: no hero visible and only one narration line.
# Everything downstream is re-timed 6 s earlier rather than re-rendered.
FR="C:/repos/Unreal Projects/Timeshift3D/Saved/GameFrames/frame.%04d.png"
OUT="C:/repos/Unreal Projects/Timeshift3D/Trailer_Chronoshift.mp4"
F="C\:/Windows/Fonts/arialbd.ttf"
DUR=44.5
MUSIC_START=41

ffmpeg -y -v error -i nvo_01.wav -i nvo_02.wav -i nvo_03.wav -i nvo_04.wav -i nvo_05.wav -i nvo_06.wav -i nvo_07.wav -i nvo_08.wav -i music.mp3 -filter_complex "[0:a]adelay=800|800[a0];[1:a]adelay=3120|3120[a1];[2:a]adelay=8480|8480[a2];[3:a]adelay=13120|13120[a3];[4:a]adelay=20500|20500[a4];[5:a]adelay=27500|27500[a5];[6:a]adelay=33400|33400[a6];[7:a]adelay=39030|39030[a7];[a0][a1][a2][a3][a4][a5][a6][a7]amix=inputs=8:duration=longest:normalize=0,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=220,aecho=0.85:0.9:38:0.12,volume=1.35,aresample=48000[vo];[8:a]atrim=start=41:duration=44.5,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=2.0,afade=t=out:st=42.0:d=2.5,volume=0.5,aresample=48000[mus];[mus][vo]sidechaincompress=threshold=0.03:ratio=9:attack=25:release=450:makeup=1[musduck];[musduck][vo]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95,aresample=48000[mix]" -map "[mix]" -c:a pcm_s16le narration_mix.wav

ffmpeg -y -v error -framerate 30 -start_number 240 -i "$FR" -i narration_mix.wav \
 -filter_complex "\
 [0:v]fade=t=in:st=0:d=1.0,\
 drawtext=fontfile='$F':text='CHRONOSHIFT':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=h*0.40:alpha='if(lt(t,0.8),0,if(lt(t,1.6),(t-0.8)/0.8,if(lt(t,3.8),1,if(lt(t,4.6),(4.6-t)/0.8,0))))',\
 drawtext=fontfile='$F':text='ERA ONE  \:  THE PREHISTORIC AGE':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=h*0.52:alpha='if(lt(t,8.5),0,if(lt(t,9.3),(t-8.5)/0.8,if(lt(t,12.0),1,if(lt(t,12.8),(12.8-t)/0.8,0))))',\
 drawtext=fontfile='$F':text='CHRONOSHIFT':fontcolor=white:fontsize=104:x=(w-text_w)/2:y=h*0.38:alpha='if(lt(t,39.5),0,if(lt(t,40.5),(t-39.5),1))',\
 drawtext=fontfile='$F':text='ERA ONE  \:  THE PREHISTORIC AGE':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=h*0.52:alpha='if(lt(t,40.5),0,if(lt(t,41.5),(t-40.5),1))',\
 drawtext=fontfile='$F':text='Music\: The Battle of 1066 - Patrick Patrikios':fontcolor=white@0.72:fontsize=24:x=(w-text_w)/2:y=h*0.62:alpha='if(lt(t,41.5),0,if(lt(t,42.3),(t-41.5)/0.8,1))',\
 fade=t=out:st=43.3:d=1.2[v]" \
 -map "[v]" -map 1:a -t 44.5 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
 -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "wrote $OUT"
