# 时间外推算子：正式题目

搜索承诺：either（既找有效算子，也找严格失效案例）。来源标签：internal / provided-source / web-source。

## 定义与归一化

- 参考域 Ω：二维网格，N = 43,573 节点；参考图 L 为邻居差分算子（生成器 ref_nm）。
- 状态 y(t) ∈ R^{N×21}，演化 y'(t) = D·L y(t) + R(y(t))，D = 0.08，R 为 Courtemanche 1998 反应项。生成器每步先做扩散并裁剪 V，再离子步进。
- 时间：内部步长 0.02 ms，保存步长 2 ms，共 1001 帧（0–2000 ms）。
- 观测算子 O(y) = (V, Ca) = (y₀, y₁₈)。记 u_k = O(y(2k ms))。
- 流映射 Φ_τ: y(t) ↦ y(t+τ)。代理模型 G 只能作用在观测序列上，不能作用在 y 上。
- 数据：750 例，初值由单细胞模板初相位生成；x_mesh 形变坐标不进入演化。按完整文件切分 train=batch_000..019、val=020..021、test=022..024，即 600/60/90 例。
- 归一化：Scaler 固定 V ∈ [−100, 50] mV、Ca ∈ [0, 0.0012] mM；NRMSE 分母 150 mV / 0.0012 mM。
- 激活事件：V 上穿 −20 mV；首次激活漏检、误检、匹配时间 MAE 按 code/TC_GCN_server 的事件评价实现；无匹配事件时 MAE=0 不算准确。
- 四个时间范围必须分别声明：训练监督截止、验证选模窗口、测试观测截止、评分窗口。

定义的逐条说明见 library/definitions/。

## 主命题 P0

存在算子 G，仅以 u₀…u₂₅₀（0–500 ms 观测）为输入，使未见初值的病例在 k = 251…500（502–1000 ms）上，V 与 Ca 的 NRMSE 以及首次激活事件指标（漏检率、误检率、时间 MAE）同时达到验收阈值。

验收阈值由研究者填写。在填写前，候选算子必须至少优于旧 AR 基线：晚期 RMSE 66.80 mV / 405.65 nM，首次激活漏检 46.86%，下降事件 F1 0.180（AR-BASE-002）。

## 辅助命题

| ID | 命题 | 当前等级 | 可证伪测试 |
|---|---|---|---|
| S1 闭包 | 0–500 ms 的 V/Ca 历史决定 y(500 ms) 的全部 21 维 | conjecture | 用生成器构造同一观测历史、不同隐态的两例，比较 502–1000 ms 的 V/Ca 是否分叉 |
| S2 一步算子累积 | 2 ms 一步算子 G₁ 推 250 步后误差可控 | experimental（AR 七组晚期误差） | 固定权重下误差随预测跨度的曲线；persistence 对照 |
| S3 低维表示 | PCA256 的重建误差低于验收阈值 | partial-result（pca_oracle） | 90 例重建误差分布 |
| S4 记忆态 H 充分性 | 区域记忆态 H 补足 S1 缺的信息 | experimental（六组 80 更新筛选） | 有 H 与无 H 在同协议下的激活 F1 与时间 MAE |

## 允许使用的基础事实

- 生成器源码事实（上节）。
- verification-ledger.md 中等级为 agent-verified 及以上的条目。目前没有；AR-BASE-001 是第一个审查对象。

## 已知结果

| 结果 | 等级 | 证据 |
|---|---|---|
| AR 七组消融 | proof-draft | results/ar/audit_20261008/summary.json；AR-BASE-002 |
| Neural ODE 第 3 轮 90 例全窗 25.77 mV / 170.8 nM 对 AR 53.65 / 293.2 | proof-draft | NODE-GRAPH-003 |
| 六组 H 筛选，hard-H V 17.57 mV / Ca 134.71 nM / Dice .567 | experimental | NODE-GLOBAL-SCREEN-001 |
| 九组 500×200 正式训练 | 进行中 | results/neural_ode_full500/session_20261009_recovery/ |

## 已试路线与失败位置

- F1 AR：晚期 RMSE 66.80 mV，首次激活漏检 46.86%；nogru 场误差最低但激活 F1 仅 .179，失败类型 failure-case。
- F3 图 Neural ODE：第 4 轮双场改善但激活 F1 .567 低于 AR .571，早期 Ca 差；与 AR 的监督/选模协议不同，失败类型 definition-mismatch。
- F5 区域记忆态 H：hard 约束激活时间 MAE 25.2 → 35.5 ms、误激活 .65% → 4.41%，失败类型 failure-case（候选，未认证）。

方法族登记见 ideas.md，路线状态见 research-tree.md，命题依赖见 claim-map.md。

## 不属于本题

几何个体化、参数反演、真实患者验证属于第二道题 problems/cardiac-research/items/personalization/problem.md；当前数据的几何形变不进入动力学，不能从本题结果推出。
