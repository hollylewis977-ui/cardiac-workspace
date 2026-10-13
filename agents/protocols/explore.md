# 探索与路线诊断

方法族按核心机制归族，登记在 projects/cardiac-ep/ideas.md；换超参、换名、换措辞不算新族。初次研究或结构性改线至少三族；后续沿 CURRENT_STATE 的最小缺口推进。

每个 A 节点必填实验卡：假设、改变因素、对照、数据与时间协议、主要指标、种子与预算、停止条件、产物。公平比较控制或报告监督范围、可用历史、模型规模、更新次数、选模方式与 clamp。先固定评价标准再跑测试。

从现有结果的具体失效切入：波前衰减、误激活、晚期电位偏移、低维表示不足、长期推进误差。先判断是数据、实现、表示、优化还是累积误差，用最小诊断区分。

同一障碍失败两次不重复原推导：改表示、弱化目标、找失效案例，或按 independent-replication.md 申请独立复核。记录失败位置与类型：gap 缺实验或证据；failure-case 被病例否定；circular 测试真值选模或 oracle 混入预测；too-strong 命题超出数据支持；definition-mismatch 协议不同还硬比；reference-mismatch 文献方法前提不符；missing-tool 缺标签、数据或预算。暂时还是结构性、影响范围、中间结果都写。

只有新机制、新表示、新数据或新工具能直接攻击原 gap 才重开路线；改名或加 Agent 不算。关键结论失效只回退依赖分支，降为 blocked / partial-result / GAP。候选主结果转 claim-audit，失效案例转 failure-case-audit。没有运行的方案保持 planned，不虚构提升。
