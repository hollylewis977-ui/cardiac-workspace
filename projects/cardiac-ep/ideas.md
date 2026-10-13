# 方法族登记表

| Family | 核心机制 | 决定性子目标（A 节点） | 可证伪测试 | 状态 | 结构性障碍 | 重开条件 |
|---|---|---|---|---|---|---|
| F1 AR 一步算子 | GRU + 图传播的 2 ms 一步算子，自回归推进 | A1：AR 在 ≤500 ms 监督/选模下 90 例晚期误差与激活指标达标 | 七组消融配对比较；persistence 对照 | partial-result | 晚期 RMSE 66.80 mV、漏检 46.86%；nogru 场误差低但激活 F1 .179（failure-case） | 新记忆机制或新监督信号能同时降场误差和升激活 F1 |
| F2 固定 PCA 低维推进 | 分通道固定空间基底 256+256，系数空间 GRU/MLP 推进 | A2：PCA-GRU 优于 PCA-MLP 且不劣于 AR | pca_oracle 重建下限；自由预测对条件动力学 | pushing | 重建误差是预测下界（S3）；GPU 训练未启动 | 无 |
| F3 图 Neural ODE | 原始网格 V/Ca/h 联合连续积分，AR 权重初始化 | A3：同协议下激活 F1 ≥ AR .571 且双场误差更低 | 90 例配对；下降事件 F1 | partial-result | 第 4 轮激活 F1 .567；早期 Ca 差；协议与 AR 不同（definition-mismatch） | 统一协议后重比，或新激活损失 |
| F4 直接时间查询 | 历史编码后直接查询未来时刻，无回灌 | A4：与 AR/PCA 对齐协议后的比较 | 对齐 500/1000 ms 监督与选模 | planned | 没有 strict-validation 开关（missing-tool） | 实现许可窗口选模 |
| F5 区域记忆态 H | 132 区域 24 维 H，节点 h 保留；软/硬约束；边界融合 | A5：有 H 在同协议下激活 F1 与时间 MAE 优于无 H | 六组筛选；九组 500×200 正式训练 | pushing | hard-H 时间 MAE 25.2 → 35.5 ms、误激活 .65% → 4.41%（failure-case 候选） | 正式训练后重评 |

## 覆盖审计
- 当前覆盖：离散一步算子、低维系数动力学、连续 ODE、直接查询、区域记忆。
- 尚未覆盖：显式闭包/隐态重构（S1 的直接检验）、Koopman/DMD 类线性算子、含 CRN 残差的物理约束。
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
