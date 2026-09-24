"""Record the narration and lay it out against the 44.5 s cut.

The script describes what the game actually is and what you actually do in it - the weapons
that exist as pickups, the crouch-stealth, the key that opens the portal, and the boss's
second phase - rather than generic atmosphere.
"""
import asyncio, json, subprocess, edge_tts

VOICE, RATE, PITCH = 'en-GB-RyanNeural', '-8%', '-4Hz'
TOTAL = 44.5

LINES = [
    (0.8,  "Chronoshift."),
    (2.6,  "A time traveller, stranded a hundred million years before his own."),
    (8.0,  "Era One. The prehistoric age."),
    (12.0, "You arrive with nothing. You survive with a spear, a club, a sling and a bola."),
    (20.5, "Crouch in the ferns and the raptors lose you. Stand up, and they come."),
    (27.5, "Cross the swamp, the nesting grounds, the canyon and the lava fields."),
    (33.4, "Find the key artifact. It opens the portal home."),
    (38.2, "Rex Prime guards it. Wounding him only makes him faster."),
]


async def say(text, out):
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(out)


def dur(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', p], capture_output=True, text=True)
    return float(r.stdout.strip())


async def main():
    placed, cursor = [], 0.0
    for i, (anchor, text) in enumerate(LINES, 1):
        mp3, wav = f'nvo_{i:02d}.mp3', f'nvo_{i:02d}.wav'
        await say(text, mp3)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-ar', '48000', '-ac', '2', wav], check=True)
        d = dur(wav)
        start = max(anchor, cursor + 0.3)
        cursor = start + d
        placed.append({'file': wav, 'start': round(start, 2), 'dur': round(d, 2)})
        print(f'{i}  {start:5.2f} -> {cursor:5.2f}s   "{text}"')
    json.dump({'voice': VOICE, 'lines': placed}, open('narration_layout.json', 'w'), indent=1)
    over = cursor - TOTAL
    print(f'\nends at {cursor:.2f}s of {TOTAL}s' + ('  *** OVERRUNS ***' if over > 0 else '  (fits)'))

asyncio.run(main())
