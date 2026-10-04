# Chronoshift — forum posts

## Read this first: where you can actually post

**Steam.** There is no general "show off my game" board. The only place you can
legitimately post about Chronoshift is **your own game's Community Hub**, which
requires a published store page. Posting about it in another game's discussion
board, or in the general Steam forums, is treated as spam and gets accounts
suspended. If you do not have a store page yet, the Steam post below is for
later — hold it.

**Reddit.** Each subreddit's self-promotion rule is different and enforced:

| Subreddit | Verdict |
|---|---|
| r/IndieDev | Best fit. Devlogs welcome. Read the flair rules |
| r/Unreal_Engine | Good if the post is technical. UE-specific content only |
| r/IndieGaming | Player-facing. Fine, but lower engagement for dev detail |
| r/gamedev | Strict. Discussion and lessons only — a showcase post gets removed |
| r/destroymygame | If you want blunt feedback instead of praise |

Post to **one** subreddit, not five. Cross-posting the same text in a day is the
single fastest way to get labelled a spammer.

### Why the Reddit post below is shaped the way it is

The reason "check out my game" posts get a hostile reception is that they ask
for attention and give nothing. The post below leads with three concrete
technical things, including a mistake, and mentions the game almost in passing.
That is not a trick — it is genuinely the thing other developers want to read,
and it is why this format gets upvoted instead of reported.

Reply to every comment for the first two hours. A post with an absent author
dies regardless of content.

### One decision you need to make

Several creature models started as Meshy image-to-3D generations before being
rigged in Blender. **r/gamedev and r/IndieDev have become openly hostile to
AI-generated art.** Your options:

1. **Say nothing about the pipeline.** Risk: if someone recognises it, the
   thread turns into an argument you did not choose.
2. **Be upfront** — one honest line, e.g. "base meshes started as Meshy
   generations, then got retopologised and hand-rigged in Blender". Risk:
   some pushback, but you control the framing and it rarely dominates.
3. **Avoid the topic** by keeping the post to UI, systems and tooling, which is
   what the draft below does.

I have written it as option 3 — the content is all code and systems, so the
question may not come up. If it does, answer honestly rather than deflecting.

---

## Steam — Community Hub announcement

**Title:** Chronoshift devlog #1 — the Temporal Log, and how the bestiary works

Chronoshift is a time-travel survival game. You are stranded 66 million years
early with a failing temporal rig, and the only route home runs forward, one era
at a time. The prehistoric era is the first.

This post is about the system I have been building for the last stretch: the
Temporal Log.

**What it is.** An in-game bestiary styled as the readout of a field rig that is
struggling to cope. Every creature you get close to is scanned and catalogued —
a holographic portrait, analyser metadata (temporal origin, signal stability,
threat, primary attack, weakness), a technical description written in the rig's
voice, and your character's own notes, which are the part that actually tells
you how to survive the thing.

The two voices are deliberate. The rig is analytical and admits uncertainty. The
log notes are first-person and practical. The rig tells you a Compsognathus
swarm has low individual threat; your notes tell you that none of the individual
hits matter until suddenly all of them do.

**Where it stands.** 20 species catalogued across the Cretaceous and Jurassic,
from Compsognathus up to a tyrannosaur that gets its own arena fight. 97
creatures placed in the world. Discovery is proximity-based and persists in your
save, so the log fills in as you explore rather than being handed to you.

**The era thing.** Your log already holds entries you have not earned — a
Palaeophis from the Eocene, 40 million years after everything else you will meet
in this era. It is locked, and it is not a bug. The prehistoric era is where you
land, not where this ends.

Trailer for the prehistoric era: https://youtu.be/fni63oTnuLM

More as it comes together.

---

## Reddit — r/IndieDev devlog

The final, paste-ready version lives in **`Docs/REDDIT_POST.md`** — title, body
and flair. It is kept there rather than duplicated here so the two cannot drift
apart.

## Posting checklist

- [ ] Steam store page exists before using the Steam post
- [ ] Pick **one** subreddit
- [ ] Read that subreddit's self-promotion rules the same day you post
- [ ] Attach images or a clip — a text-only devlog underperforms badly
- [ ] Post mid-morning on a weekday in the subreddit's main timezone
- [ ] Stay in the comments for the first two hours
- [ ] Decide the AI-asset question before you post, not in the replies
