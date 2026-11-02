# 方法族登记表

| Family | 核心机制 | 决定性子目标（A 节点） | 可证伪测试 | 状态 | 结构性障碍 | 重开条件 |
|---|---|---|---|---|---|---|
| F1 AR 一步算子 | GRU + 图传播的 2 ms 一步算子，自回归推进 | A1：AR 在 ≤500 ms 监督/选模下 90 例晚期误差与激活指标达标 | 七组消融配对比较；persistence 对照 | partial-result | 晚期 RMSE 66.80 mV、漏检 46.86%；nogru 场误差低但激活 F1 .179（failure-case） | 新记忆机制或新监督信号能同时降场误差和升激活 F1 |
| F2 固定 PCA 低维推进 | 分通道固定空间基底 256+256，系数空间 GRU/MLP 推进 | A2：PCA-GRU 优于 PCA-MLP 且不劣于 AR | pca_oracle 重建下限；自由预测对条件动力学 | pushing | 重建误差是预测下界（S3）；GPU 训练未启动 | 无 |
| F3 图 Neural ODE | 原始网格 V/Ca/h 联合连续积分，AR 权重初始化 | A3：同协议下激活 F1 ≥ AR .571 且双场误差更低 | 90 例配对；下降事件 F1 | partial-result | 第 4 轮激活 F1 .567；早期 Ca 差；协议与 AR 不同（definition-mismatch） | 统一协议后重比，或新激活损失 |
| F4 直接时间查询 | 历史编码后直接查询未来时刻，无回灌 | A4：与 AR/PCA 对齐协议后的比较 | 对齐 500/1000 ms 监督与选模 | planned | 没有 strict-validation 开关（missing-tool） | 实现许可窗口选模 |
| F5 区域记忆态 H | 132 区域 24 维 H，节点 h 保留；软/硬约束；边界融合 | A5：有 H 在同协议下激活 F1 与时间 MAE 优于无 H | 六组筛选；九组 500×200 正式训练 | pushing | hard-H 时间 MAE 25.2 → 35.5 ms、误激活 .65% → 4.41%（failure-case 候选） | 正式训练后重评 |
| F6 结构化线性潜态 | 历史估计潜态，固定或病例条件化线性生成元，以矩阵幂/解析块推进 | A6：在统一协议下取得可用精度/训练和推理时间折中 | 共同表示重建、latent线性一致性、全窗自由预测及GPU时间 | planned | 有限维线性闭包与波前交互能力未验证 | 非线性表示通过重建检查后，作低成本动力学对照 |

## 覆盖审计
- 当前覆盖：离散一步算子、低维系数动力学、连续 ODE、直接查询、区域记忆。
- 尚未运行：显式闭包/隐态重构（S1 的直接检验）、Koopman/DMD 类线性算子（F6仅planned）、含 CRN 残差的物理约束。
- 同一障碍连续失败次数：激活 F1 在 F1/F3/F5 上各 1 次。
- 下一轮为何有信息增益：九组正式训练把 F3/F5 的 80 更新筛选推到 100000 更新，首次给出同预算比较。

## F1 AR 一步算子
- 实验卡：七组 baseline/mixed/noise/range/clamp/events/nogru，各一次，500 轮/100000 更新，训练与选模 ≤500 ms，90 例测试只输入 0–500 ms；指标全域/活动区 V、Ca RMSE，激活漏检/误检/时间 MAE，下降 F1；单种子。
- 证据：AR-BASE-001、AR-BASE-002、results/ar/audit_20261008/summary.json。
- 已完成子实验：ar-split-duplicates（AR-DATA-002）、ar-increment-capacity（AR-CAP-001）、ar-adaptive-time 可行性（AR-TIME-001）。
- 候选：ar-adaptive-time 实施（先学 2/4/8 ms 并匹配物理展开时长），planned。

## F2 固定 PCA 低维推进
- 实验卡：固定 6873/256 基底，GRU256 对无记忆 MLP，同预算、≤500 ms 选模，只比两场自由预测。
- 证据：pca_oracle / pca_forecast / pca_conditional（项目 summary）；PCA-DEPLOY-001。
- 状态：服务器 code/pca 已部署，GPU 未启动。

## F3 图 Neural ODE
- 实验卡：训练标签可至 1000 ms，测试输入 ≤500 ms；AR 权重初始化后各 40 更新微调；90 例评估。
- 证据：NODE-GRAPH-001/002/003、NODE-EVENT-001、NODE-LOSS-001。
- 候选：neural-ode-one-day（2 ms Heun RK2、h32、一图层、区间 checkpoint，目标 200 更新 ≤144 s），planned，未提交。

## F4 直接时间查询
- 实验卡：对齐 500/1000 ms 监督、历史输入、选模、更新预算和 clamp 后比较。
- 障碍：Direct 入口无 --strict-validation；需新增有测试覆盖的选模方式。

## F5 区域记忆态 H
- 实验卡：六组 baseline/scratch_baseline/multi/scratch_multi/multi_hard/scratch_multi_hard，各 80 更新、8 epoch 课程、12 例验证；九组 500×200（旧六组 + Pure 三组）单卡串行，每组 best 测速与 60 例验证。
- 证据：NODE-GLOBAL-001/002/AUDIT-001/RUN-001/SCREEN-001、NODE-PURE-001、NODE-FULL500-SUBMIT、NODE-BOUNDARY-001。
- 边界记忆分支：code/NeuralODE_BoundaryMemory，implementation-verified，真实数据 0 更新。

## 2026-10-15：速度诊断后的候选实验卡（planned）

完整卡片与文献映射见项目 `docs/neural_ode/design.md` 同日章节；不是新算力授权，不修改原九组作业。统一600/60/90切分、0–500ms输入/502–1000ms评分；新训练明确沿用Pure监督≤1000ms并单列val选模窗口，不混同严格P500协议。测试集已开发暴露。

- F3数值消融：假设昂贵全图RHS的2000次重复是纯模型瓶颈。固定epoch246权重和3例val性能病例，比较RK4 0.5/1/2ms、Heun1/2ms，记录同步时延/NFE/峰值显存和完整窗场/事件指标。仅改solver；不改变h、图层、clamp或重训。门槛先冻结，数值差或事件退化则停止放大步长。所有执行均走254 Slurm，未提交。
- F2/F3表示联合候选：复用RecoveryLatentODE的PCA512+64作低维RHS基线，先oracle连续轨迹重建，再自由预测；表示不足时比较非线性多尺度图latent。假设低维推进能保留历史恢复态和传播；主要障碍是波前/再次激活表示误差，不能以少量latent或低重建MSE认定闭包充分。基底只拟合允许训练数据，解码完整250帧成本计入。新训练预算/种子及val规则需在执行卡落定，当前未启动。
- F4直接查询候选：同一潜空间上训练时间条件flow，蒸馏仅用训练病例并对真实训练标签校正；作为取消积分循环的对照。检查初值、跨时距一致性、V/Ca与事件指标，不称自动满足自治半群或外推保证。架构、训练/选模、完整解码输出须与ODE清楚对齐，当前无训练/测速。
- 软件性能候选：推理输出的切片view可能保留250份完整h状态；独立核查复制两通道/预分配输出和batching，再定位完整评估的I/O、CPU事件与JSON开销。此项不构成新科学方法族；速度收益尚未实测。

## 同日续：训练与推理共同目标下的框架筛选

直接证据：Pure只有一个共享GRU，节点作batch、历史时间串行；未来不执行GRU。暖身后每轮200更新平均93.2预测帧，原始未来前向149120 RHS/447360细图稀疏乘，尚未计反向/嵌套checkpoint。loss_nodes4096不减少全节点推进。当前无训练阶段profiler，不能拿推理3%编码占比证明训练GRU占比。细节、原文与完整实验卡在项目docs/neural_ode/design.md的“逐节点GRU、训练成本与替代框架”。

- 首选F4延伸：拓扑受约束空间压缩→TCN/SSM一次历史编码→时间条件latent查询→采样节点解码；训练不经过未来积分或长unroll。参考DeepONet/Poseidon随机时间pair；已有Direct仍有细节点GRU和每query全图层，不能只改名或删GRU。新anchors≤500ms，以对齐Pure监督≤1000ms。
- 备选F2/F1延伸：UPT式小latent离散推进，RIGNO式多尺度空间编解码；配对/短展开训练，最终自由rollout。UPT原训练有额外重编码/解码开销，训练提速未证；不把SSM模块、latent表示、Transformer名称另算新方法族。
- 新F6/A6探索对照：共同表示下固定或由起点历史条件化A，exp(τA)或K^m推进；避免非线性长反传。主障碍为线性闭包和局部波前/再次激活欠拟合，尚无数据支持。
- 预算提案：单卡20min分项诊断；每动力学候选60min单种子筛选、共同表示训练/缓存成本另列；seed20260917，固定12val筛选/60val验收。均planned未提交，无新算力授权，不改既有500×200作业；以相同GPU时间、实际更新/query数量和达到同精度时间比较，短预算失败不排除方法族。协议保持600/60/90、0–500输入/502–1000评分、固定量程/无clamp；旧90例已暴露。
