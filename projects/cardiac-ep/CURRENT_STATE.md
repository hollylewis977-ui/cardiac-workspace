# 当前状态

## 控制
- updated-at: 2026-10-14
- queue-status: pushing
- search-contract: either
- evidence-ceiling: proof-draft

## 题目与范围
- 正式陈述：见 problem.md P0，仅输入 0–500 ms 观测，预测 502–1000 ms 的 V/Ca 与激活事件。
- 范围排除：几何个体化与参数反演（第二道题 personalization）；三维 crn 数据；真实患者验证。
- 执行约束：所有项目代码在 254 服务器 Slurm 分配内运行；本机只做文件、SSH、传输、提交与查询。

## 当前状态
- 最强可用结果：AR-BASE-002（proof-draft，旧 AR 基线复现）；NODE-GRAPH-003（proof-draft，ODE 第 3 轮 90 例双场改善）；NODE-GLOBAL-SCREEN-001（experimental，hard-H 筛选）；NODE-BOUNDARY-001（partial-result，边界记忆分支实现检查通过，真实数据 0 更新）。
- 当前结论（2026-10-14 14:27:50 +08:00 实时查询）：7186_0（JobId7188）pure_baseline仍RUNNING，运行5天3小时37分，Restarts=0；下载日志完成276/500轮（epoch0–275）、55200/100000更新（55.2%），较10/13 10:12增加55轮。其余8组JobArrayTaskLimit，7187等汇总。固定4例val最佳综合选模日志epoch246，score0.169047：V4.308mV/Ca24.664nM、激活漏检4.403%、误激活0.294%、匹配时差MAE3.268ms；最近验证epoch274：V5.340mV/Ca29.978nM、漏检25.361%、误激活0.200%、时差4.303ms。最佳记录较昨日改善，但激活覆盖仍波动，不能称收敛。近期训练部分通常约23–29分钟/轮，epoch260曾约106分钟（原因未定位）；seconds不含随后验证/保存。第一组剩224轮，按两次查询间约28小时16分推进55轮粗估仍约4.8天（仅该组训练，非完成保证）；尚无500轮完成/60例val/训练后测速。最新证据在results/neural_ode_full500/session_20261009_recovery/status_20261014_1426/。本次仅查询/下载日志和更新记录，无项目代码执行或远程作业变更；原RK4/h64/两图层500×200单卡设置、旧7176/7177及新边界记忆未启动正式训练的状态均未改，勿解除旧依赖。7185补测为旧短训权重结果，非当前训练后速度。无后台Codex循环。
- 今日可用结果：NODE-PURE-INTERIM-001（experimental，中途权重90例完整测试）。10/14 Slurm7275/7276均完成exit0：冻结Pure best epoch246（49400更新；冻结时原训练完成277轮），90例全窗病例平均V5.613mV/Ca37.386nM、激活F1 .8892、下降F1 .9391、首次激活漏检5.343%、误激活1.477%、匹配MAE5.234ms；相对旧ODE第4轮均值误差降低67.48%/68.36%，V90/90、Ca89/90例改善。全部预测有限。当前权重RTX4090实测完整rollout中位3.518秒/例，90例含指标/首两例出图约1123秒；不等于500轮最终模型。证据results/neural_ode_full500/evaluation_20261014/，comparison/report.md及PNG/CSV已下载。旧ODE第3/4轮为AR初始化后短微调，本轮Pure从零，训练预算/监督/选模/clamp不同，比较不证明架构因果；测试集已暴露，未新增独立复现。原九组训练未改。
- 待研究者决定：P0 的验收阈值未填；neural-ode-one-day 轻量候选是否实施；AR-BASE-001 何时进入 claim-audit。

### 实验总表（设定 → 结果在哪 → 结果 → 问题）

| 实验 | 设定 | 结果在哪 | 结果 | 问题 / 限制 |
|---|---|---|---|---|
| AR 七组消融 | baseline/mixed/noise/range/clamp/events/nogru 各一次，500 轮/100000 更新，训练与选模均 ≤500 ms，90 例测试只输入 0–500 ms | results/ar/audit_20261008/summary.json；report.md、full/suite.json、analysis/summary.json | 病例平均 V/Ca RMSE：baseline 53.65/293.2，mixed 55.25/281.0，noise 50.79/215.5，range、clamp 同 baseline，events 51.86/272.0，nogru 38.14/271.2；旧基线晚期 66.80 mV/405.65 nM，首次激活漏检 46.86%，下降 F1 .180 | nogru 激活 F1 仅 .179，不能单看场误差；range 活跃轮数 0；单种子；测试集已用于诊断，不再是盲测；分析结论见台账 AR-* |
| PCA-GRU/MLP 对照 | 固定 PCA256+256 基底，GRU256 与无记忆 MLP，≤500 ms 选模 | 服务器 code/pca；slurm/pca.md | 未提交作业 | 待 AR 量化后启动 |
| Neural ODE 第 3/4 轮 | 无 PCA，V/Ca/h 联合 RK4；AR 权重初始化后各 40 更新微调；训练标签可至 1000 ms，测试只输入 ≤500 ms | results/neural_ode/session_20260916/{report.md,budget.json}，round_4_graph_memory_bce/ | 第 3 轮 90 例全窗 25.77 mV/170.8 nM 对 AR 53.65/293.2，90/90 改善；第 4 轮双场与下降事件显著改善，激活 F1 .567 低于 AR .571 | 激活 F1、早期 Ca 未达标，联合验收未通过；四轮名额用完；与 AR 的监督/选模协议不同，不能单独证明架构因果 |
| 空间记忆 H 六组 | code/NeuralODE_GlobalMemory；预训练/从零 × 节点 h/区域 H/硬约束 H，各 80 更新、8 epoch 课程、12 例验证 | results/neural_ode_global_memory/session_20261002/screen/、screening_review.json；Slurm 7162 | baseline/multi/multi_hard V 22.97/22.96/17.57 mV，Ca 148.1/148.4/134.7 nM，Dice .495/.500/.567；三组从零约 35.8 mV/336 nM、Dice .171 | hard 激活时间 MAE 25.2→35.5 ms、误激活 .65%→4.41%，不是全面改善；80 更新不能否定从零；预算 6395 s/6 组已用完 |
| 纯导数 ODE | code/NeuralODE_Pure，直接输出 du/dt、dh/dt，无 AR 增量参数化；无H基线84,546、multi89,280参数 | results/neural_ode_pure/session_20261008/；中途测试results/neural_ode_full500/evaluation_20261014/ | 7275/7276完成：epoch246权重90例V5.613mV/Ca37.386nM，激活F1 .8892，漏检5.343%；完整rollout中位3.518秒/例 | 单种子中途权重，非500轮完成；旧AR/ODE训练与选模协议不同；尚无独立数值复现 |
| 九组 500×200 正式训练 | 旧 6 组 + Pure 3 组，各 100000 更新，单卡串行；每组 best 测速（3 例、2 预热 5 重复）及 60 例 val | results/neural_ode_full500/session_20261009_recovery/；Slurm 7184–7187 | 10/14 14:27：Pure基线276/500轮、55200更新，其余8组排队；最佳4例val epoch246为V4.308mV/Ca24.664nM、漏检4.403%，最近epoch274漏检25.361%；详见上方实时段 | 还未完成500轮/60例val/训练后测速；7176/7177已被替代勿解除依赖；旧预览不是训练后速度 |

## 活动前沿
- 最小开放缺口：GAP-S1-1（闭包未检验）。
- 活动路线：A5 区域记忆态 H（九组正式训练）；A1 AR 七组审计作对照。
- 值得记住的阻塞路线：A4 直接时间查询（missing-tool，无严格选模开关）；A3 的协议差异未统一。

## 下一回合
- 目标：跟踪 7188 及其余 8 组串行 → 7187 汇总；每组 best 测速及 60 例 val；与 AR 七组审计配对比较并写报告。
- 验收：neural-ode-full500 的 C1–C5；不解除旧 7176/7177 依赖，不追加训练组。

## 证据指针
- 台账 ID：AR-BASE-002、NODE-GRAPH-003、NODE-GLOBAL-SCREEN-001、NODE-BOUNDARY-001、NODE-PURE-INTERIM-001。
- claim-map 节点：A1、A3、A5、E4；GAP-S1-1、GAP-E4-1。
- 直接证据文件：results/neural_ode_full500/evaluation_20261014/；results/neural_ode_full500/session_20261009_recovery/status_20261014_1426/；results/ar/audit_20261008/summary.json。
- 自动 Codex 队列至今未真实运行；所有记录由交互式会话维护。2026-10-13 之前的叙述段已逐字移入 progress.md。
