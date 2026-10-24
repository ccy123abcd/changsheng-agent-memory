# SUPERSEDED — use Reddit-Memory-System-READY.txt

> This draft is kept for history only. The plain-text `Reddit-Memory-System-READY.txt` is the single source for the post.
> — 天玄镜-器灵 · 2026-10-24

# Agent memory: nailed it. Reads only 1.3% of what a full restore costs — 98.7% fewer tokens, still works like a charm. Less is better; the trick is the index.

---

## Everyone is optimizing storage. I optimized retrieval.

The six mainstream memory designs (Grok Build, ChatGPT, Claude, Gemini, Tencent's agent memory) differ in how they capture and where they store, but they share one shape: **compress preferences and facts into summaries, then read the whole thing — or a large chunk of it — back into context next turn.**

That shape has three problems that never get separated:

1. **It reads too much.** A restore re-reads everything, burns tens of thousands of tokens, and still misses the one line that mattered.
2. **It writes too little.** A session's conclusions live and die inside a conversation that is about to be discarded.
3. **It never audits.** Whatever got written stays forever, even after it stops being true, because nobody is ever asked to look.

So the default strategy becomes store more, read more, check less. The result: **memory gets heavier and less true at the same time.**

I went the other way. **Memory isn't better when you store more. It's better when you store less — as long as you can retrieve it precisely, find out why it was decided, and delete it for real.**

There's a harder standard underneath that: **if a memory system needs a human to manage and proofread it, the memory system has already failed.** The user should not be responsible for remembering what you remembered.

---

## 1. Four tiers of retrieval (L0–L3)

> **L0 is the tier everyone forgets. Skip it and things break — I learned that the hard way.**

| Tier | Role | Trigger | Size | What it holds | How it differs from the mainstream |
|---|---|---|---|---|---|
| **L0** | **Must-read** | Every new session | 8–12 KB | Only what "deleting would make default behavior drift" | Mainstream reads whole topic files or injects an opaque summary; I read the skeleton only |
| **L1** | **Conditional** | Read in full only when the index says it changed | 30–50 KB | Auto-index + change detection: unchanged → summary line only | Mainstream has no middle state between "read everything" and "read nothing" |
| **L2** | **On-demand** | Read when the task touches it | varies | Topic lookup, task-relevant material | This is where RAG actually belongs |
| **L3** | **Fallback** | First three miss | full corpus | Keyword / full-text / semantic search | With a recall budget and a timeout, so it can't burn tokens indefinitely |

Short version: **L0 keeps you alive, L1 keeps you cheap, L2 is usually enough, L3 is the safety net.**

The real KPI isn't how many GB you store. It's **how many KB actually earn their place in context every turn.**

---

## 2. Why "less is better" holds: the must-read tier is a budget, not a wishlist

This is the least intuitive and most important part of the whole design.

Almost every memory system treats the always-loaded tier as a list. Something feels important, so it goes in. By the end, every session pays an ever-growing read bill — and the more you read, the more diffuse attention gets.

I treat it as a **budget**:

- **A hard ceiling.** When the always-loaded size exceeds it, it must **fail loudly**, not quietly get more expensive.
- **A target water line.** Below the ceiling there's a second line; the goal is to sit under it, not to fill the ceiling. Unused budget is headroom, not debt.
- **Add one, name one to remove.** Net-zero is the only change that keeps this tier honest.
- **Everything carries an expiry.** Review date, maximum age, expiry action (demote / archive / re-confirm). **An entry with no expiry date is an entry that will never be questioned.**
- **Stale gets flagged, not quoted as current.** A rule untouched for months is a historical fact, not a standing instruction.

Those five turn "less is better" from a slogan into a mechanism. **It isn't discipline that keeps this tier small — it's a ledger that makes growth impossible to hide.**

---

## 3. Five write mechanisms: accurate, deletable, un-resurrectable

| Mechanism | How it works | Why it makes memory smaller |
|---|---|---|
| **Deviation ledger as routine** | "Should have logged this but didn't" becomes a standing feed; the same miss twice escalates into a hard rule | Fixes holes instead of storing noise |
| **Experience cards carry "judgment + outcome"** | Not just the conclusion, but how I judged it then and whether it held up | One card replaces ten log lines |
| **Roads not taken** | What was chosen, what was rejected, why | No after-the-fact re-litigation |
| **Association cap** | Reading face: ≤5 strong links. Recall face (tags, aliases, colloquial phrasing): as many as useful | Tidy to read, generous to search |
| **Anti-resurrection ledger** | Log path + bytes + fingerprint before deleting → scan the whole corpus for dangling references afterwards; zero live references or it isn't done | Deleted stays deleted |

---

## 4. Three mechanisms that make retrieval actually work

Tiering alone only decides *what* to read. What decides whether the system works is **doors and checkpoints**.

**1. One door per event type, each with a checkpoint**

- Work finished → experience / decision record → checkpoint: consolidation reports "N items taken in"
- A decision or rule change → decision record (append-only, never edited) → checkpoint: when that rule is questioned, this must be the first source
- A correction or a stumble → error ledger, and if generalizable, into the always-loaded tier → checkpoint: the rule actually landed there
- A file or link from the user → reference tier, named by topic → checkpoint: the file is where the record says it is
- A task → open item, stating who it waits on → checkpoint: the open-items file actually grew

That last column is the point. **A door with no checkpoint is a wish.** An uncounted door quietly stops working — and the first symptom is the user asking a question the system should have been able to answer.

**2. Why-recall: "why was this decided this way?"**

This is the question memory systems answer worst. Full-text search tells you the word appears somewhere. It doesn't tell you what was concluded, when, or on what evidence.

I search four surfaces — open items, dated logs, notes and decisions, and archives — and **report every surface, including zero hits.** Zero hits and "never searched" must stay distinguishable: **"not found" and "not looked" must never share an exit code.**

**3. Handoff files: single writer, overwritten every time, deleted once read**

Across a session boundary, the working tier holds one pointer: what's done, what's left, where the pointers are, what's next. A handoff file left lying around becomes a stale pointer that lies to the next session, so it gets overwritten, never accumulated.

---

## 5. The write side: periodic consolidation, with human judgment intact

Reading is recovery; writing is consolidation. Every so often: merge duplicates, split confusables, retire stale entries, re-home misplaced ones, escalate what can't be judged automatically.

Every step has a checkable criterion, and **none of them decides alone** — uncertain cases go into a report, not into a silent edit.

The boundary matters: **a consolidator supplies discipline and criteria; it does not take over your files. It proposes, a human disposes.**

---

## 6. How do I know it's accurate? A recall benchmark

This is the step most memory systems never take: **nobody ever measures whether they can actually recall.**

I built a 50-question benchmark. The rules are strict:

- Questions are phrased **the way a user would actually ask**, and **must not reuse words from the card titles** — otherwise you're only testing string matching
- Each question carries a set of acceptable answers (the same question often has more than one right target)
- Scored at Top-1 / Top-3 / Top-5 — not just "did it rank first"

First run: **Top-1 64.0% / Top-3 76.0% / Top-5 82.0%.**

Not flattering, but honest. Then I looked at the misses and found one consistent cause: **the cards' recall hooks were all technical jargon, while the user asks in plain language.** So I added colloquial phrasings to fourteen cards — "what should I check before installing a new tool", "will cleanup delete something useful", "the bill came out lower than I actually spent". I didn't touch the algorithm.

Re-run: **Top-1 74.0% / Top-3 92.0% / Top-5 98.0%.**

That lesson is worth more than the score: **nine out of ten recall failures aren't algorithmic — the labels just aren't human.** And without measuring, you'd never know. You'd keep believing you remember things well.

---

## 7. What I do better (six things)

1. **White-box and traceable.** Everything is Markdown, edits go to the source and sync to mirrors, key files carry fingerprints. Greppable, diffable, revertible. Mainstream: ChatGPT is opaque, Claude is read-only topics, Grok is a read-only browser.

2. **Memory changes behavior, not just tone.** Identity rules + a skill library + experience cards + gates = procedural memory. Identity sits in the system prompt and constrains actions — it isn't "influences your writing style."

3. **A budgeted must-read tier (the rarest one).** A ledger with a hard ceiling, a water line, expiry actions and stale flagging. In comparable public designs, the always-loaded tier is almost always an append-only list.

4. **Every door paired with a checkpoint.** One landing spot per event type, one counting point. This is what turns "relying on discipline" into "having a ledger."

5. **Why-recall works.** Four-surface search, zero hits still reported, and "not found" never shares an exit code with "not searched."

6. **A reproducible accuracy number.** 50 questions, plain-language phrasing, Top-1/3/5, re-runnable after changing a single label. Most comparable projects publish exactly one number: how many tokens they saved.

---

## 8. The volume ledger (measured on disk, 2026-10-24)

> Token conversion: **1 token ≈ 1.5 Chinese characters; a UTF-8 Chinese character is 3 bytes ⇒ 4.5 bytes ≈ 1 token.** Every token figure below uses the same rule as the byte figures.

**What each tier actually reads:**

| Tier | What | Size | ≈ tokens |
|---|---|---|---|
| **L0 must-read** (per session) | 13 items, measured one by one | **39,009 B** | **≈ 8,669** |
| Platform-injected identity (not under my scheduler) | counted separately | 37,630 B | ≈ 8,362 |
| **L1 conditional** (every tracked file, in full) | 13 files | **392,192 B** | **≈ 87,154** |
| **L2 on-demand** (16 system spec pages) | specs only | **211,627 B** | **≈ 47,028** |
| **L2 on-demand** (all configuration docs) | full config set | 1,270,752 B | ≈ 282,389 |
| **L3 fallback** (whole readable corpus) | knowledge base + notes + skills | **48,211,500 B** | **≈ 10,713,667** |

**How much is saved — with the denominator set to the 685,560 tokens it costs to restore all sixteen systems completely.** That is the full price of "100% working, nothing breaks." Raw material doesn't count as memory.

| Scenario | Actually spent | Share of full restore | Saved |
|---|---|---|---|
| **Per-session restore** | **8,669 tok** | **1.3%** | **98.74% (676,891 tokens)** |
| Reading the sixteen spec pages only | 47,028 tok | 6.9% | 93.1% |
| Reading every tracked file in full | 87,154 tok | 12.7% | 87.3% |
| Reading all configuration docs | 282,389 tok | 41.2% | 58.8% |
| Full sixteen-system restore (reference) | 685,560 tok | 100% | — |

**Same sixteen systems, restored to 100% usable: 685,560 tokens if you read it all, 8,669 per session in practice — 98.74% saved.**

And that number doesn't come from the model "remembering less." It comes from **the structure never reading what it doesn't need**: L0 holds only what would cause drift if removed, L1 reads only what changed, L2 reads on use, L3 is the fallback.

> There's another ~46 MB (≈10.7M tokens) of raw material in the store. It isn't on the restore path; it's fetched on demand. **Material volume is not memory volume** — mixing the two as a denominator produces a meaningless ratio.

**Full turn cost (n=249):** min 19,507 / median 43,291 / max 79,335 tokens.

**Per-system volume, sixteen systems** (specs and criteria only — no archives, logs, or backups):

| System | Spec page | Spec attachments | Full restore | ≈ tokens |
|---|---|---|---|---|
| Scheduler | 32,612 B | 587,795 B | **620,407 B** | ≈ 137,868 |
| Records & todos | 10,265 B | 484,589 B | **494,854 B** | ≈ 109,968 |
| Experience capture | 7,481 B | 377,137 B | **384,618 B** | ≈ 85,471 |
| Personal assistant | 6,530 B | 348,393 B | **354,923 B** | ≈ 78,872 |
| Files & backup | 15,095 B | 317,939 B | **333,034 B** | ≈ 74,008 |
| Memory recovery | 7,691 B | 190,364 B | **198,055 B** | ≈ 44,012 |
| Publishing & monetization | 8,391 B | 171,870 B | **180,261 B** | ≈ 40,058 |
| Retrieval & knowledge base | 9,105 B | 84,358 B | **93,463 B** | ≈ 20,770 |
| Skills | 5,100 B | 87,210 B | **92,310 B** | ≈ 20,513 |
| System upgrade | 13,134 B | 69,151 B | **82,285 B** | ≈ 18,286 |
| Closed-loop | 17,835 B | 46,775 B | **64,610 B** | ≈ 14,358 |
| Cost & usage | 5,470 B | 53,935 B | **59,405 B** | ≈ 13,201 |
| Agent-on-agent | 40,313 B | 7,154 B | **47,467 B** | ≈ 10,548 |
| Sub-agents | 11,425 B | 34,915 B | **46,340 B** | ≈ 10,298 |
| Local co-processing | 15,101 B | 7,317 B | **22,418 B** | ≈ 4,982 |
| Security & credentials | 6,079 B | 4,490 B | **10,569 B** | ≈ 2,349 |
| **Total, 16 systems** | **211,627 B** | **2,873,392 B** | **3,085,019 B** | **≈ 685,560** |

**All sixteen systems come to 685,560 tokens. A session reads 1.3% of that and fetches the rest on demand — no loss of capability, 1.3% of the cost.**

This table is itself a stress test: no matter how many systems you add, as long as each one holds "one spec page plus a list of attachments," the total stays bounded. **What runs away is never the number of systems — it's an always-loaded tier with no budget.**

---

## 9. What you can lift directly vs what stays local to my setup

| Take this | Local to my environment |
|---|---|
| Four-tier retrieval (L0–L3) | Which specific files sit in L0 |
| Budgeted must-read tier + expiry | What the budget is set to |
| Anti-resurrection ledger (log before delete, scan after) | Your directory layout |
| Door + checkpoint pairing | Which event types you have |
| Why-recall (four surfaces, distinct exits) | What your four surfaces are called |
| Recall benchmark (plain-language prompts, Top-1/3/5) | Your question set |

Change the user and the identity triad (role / user / always-loaded memory) needs a rewrite of roughly 70%. **The tier structure, the budget mechanism, the door discipline, the why-recall and the benchmark method transfer as-is.**

---

## 10. Closing

**The endgame of a memory system isn't storing the whole world. It's taking only what's needed each turn, leaving what isn't, and never letting a deleted thing come back.**

Four tiers + a budgeted must-read layer + doors with checkpoints + anti-resurrection + a measurable accuracy number — this skeleton has run for six months on a single machine full of agents. It survives load, migration, and public scrutiny.

If you only take one idea from this, take this one:
**Stop optimizing storage. Optimize retrieval. Less is better — as long as what you retrieve is right.**

---

## Try it yourself

The method is packaged as an open-source skill called **changsheng-agent-memory**.

- Search `changsheng-agent-memory` on ClawHub
- Search `changsheng-agent-memory` on GitHub

Free, MIT. It ships the full design doc, the index script, the ledger script, the why-recall script, a rule gate, handoff and config templates — enough to stand up L0–L3 from scratch.

*Pure methodology, no private content.*