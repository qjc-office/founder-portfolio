# Task 34 — Plugins Spec Audit (verdict: HYBRID — keep as Skill, ship via Plugin marketplace later)

## TL;DR

Claude Code Plugins **are** a real, GA-stable spec as of 2026-05. The canonical docs live at `code.claude.com/docs/en/plugins` and `…/plugins-reference`. Anthropic launched the plugin marketplace with Claude Code 2.0.13 on/near 2025-09-29 [T1] and currently lists ~101 plugins (33 Anthropic-built) [T3]. **However**, for our `founder-portfolio` MVP the right move is to **stay as a Skill** and only convert when there is real demand to redistribute. Migration is mostly mechanical (drop in `.claude-plugin/plugin.json`, replace `~/.claude/skills/...` paths with `${CLAUDE_PLUGIN_ROOT}`) but introduces three real costs: namespacing (`/founder-portfolio:render`), a Python venv distribution problem, and ongoing OpenAI key management for end users. The "let other people use my skill" goal can be satisfied 80% with a GitHub repo + `git clone ~/.claude/skills/founder-portfolio` install command — no plugin format required.

## Sources (Tier 0 + freshness date)

- [T0] [Create plugins — Claude Code Docs](https://code.claude.com/docs/en/plugins) · accessed 2026-05-02 — canonical authoring guide
- [T0] [Plugins reference — Claude Code Docs](https://code.claude.com/docs/en/plugins-reference) · accessed 2026-05-02 — schema, CLI, env vars, hooks list
- [T0] [Anthropic official plugin marketplace](https://github.com/anthropics/claude-plugins-official) · accessed 2026-05-02 — `.claude-plugin/marketplace.json` reference
- [T0] [Create custom subagents — Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code/sub-agents) · accessed 2026-05-02 — agent constraints inside plugins
- [T1] [Claude Code 2.0.13 release notes summary (Medium, Reza Rezvani)](https://alirezarezvani.medium.com/claude-code-2-0-13-be2c0a723856) · accessed 2026-05-02 — Plugin marketplace launch in 2.0.13 (≈2025-09-29). Tier 1 only because the post is secondary; the underlying CHANGELOG is at docs.anthropic.com/en/release-notes/claude-code [T0] but I did not fully fetch it for this audit — flag for re-verification.
- [T3] [Pete Gypps — Official Plugin Marketplace 36 plugins](https://www.petegypps.uk/blog/claude-code-official-plugin-marketplace-complete-guide-36-plugins-december-2025) · accessed 2026-05-02 — counts at Dec 2025, used only for trend, not facts
- [T3] [BuildToLaunch — Best Claude Code Plugins 2026 (10 tested, 4 worth keeping)](https://buildtolaunch.substack.com/p/best-claude-code-plugins-tested-review) · accessed 2026-05-02 — independent quality assessment

## Findings

### 1. Where is the canonical Claude Code Plugins documentation?

`code.claude.com/docs/en/plugins` (authoring) and `code.claude.com/docs/en/plugins-reference` (schema). Both are part of the official Anthropic docs portal (same domain as the Agent SDK docs). The page-table-of-contents lists complete sub-sections: manifest schema, CLI commands (`plugin install/uninstall/prune/enable/disable/update/list/tag`), debugging tools, distribution & versioning. There's also `code.claude.com/docs/en/discover-plugins` and `…/plugin-marketplaces` for the consumer/distribution side. Status: **stable, well-organized, complete** — not an experimental preview.

### 2. Structural difference between a Skill and a Plugin

**Skill (standalone)**:
```
~/.claude/skills/founder-portfolio/
├── SKILL.md                ← YAML frontmatter + body
├── scripts/, templates/, …
```
Discovery: auto-loaded from `~/.claude/skills/`. No manifest. No version. Invoked as `/render` (no namespace).

**Plugin**:
```
founder-portfolio/                    ← arbitrary install location
├── .claude-plugin/
│   └── plugin.json                   ← required (only `name` is mandatory)
├── skills/founder-portfolio/SKILL.md ← same skill format, but NESTED
├── agents/, commands/, hooks/hooks.json
├── .mcp.json, .lsp.json
├── monitors/monitors.json
├── bin/, settings.json
```
Discovery: install via `/plugin install`, `--plugin-dir ./local-path` for dev, or marketplace. Skill becomes namespaced: `/founder-portfolio:render`. Lifecycle is real: `plugin install / update / disable / uninstall / prune`. Version field in `plugin.json` controls update flow; if absent, git commit SHA is used.

**Practical difference summary**:
| Dimension | Skill | Plugin |
|---|---|---|
| Manifest | None | `.claude-plugin/plugin.json` required (only `name` mandatory) |
| Install path | `~/.claude/skills/...` | Anywhere; `${CLAUDE_PLUGIN_ROOT}` resolves at runtime |
| Discovery | Auto-load on session start | `/plugin install` or `--plugin-dir` |
| Versioning | None | Semver field or git SHA |
| Bundled components | Skill only | Skill + agents + hooks + MCP + LSP + monitors + bin + settings |
| Invocation name | `/render` | `/founder-portfolio:render` (forced namespace) |
| Update flow | Manual `git pull` / file edit | `/plugin update`, marketplace auto-updates for Anthropic-published |

### 3. Plugin marketplace — does it exist?

**Yes**, both official and community.
- **Official**: `github.com/anthropics/claude-plugins-official` — Anthropic-managed directory. Auto-available in Claude Code 2.0.13+. Auto-update enabled by default. Submission via `claude.ai/settings/plugins/submit` or `platform.claude.com/plugins/submit`.
- **Community**: any Git repo with `.claude-plugin/marketplace.json` at root acts as a marketplace. Examples: `claudemarketplaces.com`, `buildwithclaude.com`, `aitmpl.com/plugins`, `claudepluginhub.com` [all T3]. Teams can host private marketplaces in private repos.

**Sandboxing/review**: The docs do **not** describe any sandboxing of plugin code. Hooks run shell commands, MCP servers run subprocesses, `bin/` adds executables to `PATH`. Submission to the official marketplace presumably has manual curation (no documented automated review pipeline) — this is an **unverified** assumption; the docs do not detail review SLAs. Treat any third-party plugin as you would any `git clone | bash` install.

[T0 docs do not address signing or sandboxing. This is a real security gap, not an oversight to dismiss.]

### 4. What can Plugins do that Skills cannot?

From the reference doc, plugins bundle **all** of these (Skill alone bundles only itself):
- Custom **agents** (`agents/*.md`) — but with security restrictions: `hooks`, `mcpServers`, `permissionMode` are **not** allowed in plugin agents. Only `worktree` isolation supported.
- **Hooks** (`hooks/hooks.json`) on 30+ lifecycle events
- **MCP servers** (`.mcp.json`) — bundled and auto-started
- **LSP servers** (`.lsp.json`) for language intelligence
- **Background monitors** (`monitors/monitors.json`) that emit notifications to Claude
- **`bin/`** directory that gets prepended to the Bash tool's `PATH` while plugin is enabled
- **Default `settings.json`** to e.g. activate a plugin agent as the main thread
- **Versioning + update flow** (`/plugin update`)
- **Persistent data** via `${CLAUDE_PLUGIN_DATA}` (survives updates — relevant for our Python venv!)
- **Distribution via marketplace**

### 5. What can Skills do that Plugins cannot?

- **Short, unnamespaced invocation** (`/render` vs `/founder-portfolio:render`) — minor but real friction
- **Faster iteration** — edit and reload, no install/update cycle
- **Project-local override** in `.claude/skills/` without manifest overhead
- Same **progressive disclosure** and **description-based triggering** semantics. There is **no** disclosure/triggering capability that Skills have but Plugins lack — Plugin Skills inherit identical triggering.

### 6. Conversion path for our MVP (delta)

Concrete steps:

1. **Create manifest** — `mkdir founder-portfolio/.claude-plugin && echo '{"name":"founder-portfolio","version":"0.1.0","description":"Generate founder bio webpages","author":{"name":"…"}}' > founder-portfolio/.claude-plugin/plugin.json`. Only `name` is strictly required.
2. **Move skill body** — `mv SKILL.md scripts/ templates/ data/ assets/ references/ founder-portfolio/skills/founder-portfolio/` (note the doubled name — outer is plugin, inner is skill).
3. **Path rewrites in SKILL.md** — every `~/.claude/skills/founder-portfolio/...` becomes `${CLAUDE_PLUGIN_ROOT}/skills/founder-portfolio/...`. Confirmed by docs: `${CLAUDE_PLUGIN_ROOT}` is substituted inline in skill content, agent content, hook commands, MCP/LSP configs and is also exported as env var to subprocesses.
4. **Caveat on `${CLAUDE_PLUGIN_ROOT}` in command markdown** — there is a known limitation (GitHub Issue #9354) that the variable is **not** substituted in some command markdown contexts — only in JSON configs and shell subprocesses. **Verify against your actual scripts before assuming substitution works everywhere.**
5. **Python venv distribution problem** — venvs are not portable across machines (absolute paths baked into shebangs). Options: (a) require user to `python -m venv` and `pip install -r requirements.txt` in a hook on first install, with the venv stored under `${CLAUDE_PLUGIN_DATA}` so it survives updates; (b) ship a SessionStart or Setup hook that bootstraps the venv. The docs describe `${CLAUDE_PLUGIN_DATA}` as "persistent directory for plugin state that survives updates, for installed dependencies such as node_modules or Python virtual environments" — so this is the **intended** path.
6. **OpenAI API key** — the right pattern is to have the user store the key in their own env (e.g. `~/.claude/.env.secrets` per QJC policy, or Claude Code settings env block) and reference it in the plugin's MCP/script env via `${OPENAI_API_KEY}`. Do **not** ship a config file that asks for the key — it will end up committed somewhere by some user. Document this clearly in README.
7. **Test locally** — `claude --plugin-dir ./founder-portfolio` then `/reload-plugins` to iterate.

**Breaking changes from the current skill**:
- Invocation: `/founder-portfolio:render` instead of `/render`
- Any hardcoded `~/.claude/skills/founder-portfolio` paths break. Grep first.
- If `SKILL.md` references files relative to `~/.claude/...`, those become `${CLAUDE_PLUGIN_ROOT}/...`.

### 7. Skeptical questions

- **Is Plugin the right format if the goal is "let other people use my skill"?** Probably overkill for a single-skill MVP. Plugin format pays off when you have ≥2 components (skill + agent, or skill + hook), or when you need versioned updates, or when you want to be on the marketplace. For one skill with no hooks/agents/MCP, a GitHub repo with a one-liner install is simpler and less brittle.
- **Could the skill stay a skill, hosted on GitHub, with 1-line install?** Yes: `git clone <repo> ~/.claude/skills/founder-portfolio && cd $_ && python -m venv .venv && .venv/bin/pip install -r requirements.txt`. This is genuinely 80% of plugin value with 20% of the friction. No namespacing pollution, no plugin.json maintenance, no marketplace politics.
- **Concrete benefit of Plugin format over `git clone`?** (a) Versioning + `/plugin update` as a first-class UX. (b) Marketplace discoverability (if you submit). (c) Auto-update for users who installed via marketplace. (d) `${CLAUDE_PLUGIN_DATA}` for venv persistence across updates. (e) Ability to ship bundled agents/hooks/MCP later without restructuring. (f) Force-namespacing avoids skill name collisions across users' machines. (a)-(f) are real but only matter if you actually plan to ship updates and have multiple components — premature for an MVP with one skill.
- **Is the Plugin spec stable as of 2026-05?** Yes, with caveats. Plugin marketplace launched in Claude Code 2.0.13 (≈2025-09-29) [T1], so the spec has ~7 months of in-the-wild use. Schema is documented end-to-end. Active GitHub issues exist (e.g. #9354 on `${CLAUDE_PLUGIN_ROOT}` substitution gaps, #27145 on env var not set in `SessionStart` hooks) [T1] showing rough edges but not breaking changes. Treat the spec as **GA-stable**, not as a moving target — but don't expect zero papercuts.

## Recommended migration path (if any)

**Decision: HYBRID, in two phases.**

**Phase A (now, recommended)**: Stay as a Skill at `~/.claude/skills/founder-portfolio/`. Push the directory to a GitHub repo. Add a `README.md` with:
```bash
git clone https://github.com/<user>/founder-portfolio ~/.claude/skills/founder-portfolio
cd ~/.claude/skills/founder-portfolio
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# Add OPENAI_API_KEY to ~/.claude/.env.secrets
```
Cost: ~1 hour. Reach: anyone willing to `git clone`. No namespace breakage. No spec coupling.

**Phase B (only if there's real demand)**: Convert to plugin format. Trigger conditions: ≥3 external users asking for `/plugin install`-style flow, or a need to ship hooks/agents alongside the skill, or wanting marketplace exposure for SEO. Migration is mechanical (~2-3 hours), but it forces `/founder-portfolio:render` namespacing on existing users — communicate the breaking change.

**Do NOT** do Phase B as the first conversion if all you need is "share with others." It's premature. Karpathy 4-rules apply: don't add complexity (manifest, namespace, install/update flow) for a goal that's already satisfiable with a `git clone` line.

## Risks and unknowns

- **Plugin marketplace review SLA / signing / sandboxing**: docs do not address. Submitting to the official marketplace is a black box. If you go Phase B, treat your plugin as untrusted-by-default for users — document everything that runs.
- **`${CLAUDE_PLUGIN_ROOT}` substitution gaps in command markdown** (GH #9354): known issue; behavior may differ across plugin contexts. Test before assuming.
- **`${CLAUDE_PLUGIN_ROOT}` not populated in `SessionStart` hooks** (GH #27145): If you plan a venv-bootstrap hook, use `Setup` event instead of `SessionStart`.
- **Python venv portability**: requires a one-time bootstrap step regardless of skill vs plugin. `${CLAUDE_PLUGIN_DATA}` is the right home in plugin form, but you still own the bootstrap script.
- **OpenAI key UX**: per-user secret. No way for the plugin to "ship" a key. Document this clearly; do not let users paste keys into a config file inside the plugin directory.
- **Claude Code 2.0.13 release date**: I have a Tier 1 secondary citation for "≈2025-09-29." The authoritative `docs.anthropic.com/en/release-notes/claude-code` CHANGELOG should be re-verified before publishing this audit externally.
- **Marketplace plugin counts (33 / 36 / 101)** vary across sources [all T3]. They reflect different snapshot dates, not contradictions, but I did not normalize them against a single Tier 0 timestamp.

---

**Verdict reaffirmed**: Keep the Skill as-is. Ship it via a GitHub repo with a `git clone` README. Convert to a Plugin only when you have a concrete second component to bundle or ≥3 external users asking for `/plugin install` UX. The Plugin spec is mature enough that you can convert later without rewrite — that's the strongest argument for *not* converting prematurely.

*面責 / Disclaimer: AI 보조 리서치 결과물. Tier 0 출처(공식 docs)와 Tier 1 보도/CHANGELOG 인용을 교차검증했으나, marketplace 통계 및 release 날짜 일부는 Tier 1-3 소스. 외부 의사결정에 사용 전 docs.anthropic.com/en/release-notes/claude-code CHANGELOG 1차 재확인 권장.*
