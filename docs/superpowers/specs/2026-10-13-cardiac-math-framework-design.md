# 心脏代理模型数学框架：设计

日期：2026-10-13。对象：cardiac-workspace。

## 1. 背景与目标

原版 graph-geometry-research-workspace 的数学框架由九个机制组成：正式题目、七级证据等级、方法族登记、研究树、证明依赖图、认证、进展判定、升级通道、资料库。2026-09-16 的心脏改造把其中大部分删掉或压扁，只留下队列和计算实验协议。研究者仍按数学框架思考，要求把框架按"心脏代理模型"重新实例化，一套体系，不并存两套记录。

目标：projects/cardiac-ep/ 成为原版"一道题"的完整骨架；agents/ 协议分数学框架层和计算实验层；library/ 填实；工具只做最小改动，让自动队列读到新文件。

主命题定为时间外推算子；个体化登记为第二道题，不启动。现有心脏代理模型架构的联网调研不在本设计内，作为框架建成后的第一个 connected 回合单独立项。

## 2. 目录与文件角色

### 2.1 projects/cardiac-ep/

| 文件 | 角色 | 处理 |
|---|---|---|
| problem.md | 正式题目：主命题、定义与归一化、允许使用的基础事实、已知结果、已试路线、辅助命题、搜索承诺 | 新建 |
| CURRENT_STATE.md | 短入口，分节：控制字段 / 题目与范围 / 当前状态 / 活动前沿 / 下一回合 / 证据指针。现有实验总表和实时状态段压进"当前状态"。目标 6 KiB，上限 12 KiB/300 行 | 重写 |
| ideas.md | 方法族登记表 F1–F5 及覆盖审计 | 新建，吸收 experiments.md |
| research-tree.md | 路线 DAG（mermaid）加分支卡片 | 新建 |
| claim-map.md | 命题依赖图（mermaid）、节点登记表、GAP 登记 | 新建，吸收 evidence-map.md |
| verification-ledger.md | 表头加"等级"列；已有 ID 和内容不改 | 加列 |
| references.md | 现有架构对照表，先填项目已引用的 DIMON、FBNO、LNODE 及 AR-LIT-001 的三篇 | 新建 |
| SOURCE_MAP.md | 只留"路径 → 作用"表，补齐 code/NeuralODE、NeuralODE_GlobalMemory、NeuralODE_Pure、NeuralODE_Experiments；数据与协议段移入 problem.md；环境段删除；命令段移入 README | 收窄 |
| progress.md | 不动 | 不动 |
| experiments.md、evidence-map.md | 内容并入 ideas.md、claim-map.md 后删除 | 删除 |

CURRENT_STATE.md、SOURCE_MAP.md、progress.md、verification-ledger.md 四个名字被工具、测试和上级项目 AGENTS.md 引用，不改名。

### 2.2 problems/cardiac-research/items/

三个现有 task.json 不动。新增 personalization/：problem.md（第二道题）和 task.json（ready=false，enabled=false）。global-memory-queue.json、global-memory-workspace.json 留在根目录：服务器 code/NeuralODE_GlobalMemory/slurm/agent.sbatch 与 agent_check.sbatch 以 `--config global-memory-queue.json` 引用它们，队列按配置文件所在目录解析 items_dir、state_dir、project_root，挪动会全部失效。README 文件导航说明它们的用途。

### 2.3 agents/

数学框架层：

| 文件 | 处理 |
|---|---|
| core/research-core.md | 重写：四类对象、七级等级心脏判据、验证维度、认证触发、每轮交付物 |
| protocols/explore.md | 重写：方法族规则、七种失败类型、重开条件、实验卡字段 |
| protocols/claim-audit.md | 新建：十项审查心脏版 |
| protocols/failure-case-audit.md | 新建：失效案例认证 |
| protocols/independent-replication.md | 新建：Slurm 独立复核交接稿与结果等级 |
| protocols/progress-assessment.md | 新建：进展分类与换机制门槛 |
| protocols/literature-check.md | 重写：connected 回合与架构对照表字段 |

计算实验层：data-validation.md、model-validation.md、computation.md、multi-agent.md 不动；round-result.md 追加 progress 与 new_claims 两节。core/queue-core.md 不动。instructions/research-workflow.md 更新索引。

### 2.4 library/

| 目录 | 内容 |
|---|---|
| definitions/ | 一条定义一个文件：flow-map、observation-operator、closure、scaler-nrmse、activation-event、time-windows |
| results/ | 等级达到 agent-verified 及以上的结论，一条一个文件，引用台账 ID。初始为空，只放 README 写准入条件 |
| failure-cases/ | 经 5.3 认证的失效案例。初始为空，只放 README 写准入条件；nogru 场误差低但激活 F1 .179、hard H 激活时间 MAE 退化两条先作为 C 节点登记在 claim-map，等级按台账现状 |
| examples/ | 最小例子：batch_022/sample00 单病例的输入、真值和评价方式说明 |

### 2.5 templates/

新建 problem.md、ideas.md、research-tree.md、claim-map.md、claim-audit-report.md、CURRENT_STATE.md，与现有 experiment.md 平铺在 templates/ 下。project_template/ 目录删除，避免与平铺模板重复。cardiac-round-result.schema.json 加可选字段。

### 2.6 删除与归并

删除空壳目录 index/、environments/、examples/、shared/（shared/research-progress-guide.md 改写为 protocols/progress-assessment.md）。删除 queue.ps1、queue.sh、setup.sh。PDE_BRIDGE.md、SETUP_AI_PROMPT.md 的有效内容并入 README.md 后删除。ADAPTATION_REPORT.md 被 progress.md 与台账 ADAPT-001 引用，移到 docs/ADAPTATION_REPORT.md 原文保留，三处链接改为新路径。archive/math-framework/ 原样保留。

根目录最终文件：README.md、AGENTS.md、LICENSE、.gitignore、.gitattributes、cardiac-workspace.json、research-queue.json、global-memory-queue.json、global-memory-workspace.json、MANIFEST.sha256。

### 2.7 入口文档

工作台 AGENTS.md"开始工作"清单改为先读 problem.md、CURRENT_STATE.md、claim-map.md、SOURCE_MAP.md、research-core.md。README.md 文件导航表按新文件重写，吸收 PDE_BRIDGE、SETUP_AI_PROMPT、ADAPTATION_REPORT 的有效内容。.github/workflows/ci.yml 删除 shell 语法检查步骤。

## 3. 证据等级与命题体系

### 3.1 七级等级，心脏判据

| 等级 | 判据 |
|---|---|
| conjecture | 只有假设，没有任何运行 |
| experimental | 单种子、短预算或合成数据上的数值信号；smoke、低 loss、单病例图止于此 |
| partial-result | 只在受限范围成立：必要条件、训练段、单病例、固定权重下限 |
| proof-draft | 完整协议（固定选模、90 例测试、对照、协议差异写明）下成立，只有本会话自报 |
| agent-verified | 独立脚本或 Slurm 作业从冻结权重和源码哈希重算，逐值或在声明容差内一致，claim-audit 十项通过 |
| human-verified | 研究者逐项看过证据并明确接受 |
| formalized | 在开发中从未接触的数据上成立：新合成批次或真实患者 |

固定句：smoke 只证明可执行，低 loss 不是结论，单病例 PNG 不是验证。自检最高 proof-draft；独立复核才 agent-verified；只有研究者给 human-verified。

每条命题另记验证维度：code、numerics、data、prediction、personalization、uncertainty，各为 not-assessed / supported / failed。等级说验到什么程度，维度说验的是哪方面。

来源标签：internal、provided-source、web-source。不采用原版 offline / connected / mixed-isolated 隔离。

### 3.2 节点 ID

claim-map 节点前缀：P0 主命题；A 路线级命题（每个方法族的决定性子目标）；S 辅助命题；E 实验证据；C 失效案例；D 定义；L 文献。台账 ID（AR-BASE-001、NODE-GRAPH-004 等）不改，节点表"证据"列引用它们。

### 3.3 认证触发

两种情况进入 claim-audit，冻结依赖该节点的下游：某路线声称决定性子目标在完整协议下成立；某病例或条件严格否定一条命题。其他中间结果局部检查后继续。搜索承诺为 either。

## 4. problem.md 主干

定义与归一化：参考域 Ω 为二维网格，N = 43,573 节点。状态 y(t) ∈ R^{N×21}，演化 y' = D·L y + R(y)，L 为参考图邻居差分算子，D = 0.08，R 为 Courtemanche 1998 反应项；内部步长 0.02 ms，保存步长 2 ms，1001 帧。观测算子 O(y) = (V, Ca) = (y₀, y₁₈)。流映射 Φ_τ: y(t) ↦ y(t+τ)。数据 750 例，按完整文件 20/2/3 切分为 600/60/90 例。Scaler 固定 V ∈ [−100, 50] mV、Ca ∈ [0, 0.0012] mM；NRMSE 分母 150 mV / 0.0012 mM；激活阈值 −20 mV。监督、选模、观测截止、评分四个时间范围分别声明。生成器先扩散并裁剪 V，再离子步进；x_mesh 形变坐标不进入演化。

主命题 P0：存在算子 G，仅输入 u₀…u₂₅₀（0–500 ms 观测），使未见初值的病例在 k = 251…500（502–1000 ms）上 V/Ca NRMSE 与激活事件指标（首次激活漏检、误检、时间 MAE）同时达到验收阈值。阈值由研究者填写；草稿先写"必须优于"下界：旧 AR 晚期 66.80 mV / 405.65 nM、首次激活漏检 46.86%。

辅助命题：
- S1 闭包：0–500 ms 的 V/Ca 历史是否决定 y(500 ms) 全部 21 维。AR 与 ODE 都依赖；当前 conjecture。可证伪测试：用生成器构造同一观测历史、不同隐态的病例。
- S2 一步算子误差累积：2 ms 算子推 250 步后误差是否可控。
- S3 低维表示：PCA256 重建误差是否低于目标；pca_oracle 已量化，partial-result。
- S4 记忆态 H 是否补足 S1 缺的信息。

允许使用的基础事实：生成器源码事实与台账 agent-verified 及以上条目。已知结果与已试路线：AR 七组、Neural ODE 第 3/4 轮、六组 H 筛选、Pure 训练中，各带等级与失败位置。

方法族初始登记：F1 AR 一步算子、F2 固定 PCA 低维推进、F3 图 Neural ODE、F4 直接时间查询、F5 区域记忆态 H。

## 5. 协议

### 5.1 探索

方法族按核心机制归族，换超参或换名不算新族。初次或结构性改线至少三族。同一障碍失败两次不重复原推导，只能改表示、弱化目标、找失效案例或申请独立复核。失败类型七种：gap、failure-case、circular、too-strong、definition-mismatch、reference-mismatch、missing-tool。重开条件只认新机制、新表示、新数据或新工具能直接打原 gap。每个 A 节点必填实验卡字段：假设、改变因素、对照、数据与时间协议、主要指标、种子与预算、停止条件、产物。

### 5.2 claim-audit 十项

1. 每个指标是否来自有命令、哈希、退出码的运行。
2. clamp、teacher-forcing、oracle 诊断是否混入预测。
3. 训练、选模、测试三个时间范围是否分别记录并与命题一致。
4. 是否找过最差病例和 persistence 对照。
5. Scaler、NRMSE 分母、激活阈值、事件匹配规则是否与 problem.md 一致。
6. 选模是否碰过测试集；开发暴露是否声明。
7. 权重、基底、数据清单是否真实存在且哈希一致。
8. 借用文献方法时假设与归一化是否一致。
9. dt、裁剪、float16、无匹配事件 MAE=0 等数值边界是否处理。
10. 结论是否只在单种子、单病例或训练段成立。

审查报告按 templates/claim-audit-report.md 写，记录输入快照哈希、依赖、审查人。

### 5.3 失效案例认证

先过十项。失效案例必须满足 problem.md 全部假设、指标明确越过阈值、可复现（权重、输入、命令）。单例浮点结果只算 experimental。否定加强版不等于否定主命题。认证通过后冻结依赖节点，记入 library/failure-cases/。

### 5.4 独立复核

触发：同一 gap 两轮未闭合，或 proof-draft 申请升 agent-verified。交接稿内容：命题、协议、冻结权重与源码哈希、命令、容差、验收。提交 Slurm 独立作业重算；复核脚本不改模型或协议；结果最高 agent-verified；提交走已授权预算。

### 5.5 进展判定

每轮 progress 对象：claimed_kind ∈ {frontier-advance, route-elimination, enabling-result, experimental-signal, reformulation, repeat, inconclusive, regression, candidate-solution}；main_problem_effect；scope_limitations；evidence_level ≤ proof-draft。连续两轮同一障碍上 repeat 或 reformulation，下轮必须换方法族或写 reopening_basis。连续三轮无 frontier-advance，下轮计划带 strategy_review。建议模式，脚本不自动 blocked。

### 5.6 文献

connected 回合填 references.md 架构对照表，字段：方法、论文或代码链接、对象层级（单细胞、组织、全心）、状态与观测、算子类型、时间处理（直接查询、自回归、连续）、几何处理、训练数据规模、指标、与本项目差异和可借鉴点、来源标签、阅读状态。没读到原文记 GAP。

## 6. 工具改动

1. tools/research_runtime.py：研究包 files 列表加 projects/cardiac-ep/problem.md 与 claim-map.md。
2. agents/protocols/round-result.md 与 templates/cardiac-round-result.schema.json：加可选 progress 对象与 new_claims 列表（id、statement、level ≤ proof-draft、dimensions、evidence）。runner 只校验格式，不判真伪，不写 claim-map。
3. cardiac-workspace.json：source_roots 补齐四个 NeuralODE 目录。
4. 上级项目 AGENTS.md"先读"清单加 problem.md 与 claim-map.md。

tools/cardiac_workspace.py、research_queue.py、update_manifest.py 不改。

## 7. 验证

1. `python -m unittest discover -s tools/tests`：现有 43 项通过，新增 schema 可选字段校验测试通过。
2. `python tools/update_manifest.py write` 后 `check` 通过。
3. `python tools/research_queue.py packet --slug neural-ode-full500`：只读拼包成功，含 problem.md 与 claim-map.md，CURRENT_STATE 不超 12 KiB/300 行。
4. grep：v10 数据事实只在 problem.md 一处；experiments.md、evidence-map.md 无残留引用；README、AGENTS、SOURCE_MAP 链接指向存在的文件。
5. `bash -n` 不再需要（脚本已删），CI 的 shell 步骤同步移除。

## 8. 不做的事

不动心脏项目源码、权重、数据。不启动自动队列。不做联网调研。不改 archive/math-framework/。不实现 runner 自动写 claim-map。不恢复 offline / mixed-isolated、Rethlas、tmux、graphlab。

## 9. 后续

框架建成后：第一个 connected 回合做现有心脏代理模型架构调研，按 5.6 填表；第一个 claim-audit 对象是 AR-BASE-001，通过后进入 library/results/；第二道题 personalization 在有影响动力学的数据后再 ready。
