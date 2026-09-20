---
name: changsheng-agent-memory
version: 0.6.0
description: "Cross-session memory recovery for AI agents — your agent never cold-starts again.\nAlways-loaded identity & todos, hash-indexed conditional reads cut recovery cost ~70%\n(~55-75% cumulative when the host already injects identity). Pure local, zero deps.\n\nUse when:\n(1) A new chat asks \"where did we leave off?\" and you have no context\n(2) Context is filling up and you're about to hit the limit mid-task\n(3) User says \"I already told you this\"\n(4) You re-read the same identity/rules/todos files at every session start\n(5) Session start burns tens of thousands of tokens before real work begins\n(6) You need to hand a long task to a fresh session without losing progress\n中文触发:新对话\"接着上次\" / 上下文快满 / 用户说\"我说过了\" / 每轮重读同样的规则待办 / 开场烧掉几万 token / 长任务交接"
description_zh: "跨会话记忆恢复:新对话不再冷启动——身份/规则/待办常驻,变更索引把次要文件的重复读砍掉,恢复成本降约 70%。纯本地、零依赖。"
description_en: "Cross-session memory recovery: a new chat never cold-starts — identity, rules and todos stay loaded, and a change index cuts the redundant re-reads (~70% cheaper recovery). Pure local, zero deps."
author: TXJ · 天玄镜 (Tianxuanjing)
license: MIT-0
metadata:
  hermes:
    tags: [memory, recovery, session, onboarding, context, rules, handover]
    related_skills: []
---

# ChangSheng

**Use when**: a new chat asks where you left off · context is filling up mid-task · the user says "I already told you this" · you re-read the same identity/rules/todos files every session · session start burns tens of thousands of tokens · you hand a long task to a fresh session.

**Key commands**: `python scripts/memory_index.py` (discover + write the change index) · `python scripts/rule_gate.py --check "<action>"` (optional action-time rule gate) · say **"handover"** to snapshot where work stands.

**Cost**: recovery ~44K → ~12K tokens (~70% less); ~55-75% cumulative when the host already injects identity (measured 2026-09-04). Pure local, zero API cost.

Progressive memory recovery for AI agents: your assistant stops losing context between sessions, without re-reading everything every time. ChangSheng first **discovers where your memory actually lives** (your files, your layout), then hands the agent a **shift handover** at session start.

Every new session feels like "day one at work"? This skill makes the agent read what matters (identity, rules, todos, latest work log), check an auto-generated **change index** before re-reading secondary files, and defer everything else until actually needed.

## Platform support
**中文**:各平台怎么用——Hermes 丢进 skills/ 再粘 assets/agents-snippet.md;ClawHub 装 changsheng-agent-memory 或复制目录;Claude Code / Cursor / Codex 复制目录并让 agent 跟 SKILL.md;任意 LLM + 任意系统都能跑(纯约定 + 一个 Python 标准库脚本)。

| Platform | How to use |
|---|---|
| **Hermes** (Nous Research) | Drop this folder into the agent's `skills/` directory, then paste `assets/agents-snippet.md` into `.hermes.md` or `AGENTS.md` → recovery runs automatically (saying "recover memory" per session still works). Hermes injects SOUL/MEMORY/USER automatically — the skill detects host-injected identity and skips duplicate reads (the 55-75% cumulative savings case). |
| **ClawHub / OpenClaw** | Frontmatter is dual-compatible (standard fields + `metadata.hermes`). Install via `clawhub install changsheng-agent-memory` or copy into the agent's skills dir. |
| **Claude Code / Cursor / Codex / other SKILL.md agents** | Copy this folder into the project or agent skills directory; at the start of a session, instruct the agent to follow SKILL.md (the procedure is model-agnostic). |
| **Any LLM, any OS** | Recovery logic is pure convention + one Python stdlib script — model-agnostic, runs on Windows/macOS/Linux, no GPU. |

## What it gives you
**中文**:给你什么——身份 / 规则 / 待办常驻,新会话接着上次;恢复从 ~44K 掉到 ~12K token(省约 70%,宿主已注入身份时累计 55-75%);100% 本地、零 API 花费;上下文用到 30/50/70% 档会被提醒。

- 🧠 **No more lost context**: identity, rules, todos always loaded — nothing important silently dropped; new sessions resume where you left off
- 📏 **Rules remembered**: the do's and don'ts you told your agent are re-stated at every recovery — and (where your platform supports hooks) enforced at action time. "It keeps forgetting I told it not to…" — that ends here
- 🔁 **One-line handover**: say "handover" at any task break; the next session starts exactly where you stopped
- ⚡ **Fast + cheap**: recovery cost ~44K → ~12K tokens (~70% less); with host-injected identity skipped, ~55-75% cumulative (measured 2026-09-04)
- 🔒 **100% local**: pure local scripts, zero API cost, nothing leaves your machine
- 📊 **Context health**: see your real context usage and get nudged as you approach the 30/50/70% lines by default (tunable via config) — and well before a session bloats

## How it works
**中文**:三层——L3 每会话必读(小且固定)/ L2 只在变更索引标记「有变」时才读(省钱就在这)/ L1 按需读;引擎 = scripts/memory_index.py(md5 + 24h 窗口)。

| Layer | Reads | When | Cost |
|---|---|---|---|
| **L3 Must-read** | identity / rules / todos / latest journal | Every new session — the reliability anchor | small, fixed |
| **L2 Conditional** | other tracked files | **Only if the change index flags a change**; otherwise just the index summary line | ≈0 ← savings live here |
| **L1 On-demand** | detail docs / history | Only when actually needed | 0 |
| **Dreaming write-side** | the content side (scattered rules, look-alike entries, stale leftovers) | every 3-day cycle | zero-token prescan + one tidy session |

The engine is `scripts/memory_index.py`: it **discovers** your memory files (role → real file), then hashes every L2-tracked file and flags only what changed (md5 + 24h window). No index → you either re-read everything (expensive) or gamble (risky). With the index you get **neither**.

## Setup (≈30 seconds)
**中文**:约 30 秒——`python scripts/memory_index.py --list .` 先预览发现结果,再不带参数跑一次建索引,`--demo` 自测;默认零配置(要调再 copy config.example.yaml)。

```bash
# 1. get the skill (already done if you installed from ClawHub)
git clone https://github.com/ccy123abcd/changsheng-agent-memory.git
cp -r changsheng-agent-memory ~/.claude/skills/changsheng   # or your agent's skills dir

# 2. cold start: no config needed — discovery finds your memory layout
cd changsheng-agent-memory
python scripts/memory_index.py --list .    # preview what discovery finds (nothing written)
python scripts/memory_index.py             # cold start: discover + write index

# 3. (optional) tune: copy config.example.yaml → config.yaml, set mode/roles/extras
#    or edit .changsheng/discovery.json to override a discovered role

# 4. self-test
python scripts/memory_index.py --demo
```

Discovered roles are cached in `.changsheng/discovery.json` — the agent reads it at recovery instead of re-scanning every session. Delete that file (or any discovered source) and it re-discovers automatically.

**Want it to run without being asked?** Paste `assets/agents-snippet.md` (shipped with this skill) into your project's instruction file — `AGENTS.md`, or `.hermes.md` on Hermes. Hermes, OpenClaw and DeepSeek Harness load that file at session start, so the procedure above runs by itself: no code, no hooks, no config.

## Usage (start of every new session)
**中文**:每会话开场 7 步——发现并 stat 路径 → 读 L3 必读 → 规则对齐并写 rules.json(2b)→ 读变更索引 → 按需 L1 → 报真实上下文用量 → 读并删 handover → 如实报恢复结果(空项要点名)。

1. **Step 0 — Discover (first time or when sources moved)**: run `python scripts/memory_index.py --discover .` — it locates your memory carriers by common conventions (candidate list lives in the script header constants) and writes `.changsheng/discovery.json`. Python unavailable? Fall back to the hand-list below (derived from the script; the script is authoritative). At every recovery, first **stat the stored paths** — any missing/unreadable source triggers re-discovery (never reuse stale paths).
2. **Read the L3 must-read files**: roles resolved in step 0/1 (rules, identity, todos, journal) + `must_read_extra`. Every one, no shortcuts. Host injected identity (Hermes/OpenClaw)? Mark `identity ✅ (host)` and skip the file probe.
2b. **Rules alignment**: from the rules file(s) just read, extract every imperative rule the user stated (do X / never do Y). List them explicitly in your recovery report — this is the moment the user experiences as *"it remembered what I told it"*. Then write/refresh `.changsheng/rules.json` (id, text, keywords per rule) so the guardrail can enforce them at action time (see Rules & guardrails). If the rules file is empty or has no imperative rules, say "no hard rules found" honestly.
3. **Read the change index** `memory_index.md`:
   - ✅ new change → read that file in full
   - ⏸ unchanged → read only its index summary line ← **savings live here**
4. **L1 on-demand**: consult detail docs only when a task actually needs them.
5. **Context gauge**: report real context usage — query your platform (Hermes `/status`; Claude Code `/context`; others: see the platform table below). Never invent a percentage; if the platform exposes none, say so. Optionally append `context: N%` to your recovery report. **If `config.yaml` exists with `nudge_thresholds`, read it once and use those lines instead of the 30/50/70 defaults below** (this is how the user tunes when to be nudged).
6. **Check for a handover note**: if `.changsheng/handover.md` exists, read it first (it is the fast pointer to where the last session stopped), then **delete it** — a handover is a one-shot note; keeping it would make the third session read a stale pointer. Authority stays with todos/journal — the handover only accelerates.
7. **Report recovery honestly**: `identity ✅ (host) · rules ✅ CLAUDE.md · todos ✅ docs/TODO.md · journal ✅ journal/2026-09-04.md · rules aligned: 3 (r1 never delete without asking · r2 reply in Chinese · r3 …)`. If a role came up empty, list it explicitly — never claim a full recovery that didn't happen.

### Context threshold nudges

Check context usage **every time you see it** (at recovery, and after every user turn when your platform exposes a gauge) — usage is a snapshot that jumps between turns: this turn may read 29%, the next 49%. Never assume the last reading still holds, and never wait for a threshold to be crossed before speaking up. **Nudge when you are approaching a threshold too** — a jump can skip a band entirely.

**Hard rule — the nudge is the ready signal.** Before ANY nudge goes out — pre-nudge or full nudge — refresh `.changsheng/handover.md` with a one-line snapshot of where work stands (current task · what's done · what's next). The user may switch sessions the moment they read the nudge, and they must lose nothing. A nudge without a ready handover is not a nudge — it is a trap. If the user then says "handover" or switches, the handover is already there.

**Thresholds are user-tunable.** The default three lines are **30 / 50 / 70%** with a pre-nudge band 5 points below each. Users who want more headroom can shift the whole ladder — e.g. set the first line to 35 (default example: 30/50/70 → 35/55/75) by editing the band table in this file or their config's `nudge_thresholds` if present. Whatever the numbers, keep the *shape*: a pre-nudge band below each line (line − 5), a calm mid-band, and an urgent top band ("switch now"). Defaults:

| Usage | What to say (handover is refreshed first, always) |
|---|---|
| < 25% | healthy — nothing to say |
| 25–30% | pre-nudge: "context is approaching the 30% line — I've noted where we are, so a switch stays safe and cheap" |
| 30–45% | fine — keep working; a task boundary is still a fine moment to switch |
| 45–50% | pre-nudge: "approaching 50% — I've noted where we are; plan to wrap up the current task at its boundary and switch" |
| 50–65% | suggest: "task boundary reached? Good moment to switch to a fresh session — recovery is ~12K tokens, nothing is lost. Handover is ready." |
| 65–70% | pre-nudge: "approaching 70% — I've noted where we are; wind down the current task, the next boundary should be a switch" |
| ≥ 70% | recommend: "wrap up the current task and switch — this context is near its ceiling. Handover is ready." |

With custom thresholds (e.g. 35/55/75), the bands move to match: pre-nudge at line−5, calm below the first line, urgent at the top line. The principle never changes: **never let a reading pass in silence just because it did not cross a line — and never nudge without a ready handover.**

Switching is safe and cheap: that is the whole point of ChangSheng (recovery ≈ 12K tokens instead of tens of thousands of re-explaining).

### Platform context queries

| Platform | How to see context usage |
|---|---|
| Hermes | `/status` (usage %) |
| Claude Code | `/context` (window + usage — convert to %) |
| Cursor | composer status / model context indicator |
| OpenClaw | session/context indicator (varies by build) |
| unknown | report "this platform exposes no context gauge" — do not invent a number |

## Rules & guardrails
**中文**:规则也是记忆——对齐层每会话复述你定的规则;执行层把禁令写进 .changsheng/rules.json,由 scripts/rule_gate.py 在动作前拦(命中退出码 2,失败开放、只拦禁令)。

ChangSheng treats your rules as **memory too** — the most important kind. Two layers make them stick:

**Alignment layer (every session).** At recovery (step 2b) the agent restates the imperative rules it found in your rules files — do's and don'ts alike. You see, in plain text, that what you set is loaded. No rule file yet? Write your rules in `CLAUDE.md`/`AGENTS.md`/your rules file — plain sentences work: *"Never delete files without asking."* *"Always reply in Chinese."* *"Ask before sending anything externally."*

**Enforcement layer (where the platform supports it).** Prohibitions you never want broken ("never", "don't", "always ask first") get written to `.changsheng/rules.json` (id / text / keywords), and a tiny local gate script checks every action before it runs:

```bash
python scripts/rule_gate.py --check "delete the whole project folder"
# ⛔ blocked — violates rules you set: [r1] Never delete files without asking
# exit code 2 → the platform hook refuses the action
```

**Claude Code** — wire it with a PreToolUse hook (settings `.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command",
            "command": "python ~/.claude/skills/changsheng/scripts/rule_gate.py" }
        ]
      }
    ]
  }
}
```

The gate reads the tool name + input from stdin, checks it against your rules, and exits 2 on a hit — Claude Code aborts the tool call. No hook support on your platform? The alignment layer still applies (the agent self-checks before actions) — but enforcement is only as hard as your platform allows.

The gate is pure stdlib, fails open (no rules file → pass), and writes nothing. It only ever blocks *prohibitions* (never / don't / always-ask-first) — positive rules ("always do X") are carried by the alignment layer, since an action gate cannot enforce them mechanically.

## Handover protocol
**中文**:说一句「handover」就把 .changsheng/handover.md 写出来(✅ 做完 / 📌 遗留 / 🔗 指针 / ➡️ 下一步);新会话读一次即删;任何提醒(含预备提醒)发出前必须先刷新它,只有主会话能写。

Switching sessions is only free if the *next* session knows where the last one stopped. Say **"handover"** (or "交接/收尾") at any task break — a natural stopping point, a finished task, or when a context nudge suggests switching — and the agent writes `.changsheng/handover.md` from the template (assets/handover-template.md): ✅ done (what matters next) · 📌 leftover (what's waiting, on whom) · 🔗 pointers (files/tasks that anchor it) · ➡️ next step. Each new handover **overwrites** the previous one; recovery reads it once and **deletes it** (step 6) — a consumed handover must never linger as a stale pointer.

The nudge bands above are the hard rule: **any nudge — pre-nudge or full nudge — goes out only after `.changsheng/handover.md` has been refreshed** (see Context threshold nudges). A nudge without a ready handover is just anxiety, not a safe suggestion. Recovery reads the handover if present (step 6); authority always stays with todos/journal, the handover is the fast pointer.

Two more rules keep the handover trustworthy when it matters most:

- **Refresh before you report.** Anything that *ends* a working stretch — a wrap-up message, a stage summary, a "done" report — refreshes `.changsheng/handover.md` **before** it goes out. A report sent on top of a stale handover is a lost thread: the user reads "done", starts a fresh session, and lands on the previous state.
- **Single writer.** Only the interactive main session writes the handover. Sub-agents, background workers and scheduled jobs never write it — with several writers each holding its own idea of "the current state", the last one to finish silently overwrites the others.

## Dreaming — the write side (every 3 days)
**中文**:写侧——每 3 天把内容面理一遍(同类归并 / 相似辨清 / 过期清理 / 新增归位 / 存疑上抛),每类都带可核判据,产物是一页梦报;本技能只给纪律与判据,不新建任何定时任务或脚本。

Recovery is the read side; dreaming is the write side — the same memory, the other half.

On each pass the agent tidies what it has stored, with five moves; every move carries a
checkable criterion, so this never degrades into a feeling exercise:

- **Merge duplicates** — the same fact stored in two places; criterion: its grep count drops.
- **Split look-alikes** — two near-identical entries that mean different things; criterion: one line written beside them saying where each ends.
- **Retire stale entries** — criterion: check first, keep the newest, back up before anything is deleted.
- **Re-home new entries** — criterion: the hook word is recorded (where this entry gets read from).
- **Escalate doubts** — anything you cannot call goes into the report; nothing is decided alone.

Rhythm: once per 3-day cycle — criterion: at least 3 days since the last content-side pass.
Output: a one-page dream report, written for the reader, not for the archive.

Boundary: this skill ships discipline and criteria only. It does not create jobs or scripts of
its own — scheduling belongs to your host's timer, and reorganisation never touches directories
you cannot read.

Source note: this borrows the ecosystem's content-side idea (tidy the memory itself), not its
engineering; nothing here depends on another implementation.

## Manual discovery fallback (Python unavailable)
**中文**:没有 Python 时的手工找法——规则 / 身份看 CLAUDE.md、AGENTS.md、.cursor/rules;待办看 TODO.md / todo.txt / tasks.md;日志取 journal、logs、notes 下最新的 YYYY-MM-DD.*。

Look for, in order (the script header candidate constants are authoritative — this is a summary):

- **rules/identity**: `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/` in the project; `~/.claude/CLAUDE.md` in home (candidate constants in the script header are authoritative)
- **todos**: `TODO.md` / `todo.md` / `todo.txt` / `tasks.md` (root or `docs/`); `~/todo.txt` or `~/.todo/` (todo.txt-cli)
- **journal**: newest `YYYY-MM-DD.md/.txt` under `journal/`, `logs/`, `notes/`, or `docs/journal/`
- **profile**: only if you configured one

## Files
**中文**:文件清单——scripts/memory_index.py(变更索引)+ scripts/rule_gate.py(可选动作闸门)、assets/ 两个模板、config.example.yaml;产物落 .changsheng/ 与 memory_index.md(_state.json)。

- `scripts/memory_index.py` — discovery + change-index generator (pure stdlib; `--discover` / `--list` / `--demo` / `--mode internal|auto|manual`)
- `scripts/rule_gate.py` — optional action-time guardrail (reads `.changsheng/rules.json`; `--check "desc"` or PreToolUse stdin; `--demo`)
- `assets/handover-template.md` — handover note template
- `assets/agents-snippet.md` — paste-in block for your project's instruction file (Hermes / OpenClaw / DeepSeek Harness), so recovery runs at session start with no hook
- `config.example.yaml` — configuration template (mode / roles / extras)
- Outputs: `.changsheng/discovery.json` + `memory_index.md` + `memory_index_state.json` + (optional) `.changsheng/rules.json` + `.changsheng/handover.md`

## Security
**中文**:安全——发现只按文件名扫(不看内容),索引只哈希你列出的文件,从不改你的记忆文件,什么都不上传;纯 Python 标准库,PyYAML 可选。

- Discovery scans candidate paths by **name only** (metadata, no content) and writes `.changsheng/discovery.json`; the index reads and hashes only files you listed (roles + extras)
- Never writes your memory files themselves — its own outputs are limited to `.changsheng/discovery.json`, the index md + state json, plus two optional files the agent maintains at your request: `.changsheng/rules.json` (your extracted rules, for the optional gate) and `.changsheng/handover.md` (your one-shot handover note, deleted after being read)
- Nothing is uploaded anywhere — fully local, no remote install pipelines, no script-to-shell execution
- Python standard library only. PyYAML optional: when absent, a built-in fallback parser reads the config (nested `roles:`, extras, flat `role_*` keys) — no silent config loss

## Roadmap (managed edition)
**中文**:路线图——自动用户画像(偏好 / 习惯)、跨设备同步 + 网页控制台、一键部署;不想自己配就等托管版(零配置、持续更新)。

- Auto user-profiling (preferences / habits)
- **0.6.0 — Dreaming (write side) + a Chinese line under every section.**
- Cross-device sync + web console
- One-click deploy — don't want to self-configure? Managed edition = zero-setup, full system, continuous updates. → [Managed edition entry: TBD]

## License
**中文**:许可——MIT-0,可自由使用、修改与出售。

MIT-0 — free to use, modify, and sell.
