import json
lay = json.load(open('narration_layout.json'))
lines = lay['lines']; n = len(lines)
ins = ' '.join('-i ' + l['file'] for l in lines)
dly = ';'.join('[%d:a]adelay=%d|%d[a%d]' % (i, int(l['start']*1000), int(l['start']*1000), i)
               for i, l in enumerate(lines))
mix = ''.join('[a%d]' % i for i in range(n))
aud = (dly + ';' + mix + 'amix=inputs=%d:duration=longest:normalize=0,' % n +
       'acompressor=threshold=-20dB:ratio=2.5:attack=15:release=220,'
       'aecho=0.85:0.9:38:0.12,volume=1.35,aresample=48000[vo];'
       '[%d:a]atrim=start=41:duration=44.5,asetpts=PTS-STARTPTS,' % n +
       'afade=t=in:st=0:d=2.0,afade=t=out:st=42.0:d=2.5,volume=0.5,aresample=48000[mus];'
       '[mus][vo]sidechaincompress=threshold=0.03:ratio=9:attack=25:release=450:makeup=1[musduck];'
       '[musduck][vo]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95,aresample=48000[mix]')
cmd = ('ffmpeg -y -v error ' + ins + ' -i music.mp3 -filter_complex "' + aud + '" '
       '-map "[mix]" -c:a pcm_s16le narration_mix.wav')

s = open('compose.sh').read()
a = s.index('ffmpeg -y -v error')
b = s.index('ffmpeg -y -v error -framerate')
s = s[:a] + cmd + '\n\n' + s[b:]
s = s.replace("if(lt(t,8.2),0,if(lt(t,9.0),(t-8.2)/0.8,if(lt(t,11.6),1,if(lt(t,12.4),(12.4-t)/0.8,0))))",
              "if(lt(t,8.5),0,if(lt(t,9.3),(t-8.5)/0.8,if(lt(t,12.0),1,if(lt(t,12.8),(12.8-t)/0.8,0))))")
open('compose.sh', 'w').write(s)
print('rebuilt audio graph for %d lines; inputs: %s' % (n, ', '.join(l['file'] for l in lines)))
