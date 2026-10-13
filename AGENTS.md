# 心脏电生理与 AI 个体化建模工作台

默认用中文，以 Boss 称呼研究者。优先交付能运行的代码、实验和可追溯结果。
此目录维护 Agent；实际源码在本工作台的上一级目录 `../`。
路径由 `cardiac-workspace.json` 配置，不能从终端当前目录猜测数据位置。

## 开始工作

1. 先读 `projects/cardiac-ep/CURRENT_STATE.md`、`projects/cardiac-ep/SOURCE_MAP.md` 和 `agents/core/research-core.md`。
2. 修改心脏代码前读该项目的 `AGENTS.md`、`CODEX.md`，检查 Git status/diff，保留已有改动。
3. 根据任务读取相关模块；状态只用于导航，具体实现、checkpoint 和原始日志是事实依据。旧文档中的服务器任务状态必须重新核查。
4. 已授权的代码修改、检查和必要的短实验继续完成；不要为例行步骤反复请求确认。确实缺少数据、目标或运行资源时指出具体缺口，继续可独立完成的工作。
5. 本工作台没有 Git 时先保存快照再修改；有 Git 时检查差异。不擅自提交或推送。

## 当前项目的科学边界

- 当前主线 `code/TC_GCN_server/`：V/Ca 自回归预测、AR 消融、固定空间 PCA 低维推进。`code/FBNO_time_forecast/` 是直接时间查询对照，二者不是同一模型。
- v10 是二维 CRN 合成数据。参考节点顺序固定；观测 0–500 ms，预测 502–1000 ms，保存步长 2 ms。训练监督截止、选模时间段、测试输入必须分别记录。
- 数据按完整 NPZ/样本切分，默认 20/2/3 批；PCA、归一化拟合和选模不能使用测试集。若以后有真实患者，按患者划分，不能随机分帧泄漏。
- `full_init` 有 21 个离子状态，后续只保存 V/Ca。不能把单帧 V/Ca 当作完整闭合状态，也不能把 GRU 记忆宣称为真实离子状态反演。
- v10 的变形坐标没有进入演化公式。几何泛化、参数识别、真实患者个体化能力均需各自实验，不能从现有预测指标推出。
- 源码与注释冲突时记录实际实现：例如 v10 实际 D=0.08，注释中的推算值不能充当已测传导速度。
- 区分实现检查、数值验证、数据协议、独立预测验证、个体化验证与不确定性；它们不是可以自动升级的单一等级。smoke 成功不表示预测有效，进程退出成功不表示课题完成。

## 按需读取

- 改代码、短训练和复现：`agents/protocols/computation.md`；技能 `.agents/skills/cardiac-experiment/SKILL.md`。
- 数据、时间窗与泄漏：`agents/protocols/data-validation.md`。
- 性能、生理指标与可信度：`agents/protocols/model-validation.md`。
- 方案和消融：`agents/protocols/explore.md`。
- 任务运行与收尾：`agents/core/queue-core.md`、`agents/protocols/round-result.md`。
- 文献复现与论文：`agents/protocols/literature-check.md`、`agents/instructions/paper-writing.md`。
- 只有研究者明确要求多 Agent 时才读 `agents/protocols/multi-agent.md` 并委派。

## 代码与实验约定

先最小复现，再改实现，再运行受影响测试，必要时用真实数据做有上限的 smoke。
优先复用现有 Python/PyTorch 环境；先核查版本与设备，不创建 graphlab，不为读代码安装仿真工具链。
新增依赖遵循心脏项目的 uv 约定，不重建或覆盖现有环境。
2026-09-29 用户要求：所有项目代码执行（含研究队列、训练、评估、绘图、数据处理、CPU/GPU 测试和 smoke）必须通过 254 服务器 Slurm 排队取得资源后进行，不在本机或登录节点直接运行。读取/编辑文件、SSH、传输、提交和查询作业可直接进行。历史本地命令不再作为执行依据；已有授权范围和预算仍有效，不擅自取消或改动远程作业，不将历史作业号当作当前状态。
执行大批量训练前落实数据路径、预算、输出目录和停止条件；已经授权的预算不重复确认。
模型修改使用独立实验输出目录。保留正式权重、数据、基底和冻结源码；不覆盖已有训练结果。
绘图遵循项目约定输出 PNG。无对应配置的 typecheck/lint 如实报告未配置，运行适用的语法与测试检查。

## 记忆与交付

短入口在 `projects/cardiac-ep/CURRENT_STATE.md`（目标 6 KiB，最多 12 KiB/300 行）；历史只追加到 `progress.md`。
`verification-ledger.md` 记录结论及证据，`evidence-map.md` 记录数据→预处理→模型→运行→结论依赖，`experiments.md` 记录待做实验与比较条件。
源码和正式科学产物留在心脏项目；工作台 `runs/` 存执行日志、元数据和 smoke 产物。
自动多轮队列使用 `tools/research_queue.py`，保留自动调用 Codex、研究包、证据、预算与恢复能力。
队列每项任务的短状态和回合记录位于 `projects/cardiac-ep/queue/<slug>/`；runner 统一提交，worker 不改保护状态。
队列读取全局研究状态，但不重写它，避免覆盖其他会话的进展。单次实验执行器是队列内的工具。
完成时报告改了什么、实际运行什么、结果在哪里、尚有什么未验证；不要仅以整理文件作为科研进展。
`archive/math-framework/` 是历史材料，不加载其中的数学规则、技能、证明队列或 Rethlas。
