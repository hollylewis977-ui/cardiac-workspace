# 验证台账

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| SRC-001 | 已定位 AR/PCA、Direct 和 v10 的实际入口与协议 | code/source-inspection：SOURCE_MAP.md 指向的源文件 | 未重新认证生成器物理精度、全部数据值或模型性能 |
| RUN-001 | AR/PCA 现有 71 项测试通过 | code：../../runs/20260916T053453-server-tests-ad1f043c/run.json 及 stderr.log | 覆盖测试用例，不是正式模型性能 |
| RUN-002 | Direct 现有 17 项测试通过 | code：../../runs/20260916T053532-direct-tests-4d38658f/run.json 及 stderr.log | 不是多病例正式预测 |
| DATA-001 | 25 批结构预检及原生数据接口成功 | data/structural：../../runs/adaptation-validation/doctor.json；../../runs/20260916T053538-inspect-data-6ab13662/run.json | 未逐值核查全部轨迹、近重复或物理准确性 |
| RUN-003 | AR 与 Direct 各一次真实网格参数更新/保存成功 | code：../../runs/20260916T053617-smoke-ar-b42544af/；../../runs/20260916T053623-smoke-direct-ad4a3444/ | 小模型、单更新、无正式验证；不说明精度提升 |
| ADAPT-001 | Agent 可连接项目并执行/记录实验 | code：初版工作台 17 测试、技能验证、源码差异见 ../../ADAPTATION_REPORT.md 与 ../../runs/adaptation-validation/ | 初版只保留单次实验；自动多轮能力已由 ADAPT-002 恢复 |
| ADAPT-002 | 心脏版自动队列可跨回合传递状态并管理实验 | code：43 项工作台回归通过，其中 26 项队列测试；实际 CLI 参数、研究包与预览通过，见 ../../runs/autonomy-validation/validation.json | 测试使用程序替身；CLI 未登录，真实模型回合未验证；不构成 AR/PCA 研究目标完成或精度提升 |

## AR/PCA 原有目标衔接（2026-09-16 13:44）

下列结论来自实际项目原有实验及本次复核，不属于 Agent 适配测试的新增模型成绩。项目路径均相对 `../../../`。

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-REF-001 | 原 6845 的 90 例晚期自由预测 RMSE 为 66.79545 mV / 405.64495 nM | prediction/supported：`results/ar/reference/metrics.json`，90 例及补充状态 completed；文件 SHA256 `8c4fdb42bdfc50113914a469d83ae045e1d3ac32420e202f396de5f751daed14`；本次从逐例 free_clamp1 窗口 RMSE 重新合并核对 | 仅该固定模型和已查看的测试集，不证明新改动有效；不把条件诊断分数当作预测成绩 |
| AR-DATA-001 | 遮掉未来标签不改变一个真实病例的完整自由预测 | code/data/supported（限定该检查）：`results/ar/analysis/summary.json: ar_forecast_boundary_check`；冻结源码、6845 权重，batch_022/sample00，两个正式入口均逐值不变；已观测锚点扰动对照会改变预测，退出 0 | 不认证所有预处理、样本近重复或完整数据质量；prediction 改善未评估 |
| AR-RUN-001 | 当前 7 组正式训练为 4 运行、3 等待，运行 PID 与调度状态相符 | code/runtime/supported：13:44 SSH 的 squeue 6907/6909、各 run.json/training_log.json、/proc；423/350/67/67 轮，上界 500 ms；`results/ar/full/suite.json` 保存配置与冻结来源 | 训练和 90 例正式评估尚未全部完成；新模型 prediction 为 not-assessed |
| PCA-DEPLOY-001 | GRU/MLP 对照包可在服务器导入，配对参数仅差记忆模式与输出目录 | code/supported（部署检查）：`results/ar/analysis/summary.json: pca_memory_deployment`；包 SHA256 `e6ea5bfecc0325b7203d4aa1deac505750e6bd3106ef58af101ebfbb672265fe`，14 文件一致；Bash/入口/参数检查退出 0；服务器 PyTorch 2.11.0+cu130 | 尚未提交训练，服务器 GPU 前后向留到任务短验证；PCA 新对照 prediction 为 not-assessed |

本轮未新增数值收敛、患者个体化或统计不确定性证据；不重复计入既有测试次数。

## 2026-09-16：训练段增量范围

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-CAP-001 | 全部 600 例的 0–500 ms 真实训练状态上，固定 6845 图扩散系数时所需 V/Ca 学习增量未超上限；每通道 6,535,950,000 点步 | code/data/supported（限定幅度范围）：项目 `results/ar/analysis/summary.json: ar_increment_capacity`，源文件/权重/输入指纹、600 个逐例统计与 execution；最大占比 87.18%/82.25%，V 下降阶段 47.72%；合成样例、12 例重叠和汇总恒等式核对通过 | 不证明网络已学会这些增量、不检查偏离真值轨迹后的饱和，不是自由预测成绩；不新增 PDE 收敛、个体化或不确定性证据 |

## 2026-09-16：许可观测历史的精确重复

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-DATA-002 | 750 例的 0–500 ms V/Ca 历史均有不同精确指纹，集合内及跨集合无完全重复 | data/supported（限定精确历史）：项目 `results/ar/analysis/summary.json: ar_split_duplicates`；600 例复用同日训练扫描，150 例新读，首尾训练重检及正反指纹对照通过；38.45 秒，预算 180 秒，session 22531 退出 0，无未来字段读取 | 未检近重复、空间等价或统计独立性；已有初态审查单独引用；不证明预测改善或完整数据质量 |

## 2026-09-16：正式汇总的预测边界

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-COMP-001 | compare 汇总只纳入权重记录的自由预测；条件诊断不进入改善统计，策略不匹配或缺预测时报错 | code/supported：项目 `results/ar/analysis/summary.json: ar_comparison_boundary_check`；4 个反例先失败，修改后 75 项测试通过；6 组真实短程自由统计逐值不变，90 例参考自比较差值零，2 类策略篡改被拒；内存编译和 diff 检查通过，集成退出 0 | 没有改变训练或模型精度；正式 7 组尚待完成；lint/typecheck 无配置且工具未装，不以软件检查代替预测验证 |

## 2026-09-16：物理与 ODE 候选的文献适配

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-LIT-001 | 已区分简化恢复状态拟合、完整离子 FNO 与压力容积 LNODE 的任务边界；形成与当前输入协议匹配的候选验收条件 | literature/source-inspection：项目 `results/ar/analysis/summary.json: ar_physics_literature`、报告同名小节；3 篇原始来源链接、已核章节、已有 PDF 哈希及源码接口映射 | 不是新模型或效果验证；未证明 CRN 隐状态可识别，未穷尽全部文献；LNODE 仅核查原始摘要/索引方法段 |

## 2026-09-16：非均匀步长的训练段可行性

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-TIME-001 | 12 个预定训练病例的 100–500 ms 中，快速上升只占 0.937% 点时刻，却在 2391/2412（99.13%）病例时刻涉及至少一个节点；当前数据仅有 2 ms 场标签 | data/source-inspection：项目 results/ar/analysis/summary.json: ar_adaptive_step_feasibility；后向差分 >5 mV/ms，另列 1/10 的说明性阈值，原始指纹/逐例计数/源码哈希/命令；计算 2.535 秒、预算 120 秒、退出 0；来源数据和代码未变 | 仅训练段小样本占用检查；不是自适应预测、未来尖峰探测或提速/精度结论；1 ms 标签和 Δt 联合推进尚未实现 |

## 2026-09-16：新基线完成与第五组启动

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-BASE-001 | 新基线完成 500 轮/10 万次更新，按 ≤500 ms 固定验证选中 best 480；49 项模型状态与历史 6845 逐值相同，90 例主评估复现晚期 RMSE 66.79546 mV / 405.64507 nM | code/prediction/supported（限定复现）：项目 results/ar/full/first/baseline 的 best/last/run/log/metrics；来源、选模和汇总见 results/ar/analysis/summary.json: ar_full_baseline_training；best SHA256 9f39d68870b01e34858f03128789c579c3dd625a6d0ce3b960b668b18fbde048；CPU 汇总退出 0，壁钟 7.87 秒、计算段 0.98 秒，仅取 free_clamp1 | 补充指标未齐，六组正式配对未完；微小重算差异及 1 个事件匹配差异不代表改善/退化；未新增物理收敛、个体化或不确定性证据 |
| AR-RUN-002 | clamp 只增加 train_feedback_clamp；已启动五组的单因素差异与冻结源码匹配；clamp 前 8 轮/1600 更新日志除耗时外与基线一致 | code/runtime/supported：项目 results/ar/analysis/summary.json: ar_full_baseline_training.post_baseline_runtime_check；19:23 SSH 原始 run/log 哈希、活进程、Slurm；两端 suite SHA256 5009065ad8eeec7541bc36ae6e8d7928f7c8b560dd0f95e14ac5a3d791ccda71；工具 950d8f 退出 0 | 仅启动与单步前缀；未保留中间权重不能逐参数核对；不预判限幅收益，events/nogru 启动后另查 |

## 2026-09-16：工作台移动后的入口修复

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| PATH-001 | 工作台移入项目后，旧配置会指向不存在的嵌套 PDE 目录；修正根路径与入口文档后，doctor 及五个任务计划解析通过 | code/path-supported：项目 results/ar/analysis/summary.json: workspace_relocation；先复现 make_plan 的 Missing task working directory，再检查新根路径、25 批 NPZ 结构、依赖与四个结果链接；11 个 AR/PCA Python 文件哈希不变，验证工具 38addc 退出 0、壁钟 1.84 秒 | 只验证路径与结构，未重跑训练或回归套件；不属于新预测成绩，未修改保护队列状态、模型或远程作业 |

## 2026-09-16：运行资源与基线图核查

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| AR-RUNTIME-001 | 四卡各一训练进程，未见 CPU 配额节流；12 秒采样中 mixed/noise/range/clamp 的内核 CPU 比例约 5.4%/43.8%/45.3%/68.3%，全局整理停顿增加 3929，节点 1 大块连续内存稀少 | runtime/limited-supported：项目 summary 的 ar_full_baseline_training.runtime_resource_sample；24.77 秒资源样本、12 秒内核补查、cgroup/NUMA/进程/GPU 原始数值及完整命令；工具均退出 0 | 全局计数包含其他任务，未取内核调用栈，短窗非整轮吞吐；CPU 绑定提案已因资源条件变化撤回，未执行，不是精度改善 |
| AR-PLOT-001 | 新基线两张正式 PNG 已从服务器 plots 子目录取回，字节哈希一致，图例和时间范围可读 | artifact/supported：results/ar/full/first/baseline/plots/training.png 与 loss.png；summary 的 ar_full_baseline_training.plots；核对 best/log 哈希并查看两图，无重绘或新增验证文件 | 训练曲线不能替代未来自由预测；首轮只查询模型目录顶层，随后按真实绘图入口定位子目录 |
| AR-ODE-001 | 现有独立 ODE 的监督/选模协议与 7 组 AR 不同；当前源码 9 项 CPU 测试通过 | code/limited-supported：项目 summary 的 ar_existing_neural_ode_protocol_review；实际脚本、既有 8 次更新记录、源码哈希及工具 5ac320；测试 1.985 秒、进程 5.692 秒，退出 0，无新增文件 | 合成读取边界检查非真实数据遮蔽；既有 smoke 非当前源码完整重跑；无 CRN 残差，尚无配对预测效果证据，本轮未提交/修改远程作业 |
| AR-BASE-002 | 新基线 500 轮/100000 更新及 90 例主、补充评估全完；全部 49 项模型状态张量与 6845 相同，晚期全场 66.795/405.645、波前病例均值 59.912/386.278，首次激活节点漏检 46.862%，下降事件 F1 0.1799 | prediction/benchmark-supported：results/ar/full/first/baseline/metrics.json（af1300…）、full/summary.json（7bb59f…）；summary 的 ar_full_baseline_training.complete_evaluation；收集 1fb897、比较 2f1bfd 均退出 0；控制器确认 6909_0 完成退出 0，本地/服务器 suite 哈希相同 | 这是原失效的复现；仅 1 个历史模型比较、0 个已完成单因素比较，六变体待完成。波前按病例平均，事件时间条件于匹配；sacct 未启用，旧训练作业已超出控制器保留期 |
| AR-FACTOR-001 | mixed 五长度各 9880 次正式课程后更新并覆盖晚锚点；range 228 轮范围值全零、日志前缀与基线逐值相同，含 28 轮 64 步训练；两次 mixed 正范围值约 1e-16 | code/training-execution-supported：项目 ar_running_factor_activation，实际运行配置/冻结源码/日志哈希与完整计数；064e95、f1baf3 均退出 0 | 日志相同非中间权重逐值比较；范围值涉及采样损失、标量比非参数梯度比；clamp 尚全单步，七组最终预测仍待完成，不据此取消训练 |
| AR-RUNTIME-002 | 原节点 0 绑定方案因两节点大块内存条件变化撤回，未执行；四组训练耗时自行回落。真实训练样本分配短测关闭大页均值慢 22.24%，编码数组哈希一致；冻结续训不保存 RNG 状态 | runtime/limited-supported：项目 ar_runtime_slowdown_followup；10 秒进程/全局计数、冻结源码片段、NumPy 2.4.2 的 ABBA 四个 CPU 子进程共 12.83 秒，初始路径失败已记录，恢复后全部退出 0；原四个训练 PID 与 Slurm 均存活 | 无内核栈归因；一个样本及短窗口不代表高压时段或整轮吞吐。未改系统/训练设置、重启或提交作业；不是预测改善，旧 CPU 确认不再待执行 |
| AR-NUM-001 | 原 v10 生成器在一个训练病例 0–2 ms 按原保存精度逐值重现双场；两次内步减半的相邻 RMS 差约减半。起点 RHS 单次 2 ms Euler 对真实目标已有 2.304 mV/5.432 nM RMS 差 | numerics/short-interval-supported：项目 ar_generator_replay；原函数体/初态/图/标签哈希，43,573 节点，0.02/0.01/0.005 ms 内步，4 CPU 线程，24.44 秒（不含前置导入），695d3d 退出 0 | 使用完整初态仅核验生成器，未给 AR 增加输入；一个短段不能支持全程收敛、全训练容差或预测精度。仅禁用缓存/改验证线程数，无模型或远程作业修改，无遗留验证文件 |
| AR-GRAD-001 | 12 个训练窗口中 10 个 V 上升/下降参数梯度余弦为负，中位 −0.8279；范数比中位 2.5084，8 个下降项与总梯度负相关 | gradient/local-supported：ar_parameter_phase；冻结 6845/原 AR 图、372–500 ms，原损失及梯度和核对；最大误差 2.81e-7、相对 L2 3.60e-7，71.79 秒/2.046 GiB，18f611 退出 0 | 固定权重、单时间窗；未模拟 AdamW、裁剪和权衰的实际参数步，未重新加权训练或证明精度改善 |
| AR-GRAPH-001 | 既有本地图差异在服务器冻结 AR 上复核：7,405 条边/节点不同于原生成器，距离多重集相同；检查进程设 leafsize=10 后规范边数组匹配 | code/graph-supported：ar_graph_difference；本地 SciPy 1.16.3、服务器 1.17.1 实际数组/源码哈希；876ac8、28a690 退出 0 | 不是首次本地发现；正式图未改、未重训，未确定对晚期误差的贡献，不唯一认证全部历史生成设置 |

## 2026-09-17：无 PCA 的 Neural ODE 本地探索

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| NODE-GRAPH-001 | 原始 43,573 节点 V/Ca/h 联合积分已实现；200 更新短训练出现激活消失，低 RMSE 不代表有效传播 | code/supported、prediction/failed（有限验证病例）：项目 results/neural_ode/session_20260916/round_2_graph；训练退出 0、458.244 秒，四例激活漏检约 99.99%；独立展示的 batch_020/sample00 有 51,677 真激活/7 预测事件、F1=0.0001935；完整窗口步长差 0.0000984 mV/0.0001252 nM，遮蔽/重载通过，PNG 已查看 | 尚未区分训练不足与结构不足；不是完整测试或 PCA 单因素实验；训练/选模允许未来，与严格 AR 不同 |
| NODE-GRAPH-002 | AR 网络可初始化一个联合连续场/记忆 ODE；初始化四例预测与 AR 基本持平；长窗口梯度可在本机显存内计算 | code/numerics/limited-supported：graph_memory_initial 的 verification.json/paired_val4，1/0.5 ms 差 0.01358 mV/0.08219 nM；99 项回归通过；graph_memory_backward_recompute 全 500 ms 反向检查 56.976 秒/4.69 GiB，梯度有限、权重逐值不变。前一次高显存检查主动停止，记录 resource_stop.json | 不能继承 AR 为精度保证；下降 F1 从 0.20198 到 0.18611；未完成新微调的预测验证，也未证患者能力或不确定性 |
| NODE-GRAPH-003 | 40更新微调降低全部90例的双场全窗口RMSE，但激活F1退化，联合验收失败 | prediction/partial-improvement：项目 results/neural_ode/session_20260916/report.md 与 round_3_graph_memory/test_all90；全窗25.7726 mV/170.7978 nM，对照53.6497/293.2225；激活F1 .479255/.571008，下降F1 .185571/.179894但下降精度更差。训练984.423秒、评估1119.503秒均退出0；权重选择先于测试且哈希一致；配对工具74c5c6退出0，numeric_gate_passed=false；代表性PNG已查看 | 新模型可用未来训练标签，与旧严格AR不同；非架构单因素归因、非全新盲测、单次短训练；未完成正常传播与患者/不确定性验证 |
| NODE-LOSS-001 | 备用BCE激活损失可给自信但错误的状态更强电压梯度，旧恢复默认保持平方误差 | code/algebraic-supported：Live 101项测试（0fc427）、8文件AST/diff（54bfbc）、round4授权上限拒绝检查（57ef4f）；两个验证病例三帧的代数诊断见 activation_gradient_diagnostic.json；未计算参数梯度或优化更新 | 不是性能改善或失败的唯一原因；第四轮未获授权、未启动；不改第三轮冻结代码/权重/结果 |
| NODE-EVENT-001 | 2026-09-18 原90例指标显示77例双场误差降低但激活F1下降，漏检与误报同时增多；无时间容差的节点覆盖也下降 | prediction/post-hoc-diagnostic：项目 round_3_graph_memory/event_diagnostic/diagnostic.json 与 PNG；CPU脚本4dbd3a，0.789秒退出0；1bee74核对原指标哈希、配对真值、计数恒等式与AST；激活误报235826→529809，首次激活节点召回.53138→.45860；主报告中文编码另已修复 | 没有执行模型/训练或改变第四轮提案；汇总不能唯一分开位置、时序与重复事件错配，条件时间MAE不能证明整体时序变好；非新盲测，仍未达成联合验收 |
| TRANSFER-001 | 代码与图表包已生成，排除数据/权重/基底及逐节点 TXT；按来源收齐 2,798 张 PNG，补 56 张日志或已有预测图 | artifact/supported：`exports/pde心脏代码3.zip`，1,099,858,656 bytes，7,346 条目逐项读取并匹配 SHA-256；ZIP SHA-256 `cfcfd384496ae3b6168b880a01bc699c252a019cf7cd1cd2858cec71ce5a26c5`；5,597 个图表页面链接检查通过；记录在 `runs/transfer-package-20260917/verification.json` | 仅迁移包完整性；原模型代码未由本次整理修改。2,570 张属于 DIMON 参考资料；短实验/缺图及持续更新日志的快照范围在包内注明。未训练、推理或操作远程作业，不是预测改善证据 |

| NODE-QUEUE-001 | 已注册 neural-ode 独立任务，只读预览与队列回归通过（2026-10-09 重建，原文编码损坏） | workflow/supported：problems/cardiac-research/items/neural-ode/task.json；runs/neural-ode-task-20260929-111403/checks.json；list/plan/packet/dry-run/queue-tests.log 5 项退出码 0；26 项队列测试通过；ar-pca 任务与历史预算 SHA-256 未变 | 任务注册不等于研究启动或目标完成；未创建任务运行目录、未调用模型；详见同目录 final-verification.json |

## 2026-09-30：空间记忆副本与服务器验证

| ID | 有限结论 | 验证维度与证据 | 未覆盖范围 |
|---|---|---|---|
| NODE-GLOBAL-001 | 独立实现132区域H、单/多尺度和软/硬反馈约束，原五文件哈希未变 | code/numerics：254 Slurm7051真实网格与全500ms检查，7052最终36测试；项目results/neural_ode_global_memory/session_20260930/{report.md,source_integrity.json,real_check.json,full_window_check/verification.json,tests_7052.log} | 新训练0更新，尚无效果改善；硬约束只是同驱动H收缩，非全系统保证；初始零输出分支的全窗验证不能替代训练后检查 |
| NODE-GLOBAL-002 | 形态评价器已在旧基线两验证例产出指标及PNG | evaluation/implementation：Slurm7049，initial_validation/metrics.json；V16.671mV/Ca109.819nM、Dice.6523、激活F1.6344；7052另测静息窗口缺失指标处理 | 小样本评价器预检，非新模型结果，不能归因缺少H；未选候选/用测试选模 |
| NODE-GLOBAL-QUEUE-001 | 新工作台任务和CLI已部署，真实模型循环尚未运行 | workflow/partial：Slurm7050的agent_check.log显示errors=[]但未登录；新预算null由测试确保拒绝训练 | 等待新增时长/次数和登录方式，不复制凭据、不消耗旧预算、不称自主研究已运行 |
| NODE-GLOBAL-AUDIT-001 | 离线复核发现并修正记忆约束零点梯度边界、续训计数、异常状态；统一课程和计划/权重校验 | source-reviewed、artifact-supported：2026-10-02 session_20261002/static_review.json；原5源码/3预训练初始化哈希一致，新副本44测试定义，未执行项目代码/SSH | 不是运行验证；新增检查与训练均待254 Slurm，旧36通过不可外推；模型效果与闭环稳定性未知 |
| NODE-GLOBAL-RUN-001 | 2026-10-08 Slurm7162通过当前44项回归并开始六组训练，首组已有更新及checkpoint | code/workflow：session_20261002/resume_20261008/{tests_7162.log,job_7162_startup.txt,suite.json,budget.json,train_baseline.log,frozen_7162/sha256.json}；4.643秒全部通过，冻结11源码哈希匹配审查 | 启动快照；需实时查询7162和服务器账，非六组完成；H预测收益/单例推理延迟未验证；sacct历史统计不可用 |
| NODE-PURE-001 | 独立直接导数ODE从零训练入口可用，无AR初始化或未来一步算子；历史GRU保留 | code/limited-numerics：CPU Slurm7164退出0，10测试通过；项目results/neural_ode_pure/session_20261008/{tests_7164.log,job_7164.txt,real_check_7164/real_check.json,frozen_7164/}；真实43,573节点/132区域、251帧历史与2ms预测重载通过，89,280参数 | 实现及初始化短验证，真实数据0更新；未新增GPU训练或修改7162；无完整预测效果/加速结论；检查后main仅改一处说明文字 |
| NODE-GLOBAL-SCREEN-001 | 7162六组均80更新/12验证；hard-H候选V17.57mV/Ca134.71nM/Dice.567优于所选baseline的22.97/148.10/.495；scratch短训未形成有效激活传播 | validation-screen：session_20261002/{suite.json,budget.json,screening_review.json,screen/}；12子进程exit0，6395.09秒，6/6名额使用 | 单种子、非独立测试；best步数25/25/80及scratch65不同；hard时序误差与误报上升；不能把旧scratch当新Pure结果或评价耗时当推理延迟 |

### NODE-PURE-CONFIG-500 — 2026-10-08
- 用户选择：500 epoch×200随机窗口更新，其余Pure参数不变；这是更新量对齐，未改变训练/验证监督协议。
- 修改：Pure main默认参数、独立Slurm训练脚本和README；正式GPU未提交，旧筛选额度未重置。
- code supported：Slurm7173 COMPLETED/exit0，Bash语法、10回归及真实网格2ms检查通过；CPU作业34秒。
- prediction/numerics/personalization/uncertainty：未新增证据，不能称完成500轮或证明预测有效。
- 证据：项目results/neural_ode_pure/session_20261008/config_500_review.json、job_7173.txt、tests_7173.log、real_check_7173/real_check.json及frozen_7173。

### NODE-FULL500-SUBMIT — 2026-10-08
- 用户新授权全部九组各500×200并量化推理，源模型不改；新session冻结源码、初始化哈希和单卡串行预算。
- code supported：Slurm7174 COMPLETED/exit0，44+10+9=63测试；7178报告入口exit0。
- 执行：7175 GPU检查/测速排队Resources；7176_0–8正式训练数组等待7175成功；7177最终汇总等待7176。未宣称训练开始/完成或实测速度。
- 方法：同43573节点、251帧历史、250帧预测、float32、batch1，3固定例×5重复/2预热，CUDA同步，分编码/积分/实际rollout计时并验证预测一致；显存峰值含三例常驻输入。训练后每组best自动重新计时及60例验证。
- evidence：results/neural_ode_full500/session_20261008/{manifest.json,submission.json,checks/,submission_*.txt}；新benchmark和runner静态交叉审查发现preview已有目录冲突，提交前已修复并冻结。
- prediction/numerics/personalization/uncertainty：尚无新增结论。旧80步screen不可作为正式500轮结果。

### NODE-BOUNDARY-001 — 2026-10-10

- 用户要求：内部状态＋各条边界动态→带位置信息的非线性特征→区域H，边界信息融合，不新增独立E。独立复制Pure，保留原框架与正式实验。
- 实现：节点72→16→24先编码再区域汇总；跨区域细边143→16→24，按有向区域对汇总后写入接收区域。观测率是后向差分/2ms，预测率由当前RHS计算，未读未来真值。
- code supported：CPU Slurm7204基线10测试通过；7207完整43573节点/132区域/251观测/250未来帧有限性、精确锚点与重载、记忆梯度检查通过；7208最终23测试通过，退出0。新增空界面验证器修正及因果输入回归仅影响检查入口，7207/7208的opnn.py SHA相同。
- 数量：19335跨区域细边、675有向界面、90568参数，H仍132×24。最后仍压缩各界面，不保证完整逐界面历史。硬约束仅相同固定drive下H方程收缩；新drive经du/dt依赖H，不能由固定u/h或原证明宣称闭环稳定。
- evidence：项目results/neural_ode_boundary_memory/session_20261009_2047/，real_check_7207/real_check.json、tests_7208.log、frozen_7207/、frozen_7208/及source_*.sha256；原Pure哈希记录original_pure_sha256.json。
- prediction/numerics/personalization/uncertainty：新精度、训练后GPU时延、数值收敛、患者能力均未评估。真实数据0优化更新，梯度检查目标是2ms后的记忆平方范数；初始化H读出为零，场损失第一轮写入梯度为零。未追加第十组500×200训练或改动现有作业。
