# Lore

[English](#lore) · [中文](#lore-项目说明)

---

**Turn your project's lived history into structured, cross-referenced, git-tracked memory.**

`timeline` · `checkpoint` · `recall` · `lore` · `legacy`

Lore is a Claude Code / Cursor plugin. It captures deploys, experiments, decisions, failed attempts, incidents, and releases as typed markdown records under `.lore/`, then distills them into reusable project canon.

Its anchor skill — `lore:try-failed-exp` — gives every project a place to record the things that *didn't* work, so future engineers don't retry them blindly.

## The cooling pipeline

```
LIVE (流)  ──────►  ARCHIVE (档)  ──────►  CANON (典)
raw signal          crystallized event       reusable rule
journal             postmortem               codex
intent-log          retro                    try-failed-exp
                    release-notes            migration-guide
```

Information flows cold-ward over time. Lore makes the transitions first-class.

## v0.1 skill set

| Layer | Skill | What it does |
|-------|-------|-------------|
| Archetype | `lore:journal` | Record a discrete event — deploy, incident, rollback |
| Archetype | `lore:codex` | Record a decision — ADR, design choice, adopted convention |
| Archetype | `lore:try-failed-exp` | Record an attempt that failed — evaluated but rejected, spiked and abandoned |
| Adapter | `lore:harvest` | Batch-review candidate records staged from git history |
| Meta | `lore:detect` | First-run scan + ambient signal detection |
| Meta | `lore:promote` | Cooling-pipeline operator: surfaces live → canon promotion candidates |
| Primer | `lore:using-lore` | Injected every session via SessionStart hook |

## Installation

### Claude Code

```bash
/plugin install lore
```

### Cursor

Search **"lore"** in the plugin marketplace, or add manually:

```text
/add-plugin lore
```

### Manual (any platform)

```bash
# In your project root
curl -fsSL https://raw.githubusercontent.com/host452b/lore.skill/main/install.sh | bash
```

Codex, OpenCode, and Gemini CLI install shims land in v0.2.

## First session

1. Install the plugin.
2. Start a fresh session — the SessionStart hook injects the `using-lore` primer automatically.
3. Run `lore:detect` — it scans your git history and suggests a starter set.
4. Run `lore:harvest` — it stages candidate records from git for you to confirm.
5. Write your first `lore:try-failed-exp` or `lore:codex` in under 2 minutes.

No config file required.

## Where records live

```
<your-project>/
└── .lore/
    ├── live/     ← high-churn events: journal, intent-log
    ├── archive/  ← one-time retrospection: postmortem, retro, release-notes
    └── canon/    ← reusable rules: codex, try-failed-exp, migration-guide
```

Git-tracked by default. Your lore ships with your repo.

## Design

Full architectural charter: [`docs/superpowers/specs/2026-04-17-lore-charter-design.md`](docs/superpowers/specs/2026-04-17-lore-charter-design.md)

Covers: cooling-pipeline thesis · 11 archetype skills · 5-layer architecture · install architecture · roadmap v0.1 → v1.0.

## License

MIT © host452b

---

# Lore 项目说明

**将项目的活历史变成结构化、可交叉引用、git 追踪的项目记忆。**

`timeline 时间线` · `checkpoint 检查点` · `recall 回溯` · `lore 典藏` · `legacy 遗产`

Lore 是一个 Claude Code / Cursor 插件。它将部署、实验、决策、失败尝试、故障和发布记录为 `.lore/` 目录下带类型的 Markdown 文件，并将它们提炼成可复用的项目典藏。

核心技能 `lore:try-failed-exp` 为每个项目提供一个专门记录"什么行不通"的地方，让未来的工程师不会盲目地重蹈覆辙。

## 冷却管道模型

```
LIVE（流）──────►  ARCHIVE（档）──────►  CANON（典）
原始信号             一次性回顾              可复用规则
journal             postmortem             codex
intent-log          retro                  try-failed-exp
                    release-notes          migration-guide
```

信息随时间向"冷端"流动。Lore 将这些转变变为一等公民。

## v0.1 技能清单

| 层级 | 技能 | 用途 |
|------|------|------|
| 原型 | `lore:journal` | 记录离散事件——部署、故障、回滚 |
| 原型 | `lore:codex` | 记录决策——ADR、设计选型、已采纳的规范 |
| 原型 | `lore:try-failed-exp` | 记录失败尝试——评估后拒绝、试探后放弃的方案 |
| 适配器 | `lore:harvest` | 从 git 历史批量生成候选记录，逐一确认 |
| 元技能 | `lore:detect` | 首次扫描项目 + 会话中主动识别记录信号 |
| 元技能 | `lore:promote` | 冷却管道操作器：找出应从 live 升级到 canon 的记录 |
| 引导 | `lore:using-lore` | 每次会话通过 SessionStart hook 自动注入 |

## 安装

### Claude Code

```bash
/plugin install lore
```

### Cursor

在插件市场搜索 **"lore"**，或手动添加：

```text
/add-plugin lore
```

### 手动安装（任意平台）

```bash
# 在项目根目录执行
curl -fsSL https://raw.githubusercontent.com/host452b/lore.skill/main/install.sh | bash
```

Codex、OpenCode、Gemini CLI 的安装适配器将在 v0.2 中提供。

## 第一次使用

1. 安装插件。
2. 开启新会话——SessionStart hook 会自动注入 `using-lore` 引导技能。
3. 执行 `lore:detect`——扫描 git 历史，推荐入门记录集合。
4. 执行 `lore:harvest`——从 git 提交生成候选草稿，逐一确认是否保留。
5. 两分钟内写出第一条 `lore:try-failed-exp` 或 `lore:codex`。

无需配置文件即可上手。

## 记录存储位置

```
<你的项目>/
└── .lore/
    ├── live/     ← 高频事件：journal、intent-log
    ├── archive/  ← 一次性回顾：postmortem、retro、release-notes
    └── canon/    ← 可复用规则：codex、try-failed-exp、migration-guide
```

默认纳入 git 追踪，lore 记录随代码仓库一起分发。

## 设计文档

完整架构 Charter：[`docs/superpowers/specs/2026-04-17-lore-charter-design.md`](docs/superpowers/specs/2026-04-17-lore-charter-design.md)

内容涵盖：冷却管道模型 · 11 种原型技能 · 5 层架构 · 安装架构 · 路线图 v0.1 → v1.0。

## 许可证

MIT © host452b
