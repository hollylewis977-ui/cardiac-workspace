# 当前状态

## 控制
- updated-at: 2026-11-02
- queue-status: pushing
- search-contract: either
- evidence-ceiling: proof-draft

## 题目与范围
- 正式陈述：见 problem.md P0，仅输入 0–500 ms 观测，预测 502–1000 ms 的 V/Ca 与激活事件。
- 范围排除：几何个体化与参数反演（第二道题 personalization）；三维 crn 数据；真实患者验证。
- 执行约束：当前10/19训练明确使用254服务器Slurm；10/17本地授权仅解释当时推理加速及低维NODE历史实验。10/23研究者仅允许本次本地新增Pure测试例b022_s02推理/绘图，默认Slurm规则不变；其他既有远程作业不改。

## 当前状态
- 最强可用结果：AR-BASE-002（proof-draft，旧 AR 基线复现）；NODE-GRAPH-003（proof-draft，ODE 第 3 轮 90 例双场改善）；NODE-GLOBAL-SCREEN-001（experimental，hard-H 筛选）；NODE-BOUNDARY-001（partial-result，边界记忆分支实现检查通过，真实数据 0 更新）。
- 实时训练查询（11/2 11:11 +08:00）：九组已有2组完成训练/测速/60val；pure_baseline于10/18完成500轮/100000更新，best epoch418；pure_multi于10/29完成相同预算，best epoch482（epoch均从0起）。第三组pure_multi_hard为7186_2/JobId7614，RUNNING、Restarts=0，已完成165/500轮、33000/100000更新（33%），日志11:02更新；余6组JobArrayTaskLimit，7187等待汇总。旧7176/7177未改。本次仅查询下载，未改作业；完成依据原始产物。
- 既有中途结果：NODE-PURE-INTERIM-001（experimental，中途权重90例完整测试）。10/14 Slurm7275/7276均完成exit0：冻结Pure best epoch246（49400更新；冻结时原训练完成277轮），90例全窗病例平均V5.613mV/Ca37.386nM、激活F1 .8892、下降F1 .9391、首次激活漏检5.343%、误激活1.477%、匹配MAE5.234ms；相对旧ODE第4轮均值误差降低67.48%/68.36%，V90/90、Ca89/90例改善。全部预测有限。该中途权重RTX4090实测完整rollout中位3.518秒/例，90例含指标/首两例出图约1123秒；不等于500轮最终模型。证据results/neural_ode_full500/evaluation_20261014/，comparison/report.md及PNG/CSV已下载。旧ODE第3/4轮为AR初始化后短微调，本轮Pure从零，训练预算/监督/选模/clamp不同，比较不证明架构因果；测试集已暴露，未新增独立复现。原九组训练未改。
- 待研究者决定：P0 的验收阈值未填；neural-ode-one-day 轻量候选是否实施；AR-BASE-001 何时进入 claim-audit。
- 正式图现状：archive/neural_ode_results_reorg_20261102/NeuralODE/results/ode_pure/eval/plots/（254为evaluation_20261014/plots_sci_20261014/）含b022_s00、b022_s01与10/19新增失效例b023_s13各4张PNG，三行真值/预测/误差×三列600/800/1000ms、viridis/magma、单帧NRMSE，共15PNG，snapshot_errors.csv共9行。b023_s13为epoch246权重90例中全窗V RMSE最大者（13.785mV/142.327nM、激活F1 .570、首次激活MAE31.87ms），Slurm7368 exit0/14.55秒（rollout导出7.7秒、绘图5.1秒），逐帧误差与test90指标一致，显示范围单独计算，不与b022两例比色；预测800ms后在右下生成真值没有的激活波。纯推理时延沿用10/14测速（同权重RTX4090中位3.518秒/例）。plot_snapshot_sci.py新增--cases。10/14–10/15的重绘、覆盖与交付整理五条记录已原文移入progress.md 2026-10-19节；运行区archive/neural_ode_full500/evaluation_20261014/plots_sci_20261019_b023s13/。

### 实验总表（设定 → 结果在哪 → 结果 → 问题）

10/24图：plots/complete_ap_three_cases/已换低误差点（V2.72/3.21/2.48%、Ca1.50/1.69/1.03%；分母150mV/1200nM，评502–1000ms）。16例预测中按误差选点，非总体性能；95%复极≤990ms、末值距基线≤3mV。等级experimental；冻结archive/complete_ap_search_20261024/session_007/；详见progress。

10/23新增正式图：Pure epoch246、测试集按文件顺序取下一未绘病例b022_s02；本次明确授权本机运行。交付archive/neural_ode_results_reorg_20261102/NeuralODE/results/ode_pure/eval/plots/b022_s02/（4PNG+CSV+量化JSON），250帧误差与原test90一致；全窗固定量程NRMSE(V/Ca)2.864710%/1.229194%（分母150mV/1200nM）。冻结源码、预测、核查与日志archive/visualizetions_20261023/session_001/；沿用NODE-PURE-INTERIM-001，不提升证据等级。
同例原始数据追查：直接读batch022/sample02的0–2000ms，导出真值251帧与原NPZ经既定归一化往返逐值一致；最后上冲778ms，最后V>−20mV帧812ms，1000ms V[−80,−77.4375]mV，后段无新上冲。该例为活动终止，图中主要是复极/Ca回落；真值图在同目录raw_truth/，证据archive/dataset_checks/truth_b022s02_20261023/session_001/。仅本次同例本地追查，未扩大计算授权。

| 实验 | 设定 | 结果在哪 | 结果 | 问题 / 限制 |
|---|---|---|---|---|
| AR 七组消融 | baseline/mixed/noise/range/clamp/events/nogru 各一次，500 轮/100000 更新，训练与选模均 ≤500 ms，90 例测试只输入 0–500 ms | results/ar/audit_20261008/summary.json；report.md、full/suite.json、analysis/summary.json | 病例平均 V/Ca RMSE：baseline 53.65/293.2，mixed 55.25/281.0，noise 50.79/215.5，range、clamp 同 baseline，events 51.86/272.0，nogru 38.14/271.2；旧基线晚期 66.80 mV/405.65 nM，首次激活漏检 46.86%，下降 F1 .180 | nogru 激活 F1 仅 .179，不能单看场误差；range 活跃轮数 0；单种子；测试集已用于诊断，不再是盲测；分析结论见台账 AR-* |
| PCA-GRU/MLP 对照 | 固定 PCA256+256 基底，GRU256 与无记忆 MLP，≤500 ms 选模 | 服务器 code/pca；slurm/pca.md | 未提交作业 | 待 AR 量化后启动 |
| Neural ODE 第 3/4 轮 | 无 PCA，V/Ca/h 联合 RK4；AR 权重初始化后各 40 更新微调；训练标签可至 1000 ms，测试只输入 ≤500 ms | results/neural_ode/session_20260916/{report.md,budget.json}，round_4_graph_memory_bce/ | 第 3 轮 90 例全窗 25.77 mV/170.8 nM 对 AR 53.65/293.2，90/90 改善；第 4 轮双场与下降事件显著改善，激活 F1 .567 低于 AR .571 | 激活 F1、早期 Ca 未达标，联合验收未通过；四轮名额用完；与 AR 的监督/选模协议不同，不能单独证明架构因果 |
| 空间记忆 H 六组 | code/NeuralODE_GlobalMemory；预训练/从零 × 节点 h/区域 H/硬约束 H，各 80 更新、8 epoch 课程、12 例验证 | results/neural_ode_global_memory/session_20261002/screen/、screening_review.json；Slurm 7162 | baseline/multi/multi_hard V 22.97/22.96/17.57 mV，Ca 148.1/148.4/134.7 nM，Dice .495/.500/.567；三组从零约 35.8 mV/336 nM、Dice .171 | hard 激活时间 MAE 25.2→35.5 ms、误激活 .65%→4.41%，不是全面改善；80 更新不能否定从零；预算 6395 s/6 组已用完 |
| 纯导数 ODE | code/NeuralODE_Pure，直接输出 du/dt、dh/dt，无 AR 增量参数化；无H基线84,546、multi89,280参数 | results/neural_ode_pure/session_20261008/；中途测试results/neural_ode_full500/evaluation_20261014/ | 7275/7276完成：epoch246权重90例V5.613mV/Ca37.386nM，激活F1 .8892，漏检5.343%；完整rollout中位3.518秒/例 | 单种子中途权重，非500轮完成；旧AR/ODE训练与选模协议不同；尚无独立数值复现 |
| 九组 500×200 正式训练 | 各100000更新、单卡串行；best测速3例/暖2/重复5及60val | results/neural_ode_full500/session_20261009_recovery/；本次证据archive/neural_ode_full500/status_20261102_1109/ | 11/2：Pure基线/区域H均完成；60val病例均值V/Ca RMSE分别5.132mV/38.125nM、4.380mV/30.034nM，激活F1 .883185/.897244；4090完整模型推理中位3.606/5.155s，排除I/O；hard-H完成165/500轮 | 此行为60val；最终best的90test见NODE-PURE-MEMORY-TEST90-001，不能称H全面改善。余6组等待，7187未汇总，旧7176/7177依赖勿动 |

## 活动前沿
- 11/2训练加速NODE-PECE-TRAIN-001：同hard-H epoch134，实际连续20更新RK4/Heun分组/PECE分组258.029/113.596/110.508s（含取数，不含验证/保存），wall加速2.271/2.335倍；纯更新245.345/104.311/104.510s，后两者近等速，峰值显存6.270/8.942GB。三组3val短训后均退化，仅支持速度、不证明长期收敛；优先Heun分组作为候选。新增可微PECE及分组checkpoint，默认RK4、resume与原队列不改。8374/8378/8380成功；8379汇总重复目录失败已修复，33既有检查与梯度/重载通过；experimental。交付NeuralODE/results/training_speed/pece_20261102/，冻结archive/pece_training_20261102/；此前Heun60val见NODE-SOLVER-TRAIN-001。
- 11/2两组最终best90test已完成：无区域/区域H的平均NRMSE V3.208/2.767%、Ca2.948/2.337%（每例全窗后90例等权，分母150mV/1200nM）；激活F1 .888409/.899753，首次漏检4.575/4.755%；4090纯模型平均3.509/5.096s/例。H平均场误差更低但漏检略增、推理更慢，V79/90、Ca54/90例改善。Slurm8295 COMPLETED/0:0；NODE-PURE-MEMORY-TEST90-001，experimental、单种子/已暴露二维合成测试，非独立复现。交付NeuralODE/results/test90/；冻结archive/pure_memory_test90_20261102/session_001/。正式图六病例共36张于NeuralODE/results/plots/{pure_baseline,pure_multi}/<病例>/，同批error/metadata/traces.csv/comparison/量化CSV在archive/neural_ode_results_reorg_20261102/NeuralODE/results/ode_pure/eval/test90_final_20261102/plots/（8333/exit0）；绘图冻结archive/pure_memory_plots_20261102/session_001/。
- 10/26 Pure246全部90test逐帧误差图已由既有7275报告汇总（无新推理）：502–1000ms，每例43573节点空间RMSE后病例等权均值；600/800/1000ms的V/Ca NRMSE均值为2.436/1.210%、3.999/3.411%、4.816/4.837%，固定分母150mV/1200nM，阴影为病例25%–75%分位区间。交付archive/neural_ode_results_reorg_20261102/NeuralODE/results/ode_pure/eval/test90/time_errors/，CSV保留全部90×250帧；254 CPU Slurm7610通过，冻结archive/test90_time_errors_20261026/session_002/。沿用NODE-PURE-INTERIM-001的experimental范围（中途权重、二维合成、测试历史已暴露）。
- 10/22核实7440已完成250轮/50000，best21600/108轮未变。7548实测90test单帧平均NRMSE(V/Ca,%):600ms9.677/7.769、800ms13.353/12.767、1000ms14.401/16.760，分母150mV/1200nM。非3val或窗口均值；NODE-LATENT-TEST90-SNAP-001。证据archive/latent_test90_snapshots_20261022/session_001/，交付archive/neural_ode_results_reorg_20261102/NeuralODE/results/latent/test90/。
- 最小开放缺口：GAP-S1-1（闭包未检验）。
- 活动路线：A5 区域记忆态 H（九组正式训练）；A1 AR 七组审计作对照。
- 值得记住的阻塞路线：A4 直接时间查询（missing-tool，无严格选模开关）；A3 的协议差异未统一。

## 下一回合
- 目标：跟踪7186_2/7614的hard-H及后续6组串行 → 7187汇总；前两组已完成best测速/60val/90test；最终与AR七组按协议差异配对。
- 验收：neural-ode-full500 的 C1–C5；不解除旧 7176/7177 依赖，不追加训练组。

## 证据指针
- 台账 ID：AR-BASE-002、NODE-GRAPH-003、NODE-GLOBAL-SCREEN-001、NODE-BOUNDARY-001、NODE-PURE-INTERIM-001。
- claim-map 节点：A1、A3、A5、E4；GAP-S1-1、GAP-E4-1。
- 直接证据文件：results/neural_ode_full500/evaluation_20261014/；results/neural_ode_full500/session_20261009_recovery/status_20261014_1426/；results/ar/audit_20261008/summary.json。
- 自动 Codex 队列至今未真实运行；所有记录由交互式会话维护。2026-10-13 之前的叙述段已逐字移入 progress.md。
