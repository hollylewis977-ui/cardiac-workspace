# 心脏电生理与 AI 个体化建模：当前状态

2026-10-10：按用户要求新增独立 code/NeuralODE_BoundaryMemory/，将区域内部及各界面的动态/位置特征融合进原24维H，无独立E状态。CPU Slurm7204基线10测试、7207真实43,573节点/132区域完整250帧预测与重载/记忆梯度检查、7208最终23测试均通过。19,335条跨区域细边/675个有向界面，90,568参数（约+1.4%）。原Pure源码未改，九组冻结训练未改。真实数据0优化更新，无新精度或GPU时延结论，未追加第十组正式训练；证据results/neural_ode_boundary_memory/session_20261009_2047/。hard保证仅固定drive下的H方程，新drive经du/dt依赖H，非闭环稳定保证。

2026-10-13 10:12实时查询：7186_0（JobId7188）pure_baseline仍RUNNING，运行约95小时22分；下载日志完成221/500轮（epoch0–220）、44200/100000更新（44.2%）；其余8组JobArrayTaskLimit，7187等汇总。固定4例val当前最佳综合选模epoch218，score0.183648：V4.852mV/Ca26.381nM、激活漏检4.811%、误激活0.316%、匹配时差MAE3.779ms；最近验证epoch220：V4.770mV/Ca27.674nM、漏检26.234%、时差8.271ms。双场误差较10/10明显下降，但激活覆盖仍波动；不能称全部指标改善或收敛。最近五轮训练部分约23.1–23.6分钟，seconds不含随后验证/保存。第一组剩279轮，按近期速度粗估仍约4.5–5天（非完成保证）；尚无500轮完成/60例val/训练后测速。最新日志、指标及Slurm快照在results/neural_ode_full500/session_20261009_recovery/status_20261013_1011/。原RK4/h64/两图层500×200单卡设置、旧7176/7177及新边界记忆未启动正式训练的状态均未改；勿解除旧依赖。7185补测6.350/6.635秒为旧短训权重结果，非当前训练后速度。无后台Codex循环。

2026-10-10耗时核查（只读，非实测profiling）：暖身后每轮平均93.2输出帧、每帧2个1ms RK4步，200更新共149120次全图RHS/447360次细图乘，仅计未来前向；嵌套checkpoint使反向额外重算。loss_nodes4096不减少43573节点积分，当前基线无H。按近期23–35分钟训练/轮外推，单组500轮训练约8–12天，另有验证/评估与资源波动；九组串行需重新评估预算。未改积分步长、预算、模型或作业。

2026-10-10用户确认新时间目标为单组500×200及验证一天。建议独立轻量全图候选：2ms Heun RK2、h32、一图层、单层区间checkpoint；保留完整未来梯度和窗口。静态前向RHS少4倍、图聚合调用少6倍；整体提速未测。目标完整混合200更新≤144s，预留验证/评估时间。仅方案记录（experiments.md neural-ode-one-day），未修改模型/当前作业或追加正式训练。

2026-10-13训练/测试耗时核对：10/8同架构Pure基线初始化权重GPU预览（RTX4090，3例val×5重复）历史编码0.105474s、未来积分3.502848s、合计3.607940s/例；90例串行网络前向外推约5.4分钟，60例约3.6分钟，不含I/O/归一化/传输/加载/指标/绘图/排队。非当前500轮最终权重或完整90test实测；当前正式脚本自动安排60val及测速，90test尚未执行。证据session_20261008/preview/pure_baseline/inference/inference_benchmark.json。

2026-09-29 最新执行要求：所有项目代码（含研究队列、训练、评估、数据分析、绘图及 CPU/GPU 测试）统一通过 254 服务器 Slurm 排队执行，本机与登录节点只做文件操作、SSH、传输和作业提交/查询。下文的本地实验均为历史记录；本要求不扩大已有训练预算。

2026-09-29：独立研究任务 `neural-ode` 已注册，入口 `problems/cardiac-research/items/neural-ode/task.json`；尚未启动队列。接续第四轮原始结果，优先诊断重复激活、时序和早期 Ca。项目 `results/neural_ode/session_20260916/report.md`、`budget.json`、第四轮 `test_run.json` 已记录训练及 90 例评估结束；下文“第四轮正在运行”为历史。原 4 个训练名额已用尽，新任务不重置预算。

## 实验总表（设定 → 结果在哪 → 结果 → 问题）

| 实验 | 设定 | 结果在哪 | 结果 | 问题 / 限制 |
|---|---|---|---|---|
| AR 七组消融 | baseline/mixed/noise/range/clamp/events/nogru 各一次，500 轮/100000 更新，训练与选模均 ≤500 ms，90 例测试只输入 0–500 ms | results/ar/audit_20261008/summary.json；report.md、full/suite.json、analysis/summary.json | 病例平均 V/Ca RMSE：baseline 53.65/293.2，mixed 55.25/281.0，noise 50.79/215.5，range、clamp 同 baseline，events 51.86/272.0，nogru 38.14/271.2；旧基线晚期 66.80 mV/405.65 nM，首次激活漏检 46.86%，下降 F1 .180 | nogru 激活 F1 仅 .179，不能单看场误差；range 活跃轮数 0；单种子；测试集已用于诊断，不再是盲测；分析结论见台账 AR-* |
| PCA-GRU/MLP 对照 | 固定 PCA256+256 基底，GRU256 与无记忆 MLP，≤500 ms 选模 | 服务器 code/pca；slurm/pca.md | 未提交作业 | 待 AR 量化后启动 |
| Neural ODE 第 3/4 轮 | 无 PCA，V/Ca/h 联合 RK4；AR 权重初始化后各 40 更新微调；训练标签可至 1000 ms，测试只输入 ≤500 ms | results/neural_ode/session_20260916/{report.md,budget.json}，round_4_graph_memory_bce/ | 第 3 轮 90 例全窗 25.77 mV/170.8 nM 对 AR 53.65/293.2，90/90 改善；第 4 轮双场与下降事件显著改善，激活 F1 .567 低于 AR .571 | 激活 F1、早期 Ca 未达标，联合验收未通过；四轮名额用完；与 AR 的监督/选模协议不同，不能单独证明架构因果 |
| 空间记忆 H 六组 | code/NeuralODE_GlobalMemory；预训练/从零 × 节点 h/区域 H/硬约束 H，各 80 更新、8 epoch 课程、12 例验证 | results/neural_ode_global_memory/session_20261002/screen/、screening_review.json；Slurm 7162 | baseline/multi/multi_hard V 22.97/22.96/17.57 mV，Ca 148.1/148.4/134.7 nM，Dice .495/.500/.567；三组从零约 35.8 mV/336 nM、Dice .171 | hard 激活时间 MAE 25.2→35.5 ms、误激活 .65%→4.41%，不是全面改善；80 更新不能否定从零；预算 6395 s/6 组已用完 |
| 纯导数 ODE | code/NeuralODE_Pure，直接输出 du/dt、dh/dt，无 AR 增量参数化；无H基线84,546、multi89,280参数 | results/neural_ode_pure/session_20261008/；Slurm 7164、7173；训练见下行 | 早期CPU实现与真实网格前向/重载检查通过；正式无H训练现221轮 | 早期检查不证明预测有效；训练中4例val见下行，尚无最终训练后结论 |
| 九组 500×200 正式训练 | 旧 6 组 + Pure 3 组，各 100000 更新，单卡串行；每组 best 测速（3 例、2 预热 5 重复）及 60 例 val | results/neural_ode_full500/session_20261009_recovery/；Slurm 7184–7187 | 10/13 10:12：Pure基线221/500轮、44200更新，其余8组排队；最佳4例val epoch218为V4.852mV/Ca26.381nM、漏检4.811%，最新漏检26.234%；详见顶部实时段 | 还未完成500轮/60例val/训练后测速；7176/7177已被替代勿解除依赖；旧预览不是训练后速度 |

## 固定事实与协议

此工作台位于项目内（2026-10-09 改名 cardiac-workspace）。主线 TC_GCN_server 的 AR/PCA；FBNO_time_forecast 为直接时间查询对照；Neural ODE 分支见 SOURCE_MAP。配置 ../../cardiac-workspace.json。
v10 是二维 CRN 合成数据，几何形变未进动力学；21 维完整初态只保留 V/Ca 观测；数据按完整批次 20/2/3 切分；观测至 500 ms、未来 502–1000 ms；训练监督与验证选模时间范围各自记录。合成预测不等于患者个体化验证。
自动 Codex 队列（tools/research_queue.py）至今未真实运行，CLI 未登录；所有记录由交互会话维护。Windows 用 Python 主入口，queue.ps1 受执行策略限制。
2026-10-09 整理：ar-pca、neural-ode 任务已停用；当前任务 neural-ode-full500。9/16 适配段、AR/PCA 衔接段、9/17 Neural ODE 段与迁移包段原文已移入 progress.md。

## 下一动作

跟踪 7188 及其余 8 组串行 → 7187 汇总；每组 best 测速及 60 例 val；与 AR 七组审计配对比较并写报告。不解除旧 7176/7177 依赖，不追加训练组。
