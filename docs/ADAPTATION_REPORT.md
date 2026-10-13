# 本次 Agent 改造清单

完成日期：2026-09-16。用户指定心脏电生理与 AI 个体化建模，优先写代码、跑实验。

## 当前修订：恢复自动多轮研究

按用户确认，恢复自动调用 Codex、连续推进研究的默认入口。
第一版移除了默认自主队列，这一运行方式变化已纠正。

- `tools/research_queue.py` 连续执行 analyze / implement / experiment / assess 回合，
  自动传递上一轮短状态、结论与下一动作；保留多任务公平轮转。
- `tools/research_runtime.py` 将原版研究包、证据台账、CLI 用量统计和可恢复状态提交机制迁入心脏流程。
- 支持前台/后台运行、追加任务、回合/时长/token 预算、回合结束后停止、再次启动接续、异常任务独立暂停。
- 默认继承 CLI 模型，单轮 90 分钟、每次启动 24 小时；原版 Bash/tmux 后台改为 Windows/Linux 原生 Python 进程。
- `queue.sh`、`queue.ps1`、`tools/conjecture_queue.py` 指向自动队列；`cardiac_workspace.py` 保留为回合内实验工具。
  实验使用回合专属配置，产物保存在任务可写目录，不扩大到整个 Agent 工作台。
- 当前 AR/PCA 目标写入 `problems/cardiac-research/items/ar-pca/task.json`。
  队列读取最新全局研究记录，但只提交各任务自己的状态，保留其他会话的研究进展。

本次实现并非把原数学源码原样重新启用：证明认证、Rethlas、全局“解题后冻结”不适用于当前实验任务，
仍保留在原版归档。自动任务共用心脏源码，逐轮串行运行；不会自动额外启动多 Agent。

本修订的验证：43 项工作台测试通过，其中新增 26 项覆盖实际子进程的多轮交接、后台运行、
预算、停止/恢复、失败隔离、状态冲突、部分提交恢复以及回合内调用实验工具。
这些测试用程序替身代替模型响应，未调用真实模型；不是 AR/PCA 科学目标完成的证据。
本机 CLI 0.154.0 的所需参数检查通过，但 `login status` 显示未登录，真实模型回合尚未验证。
没有启动正式研究队列、训练或远程作业；未改写心脏模型源码、数据和权重。
本修订验证摘要保存在 `runs/autonomy-validation/validation.json`。

恢复前快照：`../agent-autonomy-backup-20260916-150206/before-autonomy.zip` 及 `sha256.json`。

## 改动范围

以下文件计数描述第一版领域适配，后续队列恢复新增文件另见上节。原 97 个文件中：23 个在原位置更新（含 MANIFEST.sha256），
60 个按原相对路径移到 archive/math-framework/，14 个保持原样。
另外新增心脏项目索引、实验/验证协议、技能、配置与 Python 执行器。
归档文件逐一核对原 SHA256，未丢失原文件。

| 模块 | 原行为 | 当前行为 |
|---|---|---|
| AGENTS / research-core | 图几何、证明、反例 | 心脏代码/实验；数据与预测验证 |
| 审核/证据 | 证明等级、形式化与主问题冻结 | 实现、数值、数据、预测、个体化、不确定性分别记录 |
| queue / setup | Bash/tmux 数学队列、graphlab | Python 自动多轮心脏研究 + 单次实验工具；沿用现有环境 |
| 技能 | 数学论文写作、学习稿 | 心脏代码实验、论文到实现 |
| 状态/模板 | 猜想、gap、proof-map | 项目短状态、实验卡、数据到结论的依赖 |
| CI | 数学运行时/论文资源检查 | Windows/Linux 工作台测试与源码清单 |

第一版曾将原自动调度器归档，仅提供单次实验执行器；用户要求保留自动多轮推进后，
已完成本页首节所述的心脏版调度移植。原始实现仍完整归档，便于查阅和比较。
旧 Rethlas、十项证明认证、形式化状态和全局候选解冻结不再生效。

## 对心脏项目的改动

仅新增两个入口：
- AGENTS.md
- .agents/skills/cardiac-project/SKILL.md

本次没有改写模型、训练/分析实现、数据、正式权重、PCA 基底和 Slurm 作业脚本，
也没有提交、取消或调整远程作业。已有 Git 改动保留。
起始快照记录的 65 个源码/说明文件中，模型等 code/ 文件均核对未变。
处理期间观察到 slurm/README.md 和 slurm/pca.md 在 13:39 更新；这些文件不是本次写入，
保留当前版本，不能声称整项目所有文件的哈希均未变化。

## 第一版领域适配验证（历史记录）

- 最终工作台 17 项回归测试通过，包括中文/空格路径、只读预检、失败/超时/中断、
  不覆盖重跑记录、源码变化检测、NPZ 压缩/形状/截断校验。
- TC_GCN_server：71 项测试通过。
- FBNO_time_forecast：17 项测试通过。
- 25 个真实 v10 NPZ：成员、形状、dtype、存储方式和声明字节数预检通过；只读头信息，
  不代表逐值检查全部约 134 GB 数据。
- 原生 inspect 成功：750 样本，43573 节点，20/2/3 批切分。
- AR 和 Direct 各完成真实网格的一次小模型参数更新并保存 last.pt。
  AR loss=0.02343567，Direct loss=0.007337548；仅 smoke，不能横向比较效果。
- 三个技能通过 skill-creator 验证（Windows 用 python -X utf8）。
- Bash 的 setup.sh / queue.sh 语法通过；PowerShell 包装器语法通过，但本机执行策略禁止运行 ps1，
  使用已验证的 Python 入口，不修改系统策略。
- 本项目没有配置独立 lint/typecheck；运行适用的 Python 语法检查与上述测试。
- 源码清单已按最终内容重新生成并检查；封存摘要见 runs/adaptation-validation/validation.json。

## 直接证据

| 检查 | 结果 |
|---|---|
| 工作台与入口 | runs/adaptation-validation/ |
| AR/PCA 71 测试 | runs/20260916T053453-server-tests-ad1f043c/run.json |
| Direct 17 测试 | runs/20260916T053532-direct-tests-4d38658f/run.json |
| 真实 inspect | runs/20260916T053538-inspect-data-6ab13662/run.json |
| AR 短训练 | runs/20260916T053617-smoke-ar-b42544af/run.json |
| Direct 短训练 | runs/20260916T053623-smoke-direct-ad4a3444/run.json |

每个 run 目录保留 stdout/stderr；两个短训练的 artifacts/ 保存小型 last.pt。
记录中的 prediction/personalization/uncertainty 未自动升级，本次没有重新评价正式模型的完整预测性能。
PCA 正式训练未运行，本机主线目录没有可直接采用的固定 basis/；先核查服务器现有基底，不能擅自覆盖。

## 查看原版与继续使用

完整原版：../agent-adaptation-backup-20260916-131832/original-agent.zip。
原始哈希：同目录 agent-sha256.json；本次差异：runs/adaptation-validation/file-diff.json。
如需恢复，解压到独立目录先比较，不覆盖现在的实验记录。

在 PDE 心脏代码2 中新开 Codex 会话即可按新增 AGENTS.md 读取工作台；
本地命令与说明见 README.md，准确源码位置与科学边界见 projects/cardiac-ep/SOURCE_MAP.md。
