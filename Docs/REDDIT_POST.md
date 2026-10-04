# Ready to paste — r/IndieDev

## Title

```
I generate my entire UI frame art in Python instead of drawing it — plus the Slate bug that turned every panel into an ellipse
```

Flair: **Discussion** or **Informative**.

## Body

Solo dev, UE 5.8. I have spent the last stretch building the in-game bestiary
for my game and hit three things worth passing on — one neat, one stupid, and
one that was genuinely my fault.

---

**1. The ornate UI is generated, not drawn**

I wanted a brass instrument-panel look: framed parchment panels, corner
rosettes, gears and clock faces down the margins. I cannot draw. So a Python
script generates all of it.

Ten 9-slice frame textures, each built from a concentric colour profile — edge,
dark, mid, lit, highlight, groove, inner line — so the band reads as bevelled
metal. Then seven instrument pieces: cogs with trapezoidal teeth and spoked webs
punched through to transparent, two clock faces with bezels, 60 ticks, numerals
and hands, a cyan sweep gauge, and a knurled medallion.

Two things made it work:

- **Draw at 4x and downsample.** That is what gives the circles and tooth flanks
  clean edges. At 1x the teeth alias horribly.
- **Author each frame at the pixel size it renders at**, with the 9-slice margin
  sitting just outside the band. Then Slate only stretches the flat centre and
  the frame stays crisp at any panel size. My first attempt used a margin of a
  quarter of the texture, and the frames ballooned when stretched across a large
  panel.

The payoff is that the whole look is one file. Change the brass ramp, re-run,
re-import, and every panel in the game updates together. Gears and clock faces
turn out to be an ideal case for this because they are regular geometry —
evenly spaced teeth, radial hands, concentric bevels. I would not try to
generate a creature this way, but instrument chrome is just maths.

---

**2. The stupid one: every panel rendered as an ellipse**

Backdrop, record panel, timeline rail — all stadium-shaped blobs. It looked
ridiculous.

I had set each `SlateBrush` to `drawAs: RoundedBox`. That defaults to
`roundingType: HalfHeightRadius` with `cornerRadii: 0`, which rounds every panel
by half its own height. Set `FixedRadius` with an explicit radius and it is
fine.

No warning, no error. It just silently looks absurd. Worth knowing before you
lose an hour to it.

---

**3. The one that was actually my fault, and worse**

My creature-discovery system was writing "the player has found this species"
onto the **data assets** — shipped, read-only reference content.

Three consequences, in increasing order of bad:

- Play-session progress dirtied tracked `.uasset` files in git
- It vanished whenever the editor closed without saving
- It could never persist in a packaged build at all, because a build cannot
  write back to its own content

And the kicker: one species had already been committed to the repo as
discovered, so every player would have started with it unlocked.

Moved it to a proper `SaveGame` holding an array of discovered ids. Obvious in
hindsight. If you are storing anything player-specific on a data asset, go and
check it now.

One Blueprint wrinkle if you do this: you cannot mutate another object's array
in place. A Get on an object's array variable yields a copy, so `Add` silently
does nothing. I keep the array on the character and write the whole thing onto a
fresh save object.

---

**Bonus trap, and this one cost me real hours**

**Never compile your character blueprint while a PIE session is running.**

It does not error. The blueprint reports a clean compile. The graphs read back
intact. But `EventTick` silently stops firing on the player pawn **for the rest
of the editor session** — which killed footsteps, torch audio, zoom and my
discovery system all at once.

It presents exactly like a logic bug in whatever you just edited, so I went
hunting through code that was correct the whole time. What finally settled it
was dropping an unconditional `PrintString` at the top of a tick-driven function
and watching it never appear once. Restarting the editor fixed it instantly.

If tick-driven behaviour dies right after an edit, check for this before you
debug the code.

---

For context, the game is a time-travel survival thing — stranded 66 million
years early, the only route home runs forward one era at a time. The bestiary is
styled as a field rig struggling to log what it is looking at. 20 species and 97
creatures placed in the first era so far.

Trailer for the first era, if you want to see what it all ends up looking like:
https://youtu.be/fni63oTnuLM

Happy to go into any of it in more detail, or share the generator script if
anyone wants it.


---

## Note on the trailer link

It sits at the **end**, as context, not at the top. A devlog that opens with a
trailer link reads as an advert with technical decoration, and that is the thing
that gets downvoted.

If r/IndieDev's current rules say external links belong in a comment — check the
pinned post on the day — cut that line from the body and post it as your own
first comment instead. Reddit treats a link in the body as promotional weight
against the post in some subs; a link in a comment never counts against you.
