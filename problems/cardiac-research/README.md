# 自动心脏研究队列

2026-09-29 执行规则：本页所有项目 Python 入口及其调用的训练、评估、数据处理和测试，都必须在 254 服务器的 Slurm 作业内执行；不直接在本机或登录节点运行。下文保留命令接口说明。Slurm 作业内连续推进使用前台 `run`，使调度器覆盖整个执行周期；不按旧示例在本机后台 `start`。提交时先落实当前任务授权、资源、时限和服务器路径，历史本地运行记录不改变此规则。

延续原工作台的持续研究方式：每轮调用 Codex，读取当前证据，分析问题、写代码、
做授权实验、评估结果，再把下一动作交给下一轮。单个实验完成后仍会推进尚未完成的研究目标。

## 在工作台根目录使用

```powershell
python tools/research_queue.py check
python tools/research_queue.py list
python tools/research_queue.py plan ar-pca
python tools/research_queue.py once --slug ar-pca --dry-run
python tools/research_queue.py once --slug ar-pca
python tools/research_queue.py start --slug ar-pca --max-rounds 5 --max-hours 2
python tools/research_queue.py status
python tools/research_queue.py watch
python tools/research_queue.py stop
```

once 真正调用一次 Codex；start 隐藏窗口启动后台 runner。也可 run 前台连续执行。
stop 等当前回合保存状态后退出；强制关闭进程则下次启动识别中断，保留产物并要求先核对再 resume。
--dry-run 与 plan/packet 不启动模型，不创建任务状态、不清除 STOP。
无 --slug 时公平轮转全部 ready 任务。已完成/阻塞的任务不会冻结其他任务。

本机 PowerShell 策略可能禁止 .ps1，请使用上述 Python 入口；
后台运行不要求 tmux，不改系统执行策略。

## Neural ODE 任务

`neural-ode` 已独立注册，定义见 [task.json](items/neural-ode/task.json)。接续无 PCA 图 Neural ODE 的第四轮结果，优先研究重复激活、事件时序和早期 Ca；读取项目 `results/neural_ode/session_20260916/report.md`、原始结果和 `budget.json`，避免依据过时摘要重跑。

```powershell
python tools/research_queue.py plan neural-ode
python tools/research_queue.py once --slug neural-ode --dry-run
python tools/research_queue.py start --slug neural-ode --max-rounds 5 --max-hours 2
python tools/research_queue.py status
python tools/research_queue.py stop
```

前两条只预览；实际执行须放入 Slurm 作业，并将 `start` 换为前台 `run`。这里 5 轮/2 小时限制的是 Agent 队列运行；历史 4 个训练名额已经用完，新任务不会重置训练预算。可先静态读取源码和已有结果；CPU 检查及结果分析脚本同样通过 Slurm，新的训练须有明确追加预算。任务注册不代表已经启动或达到预测目标。

## 当前任务状态（2026-10-09）

ar-pca 与 neural-ode 已设 enabled=false，不再参与轮转；neural-ode-global-memory 改写为 neural-ode-full500（九组 500×200 正式训练、验证与测速）。启动时请带 `--slug neural-ode-full500`。

## 新任务

```powershell
python tools/research_queue.py add my-study "心脏预测实验" --objective "具体要解决的问题" --criterion "可检查的验收条件"
```

编辑 items/my-study/task.json 的目标、范围和验收，再启用：
```powershell
python tools/research_queue.py enable my-study
python tools/research_queue.py start --slug my-study --max-rounds 5
```

add/enable 可在队列运行时准备新任务，下一轮发现后纳入轮转。
pause/resume 修改任务状态，需先 stop 并确认 runner 已结束。
resume 不删除历史、不清零累计用量；恢复后再 run/start。
任务正在执行时不要改其验收目标；有改动会保留结果并暂停，避免按变化中的目标自动完成。

## 配置与记忆

工作台根 research-queue.json：默认继承 CLI 模型，单轮 90 分钟，每次启动 24 小时。
可设 max_rounds、max_wall_hours、max_tokens；0 表示对应预算不限。
单轮仍有硬超时且受剩余总时长约束；真实 token 用量只能在回合结束时核算，可能超出软上限。
再次启动获得新的启动预算，task.json 的 max_rounds 是跨启动累计上限。

状态在 projects/cardiac-ep/queue/<slug>/：
- CURRENT_STATE.md：短索引；state.json：状态、下一阶段、计数与用量。
- progress.md / verification-ledger.md：追加历史与证据哈希。
- .runtime/rounds/：研究包、Codex JSONL、结构化结果、before/after、COMMIT/APPLIED。
- 每轮 EXPERIMENT_CONFIG.json 将单次实验工具的输出指向本轮 artifacts/experiments/，沿用原项目、数据和实验配置。
- 全局 runs/research-queue/：锁、STOP、后台日志与启动状态。

模型每轮获得实际研究包；新 CLI 调用不会丢失研究状态。
文件提交中断可按哈希补齐；与其他会话编辑冲突时暂停当前任务，保留原内容。
软件恢复测试通过不等于真实研究目标完成。根据结果验收，不以回合数或 smoke 成功替代科学评价。

Codex 调用参数依据本机 0.154.0 帮助与 [官方非交互说明](https://learn.chatgpt.com/docs/non-interactive-mode)：
JSONL、输出 schema、workspace-write、额外任务目录。沿用本机登录/配置，不复制凭据，
不传入绕过沙箱/审批的参数。check 的登录提示需结合真实的短回合核实，未认证时先在自己的终端完成 codex login。
