# 验证台账
等级定义见 agents/core/research-core.md；目前没有条目经过 claim-audit，最高 proof-draft。

## 2026-10-22：Latent250训练后90例三时刻误差

- ID：`NODE-LATENT-TEST90-SNAP-001`；experimental，来源internal；单种子v10二维CRN，训练40例/验证选模3例，完整90test单帧误差；非独立复现、临床验证、全窗误差或90例测速。
- 7440日志与最终report证实累计50000更新/250轮结束，最佳仍21600更新/第108轮；使用best.pt SHA13ca9a2b5ee57ec5ef912eef108263620a752a83410699207afaf0f25ad3ccc6，codec SHA7def785005f25d8f237d1f095dded4bf982b566453b51d3586c6c19e79845ad1。4096局部PCA+64记忆、RK4 2ms，未改模型/权重/基底或重新选模。
- Slurm7548（5090）对batch022–024各30例，只输入0–500ms全251帧，自主生成502–1000ms全250帧，全部有限。在600/800/1000ms分别取单帧43573节点空间RMSE，V除150mV、Ca除1200nM后乘100，再对90例算术平均。结果V/Ca分别**9.6773882841%/7.7692521603%**、**13.3531644719%/12.7667077609%**、**14.4008284174%/16.7595747957%**；不是600–800ms等区间RMSE，也不是先平均场或合并病例后开方。
- 原始binary16到固定float32归一化采用65536值查表后GPU精确取值，全部90例观测SHA与既有Pure冻结test90对应值相同。潜态ODE CUDAgraph与首个真实病例eager全250帧/4160状态逐位一致（max差0）；首例三时刻误差与原Latent图一致。后续每例独立重新编码历史并推进，无未来真值回灌。未将此控制升级独立数值复现，test在项目历史已开发暴露。
- 实际保存270行CSV；同Slurm作业内后续CPU步骤用statistics重算均值与物理单位归一化通过。控制器COMPLETED/ExitCode0:0/38秒，完整作业14:16:56–14:17:34；35.27秒内部耗时包含输入准备/哈希/评分，不能除90冒充标准推理时延。CPU7549仅整理量化文件，无新预测。
- 直接证据：`archive/latent_test90_snapshots_20261022/session_001/{summary.json,per_case_snapshots.csv,inputs.json,verified_summary.json,final_scontrol.txt,source/,SHA256SUMS,publication.json,training_completion/}`；正式量化交付`NeuralODE/results/latent/test90/{snapshot_nrmse.json,per_case_snapshots.csv}`，交付目录不含源码/日志/NPZ/校验清单。未新增活跃test或实验代码文件。

## 2026-10-22：正式绘图代码收进NeuralODE

- ID：`VISUAL-SCI-PORT-001`；partial-result，来源internal；验证维度code/既有预测图重现supported，不构成新模型精度或独立科学验证。
- 用户要求保留拼写`visualizetions`。`NeuralODE/visualizetions/`自包含渲染器和批量入口，`NeuralODE/slurm/visualizetions.sbatch`提交；不再依赖外部绘图程序或旧快照运行器。现有模型、数据和权重未修改。
- Slurm7547/254/RTX5090完成三阶段核查：15个Python源文件语法、两个CLI help和bash语法通过；8个核心加载/归一化/绘图函数AST与原版完全相同。复用原epoch246的b022_s00/b022_s01预测重绘，两例calcium.png与traces.png共4张图的RGBA像素和尺寸与原图完全相同，三点CSV及共享场/误差色标一致，未选b023_s13的CSV三行保留。
- 当前统一代码从同一epoch246权重重新导出b022_s00再绘图通过，所有250帧误差与旧test90指标在rtol2e-5/atol1e-4物理mV/nM容差内一致；三时刻NRMSE也通过。重新推理不是原数组逐位复刻，不把这一步称像素相同；未重训或评估新病例。
- NRMSE固定分母150mV/1200nM，三列600/800/1000ms、三行真值/预测/物理绝对误差；三点最近节点4610/16113/31927，曲线显示500ms锚点而评分只含502–1000ms。交付仅PNG/CSV/量化JSON，预测/源文件/命令/manifest留独立工作目录；可选90例模型比较用原Pure与旧ODE4的完整报告实际验证，不把不同训练协议归因于架构。
- 直接证据：`archive/visualizetions_20261022/session_001/{verified_syntax.json,verified_reuse.json,verified_export.json,slurm-7547.out,allocation_7547.txt,final_scontrol.txt,completion.json,SHA256SUMS,source/,reference/,published_reuse/,published_export/,run_reuse/manifest.json,run_export/manifest.json}`；完整新预测NPZ保留服务器同会话run_export/predictions/。实时控制器确认COMPLETED、ExitCode0:0、运行40秒（12:19:47–12:20:27），与三阶段通过及末尾完成标记一致。源码与已核查冻结副本哈希一致，证据下载包SHA通过；已目视核查重绘Ca和三点曲线。无新增test文件或新增依赖。

## 2026-10-20：原Pure246在5090的PECE速度中途记录

- ID：`NODE-PURE-SPEED-5090-001`；experimental，仅已打印的预测时延观察，完整screen和90test未完成。
- 7487/RTX5090，同一epoch246权重，3val/B1/暖2重5；15条RK4为3.354020–3.447771秒，15条PECE+CSR/high为1.621419–1.693563秒。约3.37→1.68秒/例、约2倍；差异同时包含积分器、CSR和matmul high，不归因PECE单因素。
- 完整251帧历史编码+250帧V/Ca预测，GPU同步计时；排除数据准备、传输、有限性检查和评分。源代码在每条timing输出前验证有限性，已核查日志顺序对应两配置。首次结果延迟来自计时前完整reference事件/空间评分。
- 11:44:01时7487仍RUNNING，screen报告与守卫尚未完成，无新90例精度结论；快测7488排队，无结果。直接证据`archive/ode_inference_speed_20261020_rtx5090/session_001/status_20261020_1145/{slurm-7487.out,scontrol_7487.txt,status.md}`与冻结source，不升级独立验证。
- 12:00更新：screen守卫已通过；用户明确最终需要90test而非3val。7487内只读CPU进度汇总显示RK4测试12/90，均值3.384723599秒/例、中位3.354683998秒、模型合计40.616683秒，12例观测SHA匹配冻结对应子集，NFE2000；PECE测试未开始。部分均值不能当90例结果，也不能与验证集PECE直接拼接为test加速比。新证据`archive/ode_inference_speed_20261020_rtx5090/session_001/status_20261020_1201/{partial_metrics.json,summarize_progress.py,screen_verified.json}`；7488仍排队，无额外GPU测速重叠。

## 2026-10-20：v10活动持续时间与原Pure误差分层

- ID：`DATA-V10-ACTIVITY-001`；experimental，来源internal，进展experimental-signal；既有原始数据扫描的重新统计，非新模型预测或独立验证。
- 范围：25个v10批次/750例的本地与服务器副本，大小及首1MiB/尾64KiB指纹全部相同；只证明这部分文件字节匹配，不冒充全量哈希。活动分层当前覆盖原90例test，依7374扫描的完整0–2000ms/2ms真值；7486达30分钟时限终止，750例新raw扫描未完成。
- 定义：活动为保存帧有节点V>−20mV，上冲为V由≤−20跨到>−20。800ms无新上冲34/90=37.7778%；800ms时无活动且之后无上冲23/90=25.5556%，因此每个后续保存帧均无活动；1000ms后无上冲39/90=43.3333%。无上冲不等于复极结束，电活动阈值静默不等于Ca恒定或V为0。
- 原Pure246、0–500ms输入/502–1000ms评分、病例平均RMSE：后1000ms无上冲39例V3.225973mV/Ca13.508013nM；其余51例7.437520/55.646079；后1500ms仍有上冲43例7.397442/55.256049。最后800–1000ms窗口，39例2.606808/15.098309，对51例9.991759/78.706797。分组使用未来真值，仅用于分层评分，不进入预测或权重选择。
- 解释：混合均值受病例动力学组成影响；不证明现有模型无效、数据生成错误，亦不把阈值持续活动直接认证为折返或临床AF。2s以后为未观测/右删失，不能宣称永久终止。既有test已开发暴露，新数据按母轨迹分组并预先冻结划分。
- 用户选择：持续与自行终止都保留，分层评估。D降低仅为待验证方案：实际D_code0.08，网格0.4mm；代码0.36mm/0.193注释与执行值不符。拟0.08/0.06/0.04相同训练初值配对，先CV/传播与时间步核查；尚未生成新数据或执行D扫描。
- 直接证据：`archive/dataset_checks/activity_audit_20261020/{prior_test90_strata.json,file_verification.json,local_file_fingerprints.json,prior_test90_scan.csv,pure_epoch246_per_case.csv,conductivity_plan.json,source/}`；原始7374证据`archive/dataset_checks/quiescence_scan_20261019/`。重分层在7486分配内执行，未本地跑项目代码。

## 2026-10-19：Latent4096真实训练与速度

- ID：`NODE-LATENT-SCREEN-001`；experimental，来源internal；代码/GPU前后向supported，3val预测为有限短训观察，未达到替换现有模型的精度要求。
- Slurm7377在5090上完成1000更新，best1000；40例train/P1000、固定3val，0–500ms历史自主预测502–1000ms全250帧，未看test。模型16区局部PCA总D4096、记忆64、MLP宽128、RK4 2ms；与原Pure的训练病例/预算不同，不归因单一架构因素。
- 真实预测病例平均V/Ca RMSE **25.546219663mV / 162.063293383nM**，固定量程NRMSE **17.030813% / 13.505274%**；激活micro F1 **.003114889**（129匹配/82295真事件、533预测事件），下降 **.203696695**。这与此前oracle重构1.15%/1.18%是不同指标对象，不得混用。
- 训练后best的sample14/B1完整历史投影＋GRU＋潜态ODE＋全场解码，暖2重5：普通GPU流程 **536.640770ms**，仅ODE CUDAgraph的完整流程 **47.647819ms**；完整graph流程加输出D2H共 **106.479629ms**。输入已在GPU，排除磁盘/H2D、评分、冷初始化；不是每帧时间或批摊销。
- 直接证据：项目`archive/latent_ode_train_20261019/screen_001/{run/report.json,run/validation.csv,evaluation/report.json,preflight.json,slurm-7377.out,completion.json}`。权重保留服务器同会话run/best.pt及last.pt；源码冻结在source/及run/source。控制器记录已过保留期，以两阶段completed状态及末尾完成标记核验脚本结束，不补写sacct退出码。
- 结论：训练后几十毫秒计算可行；当前预测与激活覆盖不足。只读复核确认best1000与计时口径，不升级独立数值复现等级，不据1000更新否定整个Neural ODE方法族。

## 2026-10-19：PCA重构结论记忆（10/17实验，无新预测结果）

- ID：`NODE-LATENT-RECON-001`；等级experimental，来源internal；表示重构supported，未来预测not-assessed。
- 条件：v10二维CRN，train000–019中40例/P1000的1280快照拟合16个连通区域PCA，每区每通道128阶，总系数4096；固定val `batch020/sample14`、`batch021/sample16`、`batch020/sample05`，502–1000ms全部250帧/43573节点；训练与评估归一化沿用固定量程。
- 数值：病例平均V重构RMSE **1.7271431088mV**，Ca **14.1819236887nM**。百分比是`100 × RMSE / 固定量程`，分母分别150mV、1200nM，故为 **1.1514287392% / 1.1818269741%**；不是丢弃方差比例、相对信号范数误差或总信息损失比例。
- 事件限制：激活micro F1 **.9107103369**、下降 **.9524895629**；升到8192系数时场误差更低但激活F1降至.9067755257，不能把均方误差小概括为无损。未来真值先压缩再还原，仅为oracle诊断；没有证明从0–500ms预测未来的精度，也没有完成新模型训练。
- 直接证据：项目`archive/latent_ode_feasibility_20261017/screen_local_highrank/report.json`中`local_128`及`source/`、`local_max_codec.pt`；三次运行命令在同archive的`completion.json`；量化交付`code/NeuralODE/results/ode_pure/latent_feasibility_20261017/{summary.json,candidates.csv}`。181项既有CPU重算存证为`independent_verification.json`，不升级为独立GPU预测复现。
- 源码收尾：一次性筛选/汇总脚本从活跃code移出，迁移前全量副本与路径映射留`archive/source_reorganization_20261019/`；旧冻结实验包不改。继续使用的`codec.py`与`opnn.py`在`code/NeuralODE_Latent/`保留。

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| SRC-001 | partial-result | 已定位 AR/PCA、Direct 和 v10 的实际入口与协议 | code/source-inspection：SOURCE_MAP.md 指向的源文件 | 未重新认证生成器物理精度、全部数据值或模型性能 |
| RUN-001 | partial-result | AR/PCA 现有 71 项测试通过 | code：../../runs/20260916T053453-server-tests-ad1f043c/run.json 及 stderr.log | 覆盖测试用例，不是正式模型性能 |
| RUN-002 | partial-result | Direct 现有 17 项测试通过 | code：../../runs/20260916T053532-direct-tests-4d38658f/run.json 及 stderr.log | 不是多病例正式预测 |
| DATA-001 | partial-result | 25 批结构预检及原生数据接口成功 | data/structural：../../runs/adaptation-validation/doctor.json；../../runs/20260916T053538-inspect-data-6ab13662/run.json | 未逐值核查全部轨迹、近重复或物理准确性 |
| RUN-003 | experimental | AR 与 Direct 各一次真实网格参数更新/保存成功 | code：../../runs/20260916T053617-smoke-ar-b42544af/；../../runs/20260916T053623-smoke-direct-ad4a3444/ | 小模型、单更新、无正式验证；不说明精度提升 |
| ADAPT-001 | partial-result | Agent 可连接项目并执行/记录实验 | code：初版工作台 17 测试、技能验证、源码差异见 ../../docs/ADAPTATION_REPORT.md 与 ../../runs/adaptation-validation/ | 初版只保留单次实验；自动多轮能力已由 ADAPT-002 恢复 |
| ADAPT-002 | partial-result | 心脏版自动队列可跨回合传递状态并管理实验 | code：43 项工作台回归通过，其中 26 项队列测试；实际 CLI 参数、研究包与预览通过，见 ../../runs/autonomy-validation/validation.json | 测试使用程序替身；CLI 未登录，真实模型回合未验证；不构成 AR/PCA 研究目标完成或精度提升 |

## AR/PCA 原有目标衔接（2026-09-16 13:44）

下列结论来自实际项目原有实验及本次复核，不属于 Agent 适配测试的新增模型成绩。项目路径均相对 `../../../`。

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-REF-001 | proof-draft | 原 6845 的 90 例晚期自由预测 RMSE 为 66.79545 mV / 405.64495 nM | prediction/supported：`results/ar/reference/metrics.json`，90 例及补充状态 completed；文件 SHA256 `8c4fdb42bdfc50113914a469d83ae045e1d3ac32420e202f396de5f751daed14`；本次从逐例 free_clamp1 窗口 RMSE 重新合并核对 | 仅该固定模型和已查看的测试集，不证明新改动有效；不把条件诊断分数当作预测成绩 |
| AR-DATA-001 | partial-result | 遮掉未来标签不改变一个真实病例的完整自由预测 | code/data/supported（限定该检查）：`results/ar/analysis/summary.json: ar_forecast_boundary_check`；冻结源码、6845 权重，batch_022/sample00，两个正式入口均逐值不变；已观测锚点扰动对照会改变预测，退出 0 | 不认证所有预处理、样本近重复或完整数据质量；prediction 改善未评估 |
| AR-RUN-001 | partial-result | 当前 7 组正式训练为 4 运行、3 等待，运行 PID 与调度状态相符 | code/runtime/supported：13:44 SSH 的 squeue 6907/6909、各 run.json/training_log.json、/proc；423/350/67/67 轮，上界 500 ms；`results/ar/full/suite.json` 保存配置与冻结来源 | 训练和 90 例正式评估尚未全部完成；新模型 prediction 为 not-assessed |
| PCA-DEPLOY-001 | partial-result | GRU/MLP 对照包可在服务器导入，配对参数仅差记忆模式与输出目录 | code/supported（部署检查）：`results/ar/analysis/summary.json: pca_memory_deployment`；包 SHA256 `e6ea5bfecc0325b7203d4aa1deac505750e6bd3106ef58af101ebfbb672265fe`，14 文件一致；Bash/入口/参数检查退出 0；服务器 PyTorch 2.11.0+cu130 | 尚未提交训练，服务器 GPU 前后向留到任务短验证；PCA 新对照 prediction 为 not-assessed |

本轮未新增数值收敛、患者个体化或统计不确定性证据；不重复计入既有测试次数。

## 2026-09-16：训练段增量范围

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-CAP-001 | partial-result | 全部 600 例的 0–500 ms 真实训练状态上，固定 6845 图扩散系数时所需 V/Ca 学习增量未超上限；每通道 6,535,950,000 点步 | code/data/supported（限定幅度范围）：项目 `results/ar/analysis/summary.json: ar_increment_capacity`，源文件/权重/输入指纹、600 个逐例统计与 execution；最大占比 87.18%/82.25%，V 下降阶段 47.72%；合成样例、12 例重叠和汇总恒等式核对通过 | 不证明网络已学会这些增量、不检查偏离真值轨迹后的饱和，不是自由预测成绩；不新增 PDE 收敛、个体化或不确定性证据 |

## 2026-09-16：许可观测历史的精确重复

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-DATA-002 | partial-result | 750 例的 0–500 ms V/Ca 历史均有不同精确指纹，集合内及跨集合无完全重复 | data/supported（限定精确历史）：项目 `results/ar/analysis/summary.json: ar_split_duplicates`；600 例复用同日训练扫描，150 例新读，首尾训练重检及正反指纹对照通过；38.45 秒，预算 180 秒，session 22531 退出 0，无未来字段读取 | 未检近重复、空间等价或统计独立性；已有初态审查单独引用；不证明预测改善或完整数据质量 |

## 2026-09-16：正式汇总的预测边界

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-COMP-001 | partial-result | compare 汇总只纳入权重记录的自由预测；条件诊断不进入改善统计，策略不匹配或缺预测时报错 | code/supported：项目 `results/ar/analysis/summary.json: ar_comparison_boundary_check`；4 个反例先失败，修改后 75 项测试通过；6 组真实短程自由统计逐值不变，90 例参考自比较差值零，2 类策略篡改被拒；内存编译和 diff 检查通过，集成退出 0 | 没有改变训练或模型精度；正式 7 组尚待完成；lint/typecheck 无配置且工具未装，不以软件检查代替预测验证 |

## 2026-09-16：物理与 ODE 候选的文献适配

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-LIT-001 | partial-result | 已区分简化恢复状态拟合、完整离子 FNO 与压力容积 LNODE 的任务边界；形成与当前输入协议匹配的候选验收条件 | literature/source-inspection：项目 `results/ar/analysis/summary.json: ar_physics_literature`、报告同名小节；3 篇原始来源链接、已核章节、已有 PDF 哈希及源码接口映射 | 不是新模型或效果验证；未证明 CRN 隐状态可识别，未穷尽全部文献；LNODE 仅核查原始摘要/索引方法段 |

## 2026-09-16：非均匀步长的训练段可行性

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-TIME-001 | partial-result | 12 个预定训练病例的 100–500 ms 中，快速上升只占 0.937% 点时刻，却在 2391/2412（99.13%）病例时刻涉及至少一个节点；当前数据仅有 2 ms 场标签 | data/source-inspection：项目 results/ar/analysis/summary.json: ar_adaptive_step_feasibility；后向差分 >5 mV/ms，另列 1/10 的说明性阈值，原始指纹/逐例计数/源码哈希/命令；计算 2.535 秒、预算 120 秒、退出 0；来源数据和代码未变 | 仅训练段小样本占用检查；不是自适应预测、未来尖峰探测或提速/精度结论；1 ms 标签和 Δt 联合推进尚未实现 |

## 2026-09-16：新基线完成与第五组启动

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-BASE-001 | proof-draft | 新基线完成 500 轮/10 万次更新，按 ≤500 ms 固定验证选中 best 480；49 项模型状态与历史 6845 逐值相同，90 例主评估复现晚期 RMSE 66.79546 mV / 405.64507 nM | code/prediction/supported（限定复现）：项目 results/ar/full/first/baseline 的 best/last/run/log/metrics；来源、选模和汇总见 results/ar/analysis/summary.json: ar_full_baseline_training；best SHA256 9f39d68870b01e34858f03128789c579c3dd625a6d0ce3b960b668b18fbde048；CPU 汇总退出 0，壁钟 7.87 秒、计算段 0.98 秒，仅取 free_clamp1 | 补充指标未齐，六组正式配对未完；微小重算差异及 1 个事件匹配差异不代表改善/退化；未新增物理收敛、个体化或不确定性证据 |
| AR-RUN-002 | partial-result | clamp 只增加 train_feedback_clamp；已启动五组的单因素差异与冻结源码匹配；clamp 前 8 轮/1600 更新日志除耗时外与基线一致 | code/runtime/supported：项目 results/ar/analysis/summary.json: ar_full_baseline_training.post_baseline_runtime_check；19:23 SSH 原始 run/log 哈希、活进程、Slurm；两端 suite SHA256 5009065ad8eeec7541bc36ae6e8d7928f7c8b560dd0f95e14ac5a3d791ccda71；工具 950d8f 退出 0 | 仅启动与单步前缀；未保留中间权重不能逐参数核对；不预判限幅收益，events/nogru 启动后另查 |

## 2026-09-16：工作台移动后的入口修复

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| PATH-001 | partial-result | 工作台移入项目后，旧配置会指向不存在的嵌套 PDE 目录；修正根路径与入口文档后，doctor 及五个任务计划解析通过 | code/path-supported：项目 results/ar/analysis/summary.json: workspace_relocation；先复现 make_plan 的 Missing task working directory，再检查新根路径、25 批 NPZ 结构、依赖与四个结果链接；11 个 AR/PCA Python 文件哈希不变，验证工具 38addc 退出 0、壁钟 1.84 秒 | 只验证路径与结构，未重跑训练或回归套件；不属于新预测成绩，未修改保护队列状态、模型或远程作业 |

## 2026-09-16：运行资源与基线图核查

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| AR-RUNTIME-001 | experimental | 四卡各一训练进程，未见 CPU 配额节流；12 秒采样中 mixed/noise/range/clamp 的内核 CPU 比例约 5.4%/43.8%/45.3%/68.3%，全局整理停顿增加 3929，节点 1 大块连续内存稀少 | runtime/limited-supported：项目 summary 的 ar_full_baseline_training.runtime_resource_sample；24.77 秒资源样本、12 秒内核补查、cgroup/NUMA/进程/GPU 原始数值及完整命令；工具均退出 0 | 全局计数包含其他任务，未取内核调用栈，短窗非整轮吞吐；CPU 绑定提案已因资源条件变化撤回，未执行，不是精度改善 |
| AR-PLOT-001 | partial-result | 新基线两张正式 PNG 已从服务器 plots 子目录取回，字节哈希一致，图例和时间范围可读 | artifact/supported：results/ar/full/first/baseline/plots/training.png 与 loss.png；summary 的 ar_full_baseline_training.plots；核对 best/log 哈希并查看两图，无重绘或新增验证文件 | 训练曲线不能替代未来自由预测；首轮只查询模型目录顶层，随后按真实绘图入口定位子目录 |
| AR-ODE-001 | partial-result | 现有独立 ODE 的监督/选模协议与 7 组 AR 不同；当前源码 9 项 CPU 测试通过 | code/limited-supported：项目 summary 的 ar_existing_neural_ode_protocol_review；实际脚本、既有 8 次更新记录、源码哈希及工具 5ac320；测试 1.985 秒、进程 5.692 秒，退出 0，无新增文件 | 合成读取边界检查非真实数据遮蔽；既有 smoke 非当前源码完整重跑；无 CRN 残差，尚无配对预测效果证据，本轮未提交/修改远程作业 |
| AR-BASE-002 | proof-draft | 新基线 500 轮/100000 更新及 90 例主、补充评估全完；全部 49 项模型状态张量与 6845 相同，晚期全场 66.795/405.645、波前病例均值 59.912/386.278，首次激活节点漏检 46.862%，下降事件 F1 0.1799 | prediction/benchmark-supported：results/ar/full/first/baseline/metrics.json（af1300…）、full/summary.json（7bb59f…）；summary 的 ar_full_baseline_training.complete_evaluation；收集 1fb897、比较 2f1bfd 均退出 0；控制器确认 6909_0 完成退出 0，本地/服务器 suite 哈希相同 | 这是原失效的复现；仅 1 个历史模型比较、0 个已完成单因素比较，六变体待完成。波前按病例平均，事件时间条件于匹配；sacct 未启用，旧训练作业已超出控制器保留期 |
| AR-FACTOR-001 | partial-result | mixed 五长度各 9880 次正式课程后更新并覆盖晚锚点；range 228 轮范围值全零、日志前缀与基线逐值相同，含 28 轮 64 步训练；两次 mixed 正范围值约 1e-16 | code/training-execution-supported：项目 ar_running_factor_activation，实际运行配置/冻结源码/日志哈希与完整计数；064e95、f1baf3 均退出 0 | 日志相同非中间权重逐值比较；范围值涉及采样损失、标量比非参数梯度比；clamp 尚全单步，七组最终预测仍待完成，不据此取消训练 |
| AR-RUNTIME-002 | experimental | 原节点 0 绑定方案因两节点大块内存条件变化撤回，未执行；四组训练耗时自行回落。真实训练样本分配短测关闭大页均值慢 22.24%，编码数组哈希一致；冻结续训不保存 RNG 状态 | runtime/limited-supported：项目 ar_runtime_slowdown_followup；10 秒进程/全局计数、冻结源码片段、NumPy 2.4.2 的 ABBA 四个 CPU 子进程共 12.83 秒，初始路径失败已记录，恢复后全部退出 0；原四个训练 PID 与 Slurm 均存活 | 无内核栈归因；一个样本及短窗口不代表高压时段或整轮吞吐。未改系统/训练设置、重启或提交作业；不是预测改善，旧 CPU 确认不再待执行 |
| AR-NUM-001 | partial-result | 原 v10 生成器在一个训练病例 0–2 ms 按原保存精度逐值重现双场；两次内步减半的相邻 RMS 差约减半。起点 RHS 单次 2 ms Euler 对真实目标已有 2.304 mV/5.432 nM RMS 差 | numerics/short-interval-supported：项目 ar_generator_replay；原函数体/初态/图/标签哈希，43,573 节点，0.02/0.01/0.005 ms 内步，4 CPU 线程，24.44 秒（不含前置导入），695d3d 退出 0 | 使用完整初态仅核验生成器，未给 AR 增加输入；一个短段不能支持全程收敛、全训练容差或预测精度。仅禁用缓存/改验证线程数，无模型或远程作业修改，无遗留验证文件 |
| AR-GRAD-001 | experimental | 12 个训练窗口中 10 个 V 上升/下降参数梯度余弦为负，中位 −0.8279；范数比中位 2.5084，8 个下降项与总梯度负相关 | gradient/local-supported：ar_parameter_phase；冻结 6845/原 AR 图、372–500 ms，原损失及梯度和核对；最大误差 2.81e-7、相对 L2 3.60e-7，71.79 秒/2.046 GiB，18f611 退出 0 | 固定权重、单时间窗；未模拟 AdamW、裁剪和权衰的实际参数步，未重新加权训练或证明精度改善 |
| AR-GRAPH-001 | partial-result | 既有本地图差异在服务器冻结 AR 上复核：7,405 条边/节点不同于原生成器，距离多重集相同；检查进程设 leafsize=10 后规范边数组匹配 | code/graph-supported：ar_graph_difference；本地 SciPy 1.16.3、服务器 1.17.1 实际数组/源码哈希；876ac8、28a690 退出 0 | 不是首次本地发现；正式图未改、未重训，未确定对晚期误差的贡献，不唯一认证全部历史生成设置 |

## 2026-09-17：无 PCA 的 Neural ODE 本地探索

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| NODE-GRAPH-001 | experimental | 原始 43,573 节点 V/Ca/h 联合积分已实现；200 更新短训练出现激活消失，低 RMSE 不代表有效传播 | code/supported、prediction/failed（有限验证病例）：项目 results/neural_ode/session_20260916/round_2_graph；训练退出 0、458.244 秒，四例激活漏检约 99.99%；独立展示的 batch_020/sample00 有 51,677 真激活/7 预测事件、F1=0.0001935；完整窗口步长差 0.0000984 mV/0.0001252 nM，遮蔽/重载通过，PNG 已查看 | 尚未区分训练不足与结构不足；不是完整测试或 PCA 单因素实验；训练/选模允许未来，与严格 AR 不同 |
| NODE-GRAPH-002 | experimental | AR 网络可初始化一个联合连续场/记忆 ODE；初始化四例预测与 AR 基本持平；长窗口梯度可在本机显存内计算 | code/numerics/limited-supported：graph_memory_initial 的 verification.json/paired_val4，1/0.5 ms 差 0.01358 mV/0.08219 nM；99 项回归通过；graph_memory_backward_recompute 全 500 ms 反向检查 56.976 秒/4.69 GiB，梯度有限、权重逐值不变。前一次高显存检查主动停止，记录 resource_stop.json | 不能继承 AR 为精度保证；下降 F1 从 0.20198 到 0.18611；未完成新微调的预测验证，也未证患者能力或不确定性 |
| NODE-GRAPH-003 | proof-draft | 40更新微调降低全部90例的双场全窗口RMSE，但激活F1退化，联合验收失败 | prediction/partial-improvement：项目 results/neural_ode/session_20260916/report.md 与 round_3_graph_memory/test_all90；全窗25.7726 mV/170.7978 nM，对照53.6497/293.2225；激活F1 .479255/.571008，下降F1 .185571/.179894但下降精度更差。训练984.423秒、评估1119.503秒均退出0；权重选择先于测试且哈希一致；配对工具74c5c6退出0，numeric_gate_passed=false；代表性PNG已查看 | 新模型可用未来训练标签，与旧严格AR不同；非架构单因素归因、非全新盲测、单次短训练；未完成正常传播与患者/不确定性验证 |
| NODE-LOSS-001 | partial-result | 备用BCE激活损失可给自信但错误的状态更强电压梯度，旧恢复默认保持平方误差 | code/algebraic-supported：Live 101项测试（0fc427）、8文件AST/diff（54bfbc）、round4授权上限拒绝检查（57ef4f）；两个验证病例三帧的代数诊断见 activation_gradient_diagnostic.json；未计算参数梯度或优化更新 | 不是性能改善或失败的唯一原因；第四轮未获授权、未启动；不改第三轮冻结代码/权重/结果 |
| NODE-EVENT-001 | partial-result | 2026-09-18 原90例指标显示77例双场误差降低但激活F1下降，漏检与误报同时增多；无时间容差的节点覆盖也下降 | prediction/post-hoc-diagnostic：项目 round_3_graph_memory/event_diagnostic/diagnostic.json 与 PNG；CPU脚本4dbd3a，0.789秒退出0；1bee74核对原指标哈希、配对真值、计数恒等式与AST；激活误报235826→529809，首次激活节点召回.53138→.45860；主报告中文编码另已修复 | 没有执行模型/训练或改变第四轮提案；汇总不能唯一分开位置、时序与重复事件错配，条件时间MAE不能证明整体时序变好；非新盲测，仍未达成联合验收 |
| TRANSFER-001 | partial-result | 代码与图表包已生成，排除数据/权重/基底及逐节点 TXT；按来源收齐 2,798 张 PNG，补 56 张日志或已有预测图 | artifact/supported：`exports/pde心脏代码3.zip`，1,099,858,656 bytes，7,346 条目逐项读取并匹配 SHA-256；ZIP SHA-256 `cfcfd384496ae3b6168b880a01bc699c252a019cf7cd1cd2858cec71ce5a26c5`；5,597 个图表页面链接检查通过；记录在 `runs/transfer-package-20260917/verification.json` | 仅迁移包完整性；原模型代码未由本次整理修改。2,570 张属于 DIMON 参考资料；短实验/缺图及持续更新日志的快照范围在包内注明。未训练、推理或操作远程作业，不是预测改善证据 |

| NODE-QUEUE-001 | partial-result | 已注册 neural-ode 独立任务，只读预览与队列回归通过（2026-10-09 重建，原文编码损坏） | workflow/supported：problems/cardiac-research/items/neural-ode/task.json；runs/neural-ode-task-20260929-111403/checks.json；list/plan/packet/dry-run/queue-tests.log 5 项退出码 0；26 项队列测试通过；ar-pca 任务与历史预算 SHA-256 未变 | 任务注册不等于研究启动或目标完成；未创建任务运行目录、未调用模型；详见同目录 final-verification.json |

## 2026-09-30：空间记忆副本与服务器验证

| ID | 等级 | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|---|
| NODE-GLOBAL-001 | partial-result | 独立实现132区域H、单/多尺度和软/硬反馈约束，原五文件哈希未变 | code/numerics：254 Slurm7051真实网格与全500ms检查，7052最终36测试；项目results/neural_ode_global_memory/session_20260930/{report.md,source_integrity.json,real_check.json,full_window_check/verification.json,tests_7052.log} | 新训练0更新，尚无效果改善；硬约束只是同驱动H收缩，非全系统保证；初始零输出分支的全窗验证不能替代训练后检查 |
| NODE-GLOBAL-002 | experimental | 形态评价器已在旧基线两验证例产出指标及PNG | evaluation/implementation：Slurm7049，initial_validation/metrics.json；V16.671mV/Ca109.819nM、Dice.6523、激活F1.6344；7052另测静息窗口缺失指标处理 | 小样本评价器预检，非新模型结果，不能归因缺少H；未选候选/用测试选模 |
| NODE-GLOBAL-QUEUE-001 | partial-result | 新工作台任务和CLI已部署，真实模型循环尚未运行 | workflow/partial：Slurm7050的agent_check.log显示errors=[]但未登录；新预算null由测试确保拒绝训练 | 等待新增时长/次数和登录方式，不复制凭据、不消耗旧预算、不称自主研究已运行 |
| NODE-GLOBAL-AUDIT-001 | partial-result | 离线复核发现并修正记忆约束零点梯度边界、续训计数、异常状态；统一课程和计划/权重校验 | source-reviewed、artifact-supported：2026-10-02 session_20261002/static_review.json；原5源码/3预训练初始化哈希一致，新副本44测试定义，未执行项目代码/SSH | 不是运行验证；新增检查与训练均待254 Slurm，旧36通过不可外推；模型效果与闭环稳定性未知 |
| NODE-GLOBAL-RUN-001 | partial-result | 2026-10-08 Slurm7162通过当前44项回归并开始六组训练，首组已有更新及checkpoint | code/workflow：session_20261002/resume_20261008/{tests_7162.log,job_7162_startup.txt,suite.json,budget.json,train_baseline.log,frozen_7162/sha256.json}；4.643秒全部通过，冻结11源码哈希匹配审查 | 启动快照；需实时查询7162和服务器账，非六组完成；H预测收益/单例推理延迟未验证；sacct历史统计不可用 |
| NODE-PURE-001 | partial-result | 独立直接导数ODE从零训练入口可用，无AR初始化或未来一步算子；历史GRU保留 | code/limited-numerics：CPU Slurm7164退出0，10测试通过；项目results/neural_ode_pure/session_20261008/{tests_7164.log,job_7164.txt,real_check_7164/real_check.json,frozen_7164/}；真实43,573节点/132区域、251帧历史与2ms预测重载通过，89,280参数 | 实现及初始化短验证，真实数据0更新；未新增GPU训练或修改7162；无完整预测效果/加速结论；检查后main仅改一处说明文字 |
| NODE-GLOBAL-SCREEN-001 | experimental | 7162六组均80更新/12验证；hard-H候选V17.57mV/Ca134.71nM/Dice.567优于所选baseline的22.97/148.10/.495；scratch短训未形成有效激活传播 | validation-screen：session_20261002/{suite.json,budget.json,screening_review.json,screen/}；12子进程exit0，6395.09秒，6/6名额使用 | 单种子、非独立测试；best步数25/25/80及scratch65不同；hard时序误差与误报上升；不能把旧scratch当新Pure结果或评价耗时当推理延迟 |

### NODE-PURE-CONFIG-500 — 2026-10-08
- 等级：partial-result
- 用户选择：500 epoch×200随机窗口更新，其余Pure参数不变；这是更新量对齐，未改变训练/验证监督协议。
- 修改：Pure main默认参数、独立Slurm训练脚本和README；正式GPU未提交，旧筛选额度未重置。
- code supported：Slurm7173 COMPLETED/exit0，Bash语法、10回归及真实网格2ms检查通过；CPU作业34秒。
- prediction/numerics/personalization/uncertainty：未新增证据，不能称完成500轮或证明预测有效。
- 证据：项目results/neural_ode_pure/session_20261008/config_500_review.json、job_7173.txt、tests_7173.log、real_check_7173/real_check.json及frozen_7173。

### NODE-FULL500-SUBMIT — 2026-10-08
- 等级：partial-result
- 用户新授权全部九组各500×200并量化推理，源模型不改；新session冻结源码、初始化哈希和单卡串行预算。
- code supported：Slurm7174 COMPLETED/exit0，44+10+9=63测试；7178报告入口exit0。
- 执行：7175 GPU检查/测速排队Resources；7176_0–8正式训练数组等待7175成功；7177最终汇总等待7176。未宣称训练开始/完成或实测速度。
- 方法：同43573节点、251帧历史、250帧预测、float32、batch1，3固定例×5重复/2预热，CUDA同步，分编码/积分/实际rollout计时并验证预测一致；显存峰值含三例常驻输入。训练后每组best自动重新计时及60例验证。
- evidence：results/neural_ode_full500/session_20261008/{manifest.json,submission.json,checks/,submission_*.txt}；新benchmark和runner静态交叉审查发现preview已有目录冲突，提交前已修复并冻结。
- prediction/numerics/personalization/uncertainty：尚无新增结论。旧80步screen不可作为正式500轮结果。

### NODE-BOUNDARY-001 — 2026-10-10
- 等级：partial-result

- 用户要求：内部状态＋各条边界动态→带位置信息的非线性特征→区域H，边界信息融合，不新增独立E。独立复制Pure，保留原框架与正式实验。
- 实现：节点72→16→24先编码再区域汇总；跨区域细边143→16→24，按有向区域对汇总后写入接收区域。观测率是后向差分/2ms，预测率由当前RHS计算，未读未来真值。
- code supported：CPU Slurm7204基线10测试通过；7207完整43573节点/132区域/251观测/250未来帧有限性、精确锚点与重载、记忆梯度检查通过；7208最终23测试通过，退出0。新增空界面验证器修正及因果输入回归仅影响检查入口，7207/7208的opnn.py SHA相同。
- 数量：19335跨区域细边、675有向界面、90568参数，H仍132×24。最后仍压缩各界面，不保证完整逐界面历史。硬约束仅相同固定drive下H方程收缩；新drive经du/dt依赖H，不能由固定u/h或原证明宣称闭环稳定。
- evidence：项目results/neural_ode_boundary_memory/session_20261009_2047/，real_check_7207/real_check.json、tests_7208.log、frozen_7207/、frozen_7208/及source_*.sha256；原Pure哈希记录original_pure_sha256.json。
- prediction/numerics/personalization/uncertainty：新精度、训练后GPU时延、数值收敛、患者能力均未评估。真实数据0优化更新，梯度检查目标是2ms后的记忆平方范数；初始化H读出为零，场损失第一轮写入梯度为零。未追加第十组500×200训练或改动现有作业。

### NODE-PURE-INTERIM-001 — 2026-10-14
- 等级：experimental；来源internal；进展experimental-signal。
- 用户授权：当天完整预测与误差对比。独立冻结Pure无H从零模型best epoch246（49400更新），原训练冻结时完成277轮；不追加训练或修改原九组。SHA256 5b2e93a0d6536f8d2e3f04226a73c9af3d5494cbb28c734984650fde521bc687。
- prediction supported（有限范围）：90例batch022–024，输入0–500ms，完整502–1000ms/250帧/43573节点。病例平均V5.612517mV/Ca37.386250nM，激活事件F1 .889198、下降F1 .939110，首次激活漏检5.343321%、误激活1.477184%、匹配MAE5.234023ms；晚期V6.791614mV/Ca51.143119nM。相对旧ODE第4轮平均误差降低67.48%/68.36%，V90/90、Ca89/90改善；相对AR两场90/90改善。
- code/data limited-supported：7275 GPU评估/测速完成exit0（21分25秒），7276 CPU汇总exit0（2秒）；冻结source与原manifest一致，checkpoint复制前后哈希一致。比较验证90唯一病例、250帧时间、阈值/容差、真值事件计数、persistence误差一致；只取AR部署free_clamp1，ODE不注入未来真值。不是全量原始数据哈希审计。
- runtime supported（当前权重/该设备）：RTX4090、float32、batch1、3例各2预热5重复；完整rollout中位3.518086秒，P90 3.520400秒；仅网络编码/积分及输出，不含数据读取、传输、指标、绘图。完整90例评估子进程约1122.85秒。
- 10/14绘图补充：Slurm7277 exit0/120秒，SCI重绘27PNG。重新导出固定batch022/sample00、01并与原test90逐帧指标核对；最大差异V2.45e-7mV/Ca1.40e-6nM以内。NPZ场图、三点与误差直方图统一固定分母，初始500ms不评分；90例比较只复用已核对的指标。56个下载产物哈希一致，抽查7张PNG显示正常。证据plots_sci_20261014/{manifest.json,artifact_sha256.txt,slurm_job_7277_final.txt,README.md}；这是绘图与两例一致性检查，不是独立90例复现，等级不变。
- 绘图口径修正：7277空间标题使用整窗NRMSE，用户指出重复4.08%后，7278修正单帧标注；随后7279合图exit0/50秒，最新plots_sci_combined_20261014/。六组单帧值与保存指标一致，两例三时刻共享物理色标与原节点绝对误差上限；sample00 Ca1.303658/4.447405/6.856186%，sample01 Ca.537900/.540169/1.115443%。sample01 1000ms真实V[−80.375,−77.688]mV，低值均匀颜色有原始范围支持。27下载文件哈希核对；查看三张合图。用户要求尽量不写test，移除本轮新建的当前test源码，冻结旧运行证据保留；最新核查只用真实产物。原预测/90例指标及证据等级不变。
- 参考PDF样式修正：7284程序正常完成13.567秒，两个绘图子进程exit0；33下载文件及提供的calcium.pdf原文件哈希核对一致，实际PDF渲染已查看。场viridis/绝对误差magma，3行类型×3列时间、原节点scatter、12×9英寸紧凑图，已覆盖原plots_sci_20261014/。共享显示范围V[−83.717552,22.25]mV/Ca[114.820046,1161.575317]nM，绝对误差上限60mV/696nM；单帧/全窗评分仍用原固定分母，六组值及250帧与原指标一致。最终Slurm控制器记录被清理、记账服务禁用，只保留分配记录/完成日志与查询输出；不声称独立复现或升级证据。
- 10/15仅整理交付：原plots_sci_20261014/保留11PNG、3CSV和纯量化summary.json；其余35项材料移动到archive/neural_ode_full500/evaluation_20261014/plots_sci_20261014/，含原NPZ/source/manifest/日志。保留与移动的全部50文件本机/254哈希一致，归档映射及清单可追溯；历史运行路径记录不改写，后续重用入口改传归档目录。无新计算、科学结果或等级变化。
- 10/19追加失效病例图：研究者要求另选一例可视化并量化时间。选batch023/sample13，它是本权重90例中全窗V RMSE最大者（13.784737mV/142.326962nM，激活事件F1 .570053，首次激活漏检1020/25734节点、误激活6725节点、匹配时间MAE31.873918ms）。Slurm7368（CPU分区+1张4090，4CPU/16G）exit0，程序14.551秒：rollout导出子进程7.7秒（含启动、数据映射、权重加载与NPZ写出）、绘图子进程5.1秒；250帧误差与test90/metrics.json逐帧一致，最大差1.77e-7mV/1.09e-6nM。单帧NRMSE V2.475792/9.265811/16.872185%、Ca1.646260/11.130819/22.931832%（600/800/1000ms）；逐帧V NRMSE在732ms越过5%、816ms越过10%，Ca在738ms越过5%、784ms越过10%、946ms越过20%，均在1000ms达最大。预测于800ms后在右下区域生成真值没有的激活波，三点A/B约950ms出现虚假上冲。该例显示范围单独计算（V[−82.843414,19.875]mV、Ca[126.691564,1111.984253]nM，误差上限84mV/792nM），与两例b022共享色标不同。纯推理时延沿用runtime条目（同权重同设备中位3.518086秒/例，RK4固定2000次RHS与病例内容无关），本次未另做计时作业。源码改动：code/NeuralODE_Snapshot/plot_snapshot_sci.py新增--cases（默认仍为原两例），slurm/snapshot_plot_sci.sbatch透传额外参数；运行区archive/neural_ode_full500/evaluation_20261014/plots_sci_20261019_b023s13/（22文件本机/254哈希一致），交付code/NeuralODE/results/ode_pure/eval/plots/b023_s13/与254的plots_sci_20261014/batch_023_sample13/，snapshot_errors.csv两端各追加3行。等级不变，单例图不提升证据。
- 10/19数据集静息核查与真值时间线：对dataset/batch_022–024.npz只读memmap（Slurm7374扫描90例、7376打印b022_s01原值、7380画b023_s27真值；源码与输出在archive/dataset_checks/{quiescence_scan_20261019,truth_timeline_20261019}/，本机/254哈希一致）。b022_s01最后上冲624ms，1000–2000ms共21,830,073个V值无精确0，V[−80.6875,−77.6875]mV、Ca[119.15,236.51]nM，相邻帧最大变化0.0625mV；生成器二维循环无刺激，湮灭后无再激发。90例按最后上冲：<1000ms 39例、1084–1296ms 8例、≥1736ms 43例（其中2000ms帧仍有激活节点且最后上冲=2000ms者19例）。b023_s13最后上冲2000ms，属持续折返组，先前“半路湮灭”说法已更正。b023_s27（19例中全窗V RMSE中位，90例第58位，7.036mV/53.05nM）真值：上冲66723/53006/101617次（0–500/502–1000/1002–2000ms），激活节点500ms 23394峰、1100ms 667谷、1600ms 18242、2000ms 2128，三点各激活4次。交付results/waves/v10/b023_s27_*；预测图作业7379按研究者改口在PENDING取消。只读数据集事实，不改模型、指标或等级。
- 10/23追加测试例正式图：研究者明确“先允许这次”本机运行（254不可连接；无远程作业提交/修改），按文件顺序选下一未绘病例batch022/sample02，不根据测试成绩筛图。同epoch246权重SHA256 5b2e93a0…521bc687，冻结main/opnn/utils哈希与原snapshot一致；RTX5070 Laptop、Torch2.10.0+cu128、原RK4/1ms、FP32 highest，观测0–500ms，自由预测502–1000ms。250帧空间RMSE与原test90最大差3.16e-7mV/1.29e-6nM；单帧NRMSE V2.952268/3.572279/1.507262%、Ca1.508612/1.192925/1.554270%（600/800/1000ms），整窗2.864710%/1.229194%，均为RMSE除以固定150mV/1200nM，不是相对真值范数。沿用b022_s00的三行三列viridis/magma、三点曲线与误差分布；本例显示色标单独取范围，不与旧病例直接比颜色。交付NeuralODE/results/ode_pure/eval/plots/b022_s02/四PNG、traces.csv、量化metadata.json，根snapshot_errors.csv保留旧9行并追加3行；六文件发布哈希一致，电压/钙/曲线已目视检查。源码、预测、manifest、首轮打印中文路径失败日志及UTF8后复用预测成功记录在archive/visualizetions_20261023/session_001/，未改变活跃模型源码/数据/权重。此为单例可视化与原指标一致性检查，experimental等级不变，非独立90例复现/新训练或速度结论。
- evidence：results/neural_ode_full500/evaluation_20261014/{evaluation_plan.json,snapshot.json,checkpoint/best.pt,test90/metrics.json,inference/inference_benchmark.json,comparison/summary.json,comparison/report.md,comparison/per_case.csv,slurm_job_7275_final.txt,slurm_job_7276_final.txt,artifact_sha256.txt}；PNG已查看；下载5个关键哈希与远端一致。
- 限制：单种子中途权重，不是500轮最终结果；AR监督/选模≤500ms，ODE监督可至1000ms且用4例未来窗选模，初始化/累计预算/clamp不同。旧第3/4轮为AR初始化后短微调，复用历史90例原始指标，未于本次重跑。测试集已开发暴露；未新增独立复现、dt收敛、患者个体化或不确定性证据；不宣称P0达标或架构因果。
- 10/23同例原始数据核查：研究者质疑b022_s02波形近似不动，沿用本次同例本地出图授权作必要追查；直接只读NeuralODE/data/750sample/batch_v10/data/batch_022.npz、sample02，原shape[30,1001,43573]/float16。全部251个500–1000ms导出真值帧与原值经固定Scaler往返逐值一致，坐标亦逐值相同；往返引入的最大物理差7.63e-6mV/5.82e-5nM。0–2000ms原始真值最后上冲778ms（前帧≤−20、后帧>−20），最后V>−20节点存在于812ms；600/800/1000ms该节点数18785/152/0，1000ms V[−80,−77.4375]mV，1002–2000ms新上冲0，2000ms V[−80.6875,−80.4375]mV。说明此例活动终止，预测窗后段主要为复极和Ca回落，不支持持续旋转波展示；终止的具体生成机制未在本次归因。复用已冻结plot_truth_timeline.py生成每100ms原始真值场和三点/活动曲线，全部与模型预测分开，PNG/CSV/纯量化JSON交付NeuralODE/results/ode_pure/eval/plots/b022_s02/raw_truth/。直接证据、冻结源码、逐值核对、日志archive/dataset_checks/truth_b022s02_20261023/session_001/；experimental，单例数据事实与绘图一致性，非独立全数据认证或新模型精度结论。

### NODE-PURE-INTERIM-001 — 2026-10-26 逐帧展示补充
- 等级沿用experimental；同一epoch246/49400更新冻结模型，90例batch022–024、43573节点/例、0–500ms观测与502–1000ms评分；训练/选模可使用后半段标签。本次只汇总既有全测试报告，无新增推理。
- 指标：每帧每例全节点空间RMSE后病例等权均值；NRMSE为100×RMSE/150mV或1200nM，阴影为病例间25%–75%分位，不是置信区间。600/800/1000ms V/Ca均值分别2.435807/1.209917%、3.998671/3.410920%、4.815508/4.837015%；这些是单帧均值，不能替代原全窗RMSE。
- 证据：NeuralODE/results/ode_pure/eval/test90/time_errors/{nrmse_over_time.png,rmse_over_time.png,time_errors.csv,per_case_time_errors.csv,summary.json}；原metrics.json SHA256 5c86c9c822d258f51f0fd65356310242bc8ddfa84341b016a82b809a1b977242。CPU Slurm7610完成0:0，冻结archive/test90_time_errors_20261026/session_002/{source/,reference/,manifest.json,job_7610_final.txt}。90病例完整性、整窗重构、历史均值曲线、CSV/PNG与文件哈希一致；只读复核不提升为agent-verified。原中途权重/测试暴露/二维合成限制不变。

