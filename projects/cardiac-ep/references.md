# 文献与架构对照表

来源标签：internal / provided-source / web-source。阅读状态：read / abstract-only / GAP。核查记录见项目 results/ar/analysis/summary.json: ar_physics_literature（2026-09-16）。

| 方法 | 论文或代码 | 对象层级 | 状态与观测 | 算子类型 | 时间处理 | 几何处理 | 训练数据规模 | 指标 | 与本项目差异 / 可借鉴 | 来源 | 阅读状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DIMON | 项目 docs/（原仓库 DIMON 参考资料） | 组织 | 参考域场 | DeepONet 类 | 参数化时间查询 | 微分同胚映到参考域 | 见原文 | 场误差 | 本项目参考域思想来源；无时间窗外推 | provided-source | read |
| FBNO | code/FBNO_time_forecast（借用思想） | 组织 | 自由边界 H | 参考域直接算子 | 直接查询 | 自由边界 | 见原文 | 场误差 | 本项目未实现完整自由边界 H 与 CRN 残差 | provided-source | abstract-only |
| 可微心脏电生理仿真（状态与参数估计） | Differentiable Cardiac Electrophysiology Simulations for Dynamical State and Parameter Estimation，arXiv 2607.15492 v1（2026-07-16），https://arxiv.org/html/2607.15492v1；本地 docs/papers/differentiable.pdf | 组织 | AP/MS 恢复状态，观测窗内估计后自由演化；钙成像作电压代理 | 可微物理模型拟合 | 连续 | 固定 | 见原文 | 场误差 | 支持"状态估计"候选，不是 CRN 代理；逐例拟合不同于共享预训练 AR（AR-LIT-001） | web-source | read（II.1、II.3.3-5、III.2、III.7、图 5-6、17） |
| 高维离子模型 FNO | Learning high-dimensional ionic model dynamics using Fourier Neural Operators，2025-12-08，https://link.springer.com/article/10.1007/s44379-025-00046-8；代码 https://github.com/MaxGhi8/HyperNOs；数据 https://doi.org/10.5281/zenodo.14865789 | 单细胞 | 电流函数 → 完整离子轨迹（含 41 态 ORd），全分量监督 | FNO | 自回归/算子 | 无 | 见原文 | 轨迹误差 | 细胞 ODE 算子；本项目是部分观测空间预测、≤500 ms 监督 | web-source | read（第 2 节式 1-3、3.1、Limitations、附录 A.3、B） |
| 全心电机械 Latent Neural ODE | Whole-heart electromechanical simulations using Latent Neural Ordinary Differential Equations，npj Digit. Med. 2024-04-11，https://www.nature.com/articles/s41746-024-01084-x；索引全文 https://pmc.ncbi.nlm.nih.gov/articles/PMC11009296/ | 全心 | 压力容积 | Latent Neural ODE | 连续 | 无 | 见原文 | 时间序列误差 | 学压力容积动力学而非 V/Ca 场；隐空间思想对应本项目 Neural ODE 分支 | web-source | abstract-only（出版社摘要与索引的方法/讨论节选，整页访问失败） |

联网调研回合按 agents/protocols/literature-check.md 追加行；没读到原文的行阅读状态保持 GAP。
