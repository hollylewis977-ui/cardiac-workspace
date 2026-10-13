# 心脏电生理与 AI 个体化建模 Agent

此工作台位于 **PDE 心脏代码2** 项目内部，优先服务于写代码、跑实验和分析结果。
当前源码入口是 `code/TC_GCN_server/` 的 AR/PCA，以及 `code/FBNO_time_forecast/` 的直接预测对照。
2026-10-09 目录已由 graph-geometry-research-workspace-main 改名为 cardiac-workspace；服务器副本需同步改名。
保留原版的自动多轮研究方式：连续调用 Codex，分析 → 改代码 → 做实验 → 评估 → 继续下一轮。
单次实验执行器作为研究队列内的工具；跨轮状态、证据、预算和恢复由队列管理。

## 自动多轮推进

在本工作台目录执行，默认 ar-pca 任务已连接现有研究目标：

```powershell
python tools/research_queue.py check
python tools/research_queue.py plan ar-pca
python tools/research_queue.py start --slug ar-pca --max-rounds 5 --max-hours 2
python tools/research_queue.py status
python tools/research_queue.py watch
python tools/research_queue.py stop
```

`start` 在后台连续调用 Codex；`run` 是前台连续运行；`once --slug ar-pca` 调用一轮。
`stop` 在当前回合保存后退出，之后再次 `run/start` 从已有状态接续。
上例限制 5 轮、2 小时；不加覆盖参数时沿用单轮 90 分钟、一次启动 24 小时的默认预算。
继承本机 CLI 模型，不另选模型。`plan`、`packet`、`once --dry-run` 只读预览。

2026-09-16 本机检查显示 CLI 未登录；真实模型回合尚未验证。请在自己的终端完成 `codex login`，
再用一轮验证实际连接。软件回归使用独立子进程测试替身，不冒充真实模型研究。
任务配置、动态加任务、恢复和 token 预算见 [队列说明](problems/cardiac-research/README.md)。

## 交互式工作

也可在心脏项目中开启 Codex 会话；其 AGENTS.md 会引导读取本工作台：

```powershell
Set-Location '..\PDE 心脏代码2'
codex
```

可以直接说：

> 读取 Agent 的 CURRENT_STATE 和 SOURCE_MAP。先检查 TC_GCN_server 当前改动与测试，然后根据我的实验需求修改代码；保留已有修改和正式权重，记录实验协议与验证结果。

也可以从工作台开始；此时会话的可写范围需要包含上一级心脏项目目录。实际文件权限以当前会话为准。
本改造不修改全局 Codex 配置。项目 AGENTS.md 和 .agents/skills 的入口依据 [OpenAI 官方说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[技能说明](https://learn.chatgpt.com/docs/build-skills)。

## 本地检查和实验

在本工作台运行，所有相对路径以配置文件所在目录为基准，支持中文和空格：

```powershell
python tools/cardiac_workspace.py doctor
python tools/cardiac_workspace.py list
python tools/cardiac_workspace.py packet
python tools/cardiac_workspace.py plan server-tests
python tools/cardiac_workspace.py run server-tests
python tools/cardiac_workspace.py run direct-tests
python tools/cardiac_workspace.py run smoke-ar
python tools/cardiac_workspace.py status
```

`doctor` 只读检查源码入口、依赖和 NPZ 头信息，不加载完整轨迹，不据此认证数据质量。
`plan` 只显示命令；`run` 才执行指定任务，使用当前 Python，默认 CPU、两个数值计算线程、有超时。
`packet` 输出短状态、源码索引及本轮任务提示，供交互式 Agent 接续。
Linux 的 `bash queue.sh` 和 `queue.ps1` 是自动研究队列的包装入口；`.ps1` 仅在本机执行策略允许时可用。
当前 Windows 禁止执行脚本，请直接用上面的 Python 命令，无需修改系统策略。
`cardiac_workspace.py run` 执行一个实验；自动研究的入口是 `research_queue.py run/start`。
每次运行保存 `run.json`、`stdout.log`、`stderr.log`，新目录互不覆盖。
重跑成功也只代表相应运行完成，不会冻结其他任务或自动认证预测性能。
自动回合使用研究包指定的 `--config .../EXPERIMENT_CONFIG.json`，实验记录写入该回合的 `artifacts/experiments/`。

配置见 [cardiac-workspace.json](cardiac-workspace.json)。迁到服务器时用配置副本的
`project_root`、`data_dir` 和运行目录指定实际路径，再用 `--config /path/to/config.json`。
服务端 AR/PCA 的实际部署路径不同于本机；提交作业前检查现有 `slurm/` 脚本与冻结包。

## 文件导航

| 入口 | 内容 |
|---|---|
| [AGENTS.md](AGENTS.md) | 默认研究行为、项目边界和执行约定 |
| [ADAPTATION_REPORT.md](ADAPTATION_REPORT.md) | 本次修改范围、功能变化与实际验证 |
| [research-queue.json](research-queue.json) / [队列说明](problems/cardiac-research/README.md) | 自动 Codex 回合、预算、后台运行与恢复 |
| [CURRENT_STATE.md](projects/cardiac-ep/CURRENT_STATE.md) | 跨会话恢复 |
| [SOURCE_MAP.md](projects/cardiac-ep/SOURCE_MAP.md) | 源码位置、参数、数据与命令 |
| [experiments.md](projects/cardiac-ep/experiments.md) | 实验优先级、预算和验收 |
| agents/protocols/ | 数据、代码、模型验证与结果记录 |
| .agents/skills/cardiac-experiment/ | 代码修改、复现与实验技能 |
| .agents/skills/cardiac-paper-study/ | 从论文方法到本项目实现的技能 |
| archive/math-framework/ | 原数学专属模块，已退出默认入口 |

当前 v10 数据是参考域上的二维 CRN 合成场。几何形变没有进入动力学，
现有任务首先验证 V/Ca 预测；真实患者个体化、几何依赖和参数反演仍需单独定义数据与实验。
详见源码索引；不能把合成数据上的 smoke、低 loss 或单病例图当作临床/个体化验证。

## 检查工作台本身

```powershell
python -m unittest discover -s tools/tests -v
python tools/update_manifest.py check
```

源码清单不包含 `runs/`、`projects/cardiac-ep/queue/` 等生成产物。测试只依赖标准库；心脏模型的测试依赖其现有环境。
完整改造前快照在 `../../agent-adaptation-backup-20260916-131832/original-agent.zip`；
恢复队列前快照在 `agent-autonomy-backup-20260916-150206/before-autonomy.zip`；保留原 LICENSE，未提交 Git。
