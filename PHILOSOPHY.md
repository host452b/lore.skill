# Philosophy

[English](#philosophy) · [中文](#哲学)

---

## The problem this solves

Every software project accumulates signal. Git commits, deploys, incidents, experiments, decisions — they pile up in real time. But almost no project accumulates *canon*: the distilled, reusable knowledge of what was learned.

The result is a kind of institutional amnesia. A new engineer joins and asks "why do we use PostgreSQL here?" and nobody quite remembers. The team evaluates a new caching strategy, not knowing that eighteen months ago they tried the same one and abandoned it for reasons that were never written down. An architectural decision gets relitigated every six months because the original rationale was only in someone's head.

This is not a knowledge-management failure. It is a *phase-transition* failure. The signal was always there. It just never crystallized.

---

## The cooling pipeline

Information has phases.

Fresh signal is hot — high-churn, fine-grained, ephemeral. A deploy event happened. An experiment ran. An incident resolved. These are facts, and they are useful as facts.

Over time, some of that signal crystallizes into archive: a postmortem, a retro, a release note. One-time retrospection. Still tied to a specific event, but synthesized.

The most durable lessons condense further into canon: reusable rules, standing decisions, recorded rejections. A codex entry: "we use blue-green deploys for this service, and here is why." A try-failed-exp: "we evaluated event sourcing for this problem and concluded it was wrong for our scale."

Most tools optimize one band. Observability tools optimize the hot end. Wikis optimize the cold end — but they are static, untyped, and decay. What almost no tool does is optimize the *transitions*.

Lore's thesis is that the transitions are the hardest part, and that making them first-class changes what a team can know about itself.

---

## Why try-failed-exp is the anchor

The postmortem space is saturated. Jeli, Blameless, FireHydrant — the incident retrospection space has mature tooling, established workflows, and broad adoption.

The "attempted and rejected" space has almost nothing.

And the asymmetry is stark. "Do this" — the affirmative decision — is reasonably well-served by Architecture Decision Records, design documents, and wikis. "Don't do this, and here is exactly why" is almost entirely absent from the tooling landscape.

Every experienced engineer has the same story: "I wish I had known someone already tried that." The knowledge existed. It was in the heads of the people who did the experiment. It evaporated when they left, or when enough time passed, or when the codebase changed enough that nobody connected the new proposal to the old attempt.

`try-failed-exp` is a canon-tier record for exactly this knowledge. It is the mirror image of `codex`: where `codex` says *do this, and here is why*, `try-failed-exp` says *don't do this — unless these specific conditions change*.

That last clause — "unless" — is what makes the record useful long-term.

---

## The falsifiability anchor

The common failure mode of rejection records in other tools is decay. "We tried X, it didn't work" gets written, and then years later nobody remembers the constraints that drove it. The record becomes either ignored ("that was so long ago, circumstances must have changed") or mistakenly treated as a permanent prohibition.

The `## Don't retry unless` section — required on every `try-failed-exp` record — is the solution to this. It forces the author to state specific, falsifiable conditions under which the approach could be revisited:

> *Unless Redis ships native cross-slot transactions in a GA release.*
> *Unless event volume exceeds 50k writes/second sustained.*
> *Unless we have a team with dedicated Rust expertise for the critical path.*

This turns a fuzzy "no" into a conditional. A future engineer reading the record can check: have these conditions changed? If they have, the record doesn't block — it informs. If they haven't, the record explains exactly why this is still the wrong time.

The falsifiability anchor is what distinguishes lore from a prohibition list.

---

## What lore is not optimizing for

**Completeness.** Not every deploy needs a record. Not every decision needs a codex entry. Lore's value is in the records that would be *worth finding three years from now* — the decisions with non-obvious rationale, the experiments that reached conclusions, the rollbacks that carried lessons.

**Automation.** Lore produces candidates. Humans confirm. The agent can mine your git history, classify commits, draft frontmatter, and stage files. But it does not write canon records autonomously. Every record that lands in `.lore/canon/` has been read and confirmed by a human. This is a deliberate constraint, not a limitation.

**Exhaustive documentation.** API documentation belongs in docstrings. Architecture overviews belong in `docs/`. Sprint tickets belong in your issue tracker. Lore is for the *lessons learned* layer — the layer most often absent.

**Permanence without curation.** The cooling pipeline implies that not everything survives the transition. A `journal` entry that was never interesting enough to become a postmortem is fine. A `try-failed-exp` that was later superseded by changed circumstances should be updated to `status: reassessed`. Lore is a living corpus, not a museum.

---

## Why "lore"

Not "knowledge base" — too corporate, too static.
Not "wiki" — too freeform, too un-typed.
Not "memory" — too individual.
Not "documentation" — too prescriptive, too maintenance-heavy.

*Lore* is the word for communal knowledge that accumulates over time — knowledge tied to a place and a people, passed down through experience rather than formal instruction. It is what a craft community earns through doing. It carries the sense of *earned* knowledge, not just recorded knowledge.

A project's lore is what it knows that no other project knows — because it ran those experiments, made those mistakes, lived through those incidents, and wrote them down.

---

---

# 哲学

## 这个工具解决什么问题

每个软件项目都会积累信号：git 提交、部署、故障、实验、决策——实时地堆积起来。但几乎没有项目能积累出*典藏*：从中提炼的、可复用的经验知识。

结果是一种机构性遗忘。新工程师加入，问"我们为什么在这里用 PostgreSQL？"没人能说清楚。团队在评估一个新的缓存方案，却不知道十八个月前他们试过同样的方案，因为某些从未被写下来的原因放弃了。一个架构决策每隔半年就被重新争论一遍，因为当初的理由只存在于某人的脑子里。

这不是知识管理的失败，而是*相变*的失败。信号从来都在那里，只是从未结晶。

---

## 冷却管道

信息有相态。

新鲜的信号是热的——高频变动、细粒度、短暂的。一次部署发生了。一个实验跑完了。一次故障被处理了。这些是事实，作为事实本身是有价值的。

随着时间推移，部分信号会结晶为*档*（archive）：事后复盘、回顾会议、版本说明。一次性的回溯，仍然绑定于特定事件，但已经被综合提炼过。

最持久的教训会进一步凝缩为*典*（canon）：可复用的规则、持续生效的决策、有记录的拒绝。一条 codex："我们对这个服务使用蓝绿部署，原因如下。"一条 try-failed-exp："我们评估了事件溯源来解决这个问题，判断它不适合我们的规模。"

大多数工具优化一个频段。可观测性工具优化热端，Wiki 优化冷端——但 Wiki 是静态的、无类型的，会腐烂。几乎没有工具优化*转变*本身。

Lore 的核心论点是：转变是最难的部分，把它变为一等公民，会改变一个团队对自身的认知能力。

---

## 为什么 try-failed-exp 是锚点

事后复盘（postmortem）的工具市场已经饱和：Jeli、Blameless、FireHydrant——故障回顾的工具链成熟、流程健全、覆盖广泛。

"已尝试、已拒绝"的空间几乎一片空白。

这种不对称触目惊心。"做这件事"——肯定性的决策——有架构决策记录（ADR）、设计文档、Wiki 作为支撑，算是覆盖还可以的。"不要做这件事，并且这是确切原因"——在工具层面几乎付之阙如。

每个有经验的工程师都有同样的故事："要是我早知道有人试过这个就好了。"知识是存在的，它在做实验的那些人的脑子里。当他们离职，当时间足够久，当代码库变化到无人能将新提案与旧尝试联系起来时，知识就蒸发了。

`try-failed-exp` 是专门为这类知识设计的典藏层记录。它是 `codex` 的镜像：`codex` 说的是"做这件事，理由如下"，`try-failed-exp` 说的是"不要做这件事——除非这些特定条件发生了变化"。

最后那个"除非"，是让这条记录长期有用的关键。

---

## 可证伪的锚点

拒绝记录在其他工具中的常见失效模式是腐烂。"我们试过 X，没成"被写下来，几年后没人记得当初驱动这个决定的约束条件了。这条记录要么被无视（"那都是老黄历了，情况肯定变了"），要么被误用为永久禁令。

`## Don't retry unless`（除非以下条件成立，否则不要重试）——每条 `try-failed-exp` 记录的必须章节——是这个问题的解法。它强迫作者写下具体的、可证伪的条件：

> *除非 Redis 在 GA 版本中推出原生跨槽事务。*
> *除非写入事件量持续超过每秒五万次。*
> *除非我们有专职 Rust 专家承担关键路径。*

这将模糊的"不行"变成了条件语句。未来的工程师读到这条记录时可以自问：这些条件改变了吗？如果改变了，记录不是在阻拦，而是在指引。如果没改变，记录清楚地解释了为什么现在仍然不是时候。

可证伪的锚点是 lore 区别于"禁止列表"的核心所在。

---

## Lore 不优化的东西

**完整性。** 不是每次部署都需要一条记录，不是每个决策都需要一条 codex。Lore 的价值在于*三年后值得找到的*那些记录——理由不那么显而易见的决策、得出结论的实验、带着教训的回滚。

**自动化。** Lore 生成候选，人来确认。Agent 可以挖掘 git 历史、分类提交、生成 frontmatter、暂存草稿文件。但它不会自主写入典藏记录。每一条落入 `.lore/canon/` 的记录都经过人工阅读和确认。这是刻意的约束，而非能力限制。

**穷举式文档。** API 文档属于代码注释，架构概览属于 `docs/`，Sprint 工单属于 issue tracker。Lore 服务的是*经验教训*层——那个最常缺失的层。

**无需策展的永久保存。** 冷却管道意味着不是所有东西都能完成转变。一条从未值得升级为 postmortem 的 journal 记录，完全没问题。一条因条件变化已被推翻的 try-failed-exp，应当更新为 `status: reassessed`。Lore 是有生命的语料库，不是博物馆。

---

## 为什么叫"Lore"

不叫"知识库"——太企业化，太静态。
不叫"Wiki"——太自由、无类型。
不叫"Memory"——太个人化。
不叫"Documentation"——太规范性，维护成本太高。

*Lore*，是那种在共同体中随时间积累的知识——与某个地方、某群人绑定的知识，通过经验传承，而非正式教学。这是一门手艺的共同体通过实践*赚来的*东西。这个词带有一种*挣得的*感觉，而不只是被记录的。

一个项目的 lore，是它所知道的、其他项目所不知道的——因为它跑过那些实验，犯过那些错，经历过那些故障，并且把它们写了下来。
