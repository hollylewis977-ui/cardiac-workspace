# 心脏电生理与 AI 个体化建模工作台

每次回答以 **我亲爱的父亲大人** 开头，默认用中文。工作区为本目录，用于心脏代理模型研究管理；实际源码在上一级目录 `../`，路径由 `cardiac-workspace.json` 配置，不能从终端当前目录猜测数据位置。

## 不可变边界

- 主命题必须实际推进：改代码、跑授权实验或构造失效案例，不能用整理文件、重命名或综述代替。
- 区分探索与认证。探索可在明确标为 conditional/GAP 的命题上推进；候选完整结果、决定性失效案例、高风险共同依赖和证据升级必须进入认证，冻结受影响的依赖节点。
- 实质结论必须有证据等级和直接证据：`conjecture`、`experimental`、`partial-result`、`proof-draft`、`agent-verified`、`human-verified`、`formalized`。smoke 只证明可执行，低 loss 不是结论，单病例图不是验证；自检不能成为独立验证，模型强度与状态整理不能提高等级。
- `agent-verified` 需要独立复核作业重算一致并通过十项审查；`human-verified` 需要研究者逐项接受；`formalized` 需要在开发中从未接触的数据上成立。论文主结果无保留写入摘要和结论须达到后两级，并取得研究者授权。
- 2026-09-29 用户要求：所有项目代码执行，包括研究队列、训练、评估、绘图、数据处理、CPU/GPU 测试和 smoke，必须通过 254 服务器 Slurm 排队取得资源后进行，不在本机或登录节点直接运行。读取/编辑文件、SSH、传输、提交和查询作业可直接进行。已有授权范围和预算仍有效，不擅自取消或改动远程作业。
- 不写机密、不修改 `.env`、不覆盖已有改动、不用破坏性命令清理。修改前后检查 Git diff。除非明确要求，不提交或推送。

## 按阶段读取

只读当前任务所需模块，已包含在研究包中的正文不重复读取。开始相关工作前完成读取，并在首次实质进度更新列出路径：

- 任何任务：`projects/cardiac-ep/problem.md`、`CURRENT_STATE.md`、`claim-map.md`、`SOURCE_MAP.md`，再读 `agents/core/research-core.md`。
- 探索、路线诊断：`agents/protocols/explore.md`。
- 候选结果、严格审核、证据升级：`agents/protocols/claim-audit.md`。
- 决定性失效案例：再读 `agents/protocols/failure-case-audit.md`。
- 申请独立复核：`agents/protocols/independent-replication.md`。
- 每轮进展归类：`agents/protocols/progress-assessment.md`。
- 改代码、短训练和复现：`agents/protocols/computation.md`；技能 `.agents/skills/cardiac-experiment/SKILL.md`。
- 数据、时间窗与泄漏：`agents/protocols/data-validation.md`。
- 性能、生理指标与可信度：`agents/protocols/model-validation.md`。
- 文献核查与架构对照：`agents/protocols/literature-check.md`。
- 队列回合：`agents/core/queue-core.md`、`agents/protocols/round-result.md`；操作调度器时另读 `problems/cardiac-research/README.md`。
- 论文、面向公开读者的研究文字：`agents/instructions/paper-writing.md`。
- 研究者明确要求多智能体时：`agents/protocols/multi-agent.md`。不因工具可用自行增加并行 Agent。

旧入口 `agents/instructions/research-workflow.md` 和 `queue-and-escalation.md` 提供索引。

## 长期记忆与目录

`CURRENT_STATE.md` 是恢复的唯一短入口，只保存题目范围、证据上限、可用结果 ID、活动缺口与路线、下一动作和证据指针，不存实验正文。目标 6 KiB，上限 12 KiB/300 行，禁止为满足大小静默截断证据。

先读状态，再按台账 ID 和文件路径读取证据。禁止为了了解上下文完整重读增长中的 `progress.md`。摘要不能覆盖台账或直接证据；冲突时以直接证据为准并修正摘要。

产物位于 `projects/cardiac-ep/`：正式题目 `problem.md`，短状态 `CURRENT_STATE.md`，追加历史 `progress.md`，证据与等级 `verification-ledger.md`，命题依赖与缺口 `claim-map.md`，方法族与实验卡 `ideas.md`，路线 `research-tree.md`，文献对照 `references.md`，源码索引 `SOURCE_MAP.md`。通用定义放 `library/definitions/`，已证结论放 `library/results/`，认证过的失效案例放 `library/failure-cases/`。正式权重、数据和科学产物留在心脏项目；工作台 `runs/` 只存执行日志、元数据和 smoke 产物。

只有对应结构变化才更新路线和依赖文件。队列每任务的短状态在 `projects/cardiac-ep/queue/<slug>/`，由 runner 统一提交；队列读取全局状态但不重写，避免覆盖其他会话的进展。`archive/math-framework/` 是原版数学框架，供对照阅读，不加载其中的队列、Rethlas 或证明规则。

## 摘要与研究沟通

- 摘要用清楚、简洁、自然的中文，让研究者无需翻阅历史记录即可理解。默认一至三段，必要时再用列表或表格。
- 先说主命题及其解决情况，再说明本次具体实现、运行或排除了什么，最后说尚缺哪一步及下一动作。没有新结果就直接说明。
- 结论保留决定性的对象、协议、病例范围与指标。完整达标、特殊情形、辅助结论和数值观察分开说；文献结果与本次结果分开说。
- 证据等级用人能理解的话解释，例如"完整协议下成立但只有本会话自报""已由独立作业重算核验"；正式等级与证据指针仍按原规则保留。
- 首次出现台账 ID、节点 ID 或专用术语时写出含义。不用比喻。
- 选方向时说明为什么有希望推进主命题以及主要障碍；容易跑、已投入很多轮都不能单独作为理由。

## 环境与交付

优先复用现有 Python/PyTorch 环境；新增依赖遵循心脏项目的 uv 约定，不重建或覆盖现有环境。模型修改使用独立实验输出目录，保留正式权重、数据、基底和冻结源码。绘图输出 PNG，正式图走 code/visualization 的 SCI 脚本（见 agents/protocols/computation.md 第 8 条）。无对应配置的 typecheck/lint 如实报告未配置。

多步骤任务写明目标、假设、产物和验收标准。完成时报告文件路径、检查、缺口、证据等级及下一动作。题目有实质歧义、候选结果需要研究者确认、准备写论文主结果或改变项目目标时，保存具体材料再询问研究者。
