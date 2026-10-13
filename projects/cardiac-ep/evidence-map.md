# 数据与结论依赖

v10 生成器 + 实际 NPZ → 结构/值/节点/切分核查 → Scaler 与可选 PCA 拟合清单 →
AR/PCA/Direct 源码与 checkpoint → 固定协议预测 → 指标/图 → 有限结论。

任一上游改变都检查受影响下游；不用旧结果为新源码或新基底背书。
运行记录 run.json 的源码哈希描述当次执行，不能从后来修改的源文件重建过去代码。
几何/参数个体化分支需要新的动力学条件和独立校准/验证数据，目前不从 v10 预测分支继承验证。

Neural ODE 独立分支（2026-09-17）：v10 原始节点与既有参考图 → 固定量程归一化（无 PCA） →
训练/验证允许 0–1000 ms 标签、预测输入截断到 500 ms → graph_neural_ode.py → 独立源码快照与 budget.json →
round_2_graph（激活坍缩）/ graph_memory_initial（初始化配对）/ round_3_graph_memory（微调） → 完整场与事件验收。
原始运行位于项目 results/neural_ode/session_20260916；99 项回归及梯度/遮蔽证据不能代替预测效果。
AR 初始化权重 SHA256 9f39d68870b01e34858f03128789c579c3dd625a6d0ce3b960b668b18fbde048；它的严格监督协议与新微调不同。

## 2026-09-30 空间记忆证据链

服务器dataset/batch_000..024.npz → 完整批次20/2/3切分、0–500ms输入、归一化沿用旧checkpoint → source_best.pt(SHA70c58549...) → 六组共同初始化 → 参考细图连通聚合132区域H → Slurm7051实现/数值检查与7052最终36测试。原始证据在项目results/neural_ode_global_memory/session_20260930/，详见report.md。
旧基线两例验证→initial_validation/metrics.json和PNG仅支持评价器可运行及现有形态误差存在。尚无新模型训练→验证比较→候选冻结→测试验证链。新budget未确认、服务器CLI未登录，工作台真实多轮结果也尚不存在。