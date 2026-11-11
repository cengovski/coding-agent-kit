# coding-agent-kit

An original, tool-agnostic **skills kit and operating manual for AI coding agents**. Give it to Claude Code, Cursor, Copilot, Codex, or any agent that reads repo instructions, together with a product request, and the agent follows one disciplined workflow:

**clarify → choose a boring stack → plan → build in small verified steps → test (E2E when there is a UI) → harden → self-review → ship.**

It is not a framework and not a sample app. It is a set of short, focused instructions agents load on demand.

## What's inside

```
AGENTS.md                      ← agents read this first (single source of truth)
CLAUDE.md                      ← pointer for Claude Code
.cursor/rules/coding-agent-kit.mdc  ← pointer for Cursor
.github/copilot-instructions.md     ← pointer for GitHub Copilot
.claude/skills → skills/       ← so Claude Code discovers the skills natively
skills/<name>/SKILL.md         ← 19 focused skills (YAML frontmatter + procedure)
templates/                     ← SPEC, PLAN, PR, README, .env.example, project-facts
checklists/                    ← definition of done, new-app kickoff
scripts/validate-skills.sh     ← checks skill frontmatter
templates/ci/validate-skills.yml ← optional CI workflow (copy to .github/workflows/)
SOURCES.md                     ← inspirations and attribution
```

### Skills

| Phase | Skills |
|---|---|
| Orient | `using-this-kit` |
| Clarify & design | `clarifying-requests`, `architecture-and-stack`, `api-design`, `data-modeling` |
| Plan & build | `planning-work`, `implementation-discipline`, `test-driven-development`, `typescript-quality`, `python-quality`, `current-docs-lookup` |
| UI | `e2e-testing-playwright`, `ui-accessibility` |
| Harden | `security-and-secrets`, `error-handling-and-config` |
| Fix | `systematic-debugging` |
| Finish | `verification-before-done`, `self-review`, `git-and-pr-hygiene` |

## Starting a new app with the kit

Pick one of three ways.

### A. Use it as the starting point of your new repo (recommended)
```bash
git clone https://github.com/cengovski/coding-agent-kit.git my-app
cd my-app
rm -rf .git && git init            # start fresh history for your app
```
Or click **Use this template** on GitHub if the repo is marked as a template. Then open your agent in `my-app` and give it a request, for example:

> Read AGENTS.md and follow it. Build a habit-tracker web app: users sign in, add daily habits, check them off, and see a 30-day streak. Start with the clarifying-requests skill and write SPEC.md.

The agent writes `SPEC.md` and `PLAN.md`, scaffolds the app next to the kit files, and works through the plan. Afterwards, fill the **Project facts** section (from `templates/PROJECT_AGENTS.md`) with your real commands.

### B. Add the kit to an existing repo
Copy `AGENTS.md`, `CLAUDE.md`, `skills/`, `templates/`, `checklists/`, and the pointer files (`.cursor/`, `.github/copilot-instructions.md`, `.claude/`) into the repo root. If the repo already has an `AGENTS.md`, merge: keep its project facts, add the kit's rules.

### C. Point the agent at this repo
If you don't want the files in your project, tell the agent:

> Before coding, read https://github.com/cengovski/coding-agent-kit — AGENTS.md first, then load skills from skills/ as each phase needs them. Follow it for this project.

(Works best with agents that can browse or clone.)

## How agents load it

1. Read `AGENTS.md` (core rules + workflow table + definition of done).
2. Open `skills/using-this-kit/SKILL.md` to classify the task and pick skills.
3. Load each other skill only when its phase starts (progressive disclosure keeps context small).
4. Before finishing, walk `checklists/definition-of-done.md` and report evidence.

Claude Code also auto-discovers the skills via `.claude/skills/` (a symlink to `skills/`; on Windows without symlink support, copy the folder instead).

## Core rules (summary)

- Ship something that **runs** from a clean checkout.
- **Verify** every change with real checks — tests, typecheck, lint, build, and E2E for UIs — and show the output.
- **Never invent library APIs**; check current official docs (or a docs MCP like Context7) for the installed version.
- Prefer **boring, well-maintained** stacks and few dependencies.
- **Ask only when it's consequential**; otherwise choose a default and record it.
- **No secrets in source**; `.env.example` only.

## Tips for the human

- Rules an agent must *never* break (e.g. "never edit migrations") are better enforced by hooks, CI, branch protection, or deny rules than by text. Treat this kit as guidance and add enforcement where it matters.
- Keep the project-facts section short. Only write what an agent can't learn by reading the code.
- Start a fresh session for building after the spec is written, and use a second session (or subagent) as an independent reviewer.

## Contributing / changing skills

Each skill is `skills/<name>/SKILL.md` with frontmatter `name` (equal to the folder, lowercase-hyphenated) and `description` (what it does and when to use it). Keep skills short and procedural. Run `./scripts/validate-skills.sh` before committing. To run it in CI, copy `templates/ci/validate-skills.yml` to `.github/workflows/`.

## License and attribution

MIT — see [LICENSE](LICENSE). This kit is original work; see [SOURCES.md](SOURCES.md) for the projects and docs that inspired it.

---

## Türkçe özet

**coding-agent-kit**, yapay zekâ kodlama ajanları (Claude Code, Cursor, Copilot vb.) için hazırlanmış özgün bir beceri (skill) kiti ve çalışma kılavuzudur. Ajan bu repoyu okuyunca şu sırayla çalışır: isteği netleştir → sade ve kanıtlanmış bir teknoloji seç → planla → küçük ve test edilmiş adımlarla kodla → test et (arayüz varsa Playwright ile E2E) → güvenliği kontrol et → kendi kodunu gözden geçir → teslim et.

**Yeni bir uygulamaya nasıl başlanır?**
1. Repoyu yeni proje klasörü olarak klonla: `git clone https://github.com/cengovski/coding-agent-kit.git uygulamam && cd uygulamam && rm -rf .git && git init`
2. Ajanı bu klasörde aç ve şöyle yaz: *"AGENTS.md dosyasını oku ve uygula. Şu uygulamayı yap: … clarifying-requests skill'i ile başla ve SPEC.md yaz."*
3. Ajan önemli konularda (kapsam, veri modeli, giriş sistemi, ödeme gibi) tek seferde birkaç soru sorar; geri kalanında makul varsayımlar yapıp SPEC.md'ye yazar.
4. Ajan PLAN.md oluşturur, uygulamayı kurar ve her adımı testle doğrulayarak ilerler. Sonunda hangi komutları çalıştırdığını ve sonuçlarını raporlar.
5. Proje oturunca `AGENTS.md` sonuna "Project facts" bölümünü (şablon: `templates/PROJECT_AGENTS.md`) gerçek komutlarınla doldur.

Not: Skill dosyaları İngilizcedir, çünkü ajanlar İngilizce talimatları daha güvenilir uygular. Ajanla Türkçe konuşabilirsin. Gizli anahtarları (API key, şifre) asla koda yazma; yalnızca `.env` dosyasında tut, repoya sadece `.env.example` eklenir.
