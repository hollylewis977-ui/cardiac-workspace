# 心脏项目源码索引

核对日期：2026-10-14。路径相对 cardiac-workspace.json 的 project_root。数据、协议与命令见 problem.md 与 README.md。
以下为当前本机源码事实；历史文档和远程任务状态不能替代本次核验。

## 主要入口

| 路径 | 作用与适用场景 |
|---|---|
| code/TC_GCN_server/main.py | inspect/train/rollout/evaluate/fit-pca/diagnose-pca；AR 与低维 PCA 共用训练评价；也支持 graph_neural_ode 两种模型类型 |
| code/TC_GCN_server/model.py | ReferenceOperator（GRU+图传播的一步算子）；FixedPCACodec、PCALatentOperator |
| code/TC_GCN_server/data.py | NpzBatch 内存映射、Scaler、参考图、可选几何 sidecar、数据切分 |
| code/TC_GCN_server/ar_experiments.py | 7 组 AR 消融、smoke、train、diagnose、suite；oracle 诊断需与自主预测区分 |
| code/TC_GCN_server/run_pca.py | 固定 PCA256+256、GRU256 或无记忆 MLP、混合展开 16/32/64/128/192 |
| code/TC_GCN_server/neural_ode.py、run_neural_ode.py | 旧 PCA 系数/隐特征 ODE 原型；0–1000 ms 监督、502–1000 ms 验证选模，区别于严格 ≤500 ms AR 消融；见 AR-ODE-001 |
| code/TC_GCN_server/graph_neural_ode.py、verify_graph_ode.py、evaluate_graph_ode.py | 原始网格连续 V/Ca/h 图 Neural ODE、完整反向检查、配对评估；设计 docs/neural_ode/design.md，记录 results/neural_ode/session_20260916 |
| code/TC_GCN_server/quantify_results.py、plot_results.py | 固定权重量化和 PNG 图 |
| code/visualization/generate_visualizations.py | 正式图（SCI 风格）：`--npz` 读 rollout NPZ（times_ms/coords/true_v/pred_v/true_ca/pred_ca），出 voltage/calcium/traces/error(/ecg).png；标题 NRMSE 按固定分母 150 mV / 0.0012 mM，与台账一致；旧 `--case-dir` 读 snapshot_k.txt 不变。工作台任务 plot-sci 以 results/ar/reference/prediction.npz 为例 |
| code/visualization/visualize_dataset_dynamics.py | 从 v10 NPZ 直接画单例 V/Ca 动态 |
| code/FBNO_time_forecast/main.py、model.py、data.py | 历史条件直接时间查询；未来预测之间没有回灌 |
| code/FBNO_time_forecast/audit_data.py | 专项全批次头/坐标/初值与部分轨迹核查；比 doctor 更重 |
| code/NeuralODE/ | utils/opnn/main/test 四件套，只含 graph_memory_ode_v1，与冻结结果逐位一致 |
| code/NeuralODE_GlobalMemory/ | 132 区域 H 六组；slurm/agent.sbatch 用根目录 global-memory-queue.json |
| code/NeuralODE_Pure/ | 直接输出 du/dt、dh/dt 的纯导数 ODE，无 AR 初始化 |
| code/NeuralODE_Experiments/ | 九组 500×200 正式训练源码；产物 results/neural_ode_full500/ |
| code/NeuralODE_Experiments/evaluate_snapshot.py、compare_snapshot.py | Slurm内冻结当前Pure最佳权重，完整90例测试与测速，并对照历史AR/ODE逐例指标；2026-10-14产物results/neural_ode_full500/evaluation_20261014/，不是500轮完成结果 |
| code/NeuralODE_BoundaryMemory/opnn.py、main.py、real_check.py | Pure 独立副本；内部/有向界面先提取位置与动态特征，再融合进 24 维 H，无独立 E；Slurm 7207 完整网格有限性检查及 7208 最终 23 测试通过；无新正式训练/GPU 测速 |
| code/DATASET/total_generator_normalize_v10.py | 当前二维 CRN 合成数据来源 |
| code/lddmm/ | 历史 MATLAB 几何工具；当前本机没有旧 README 引用的 bridge/ 目录，几何 sidecar 需另核来源 |
| docs/pca/design.md、audit.md | PCA 设计/审查；部分"未拿到数据"描述是当时历史，优先核对当前实现 |
| results/ar/report.md、full/suite.json、audit_20261008/summary.json | 已有实验和诊断证据；阅读相关段，实时状态另核查 |
| slurm/README.md、ar.sbatch、pca.md、pca_p500.sbatch | 服务器部署路径、资源与启动方式；ar.sbatch 使用服务器 code/ar 冻结部署包，与本机 code/TC_GCN_server 不同 |

code/TC+GCN_original 是原版直接轨迹模型；TC+GCN、FNO、V_single、backup_code 和 Original 是其他分支/参考。
不要从相似目录名把它们当作当前服务器主线。dataset/crn 是另一套三维资料，不能套用 v10 读取协议。
两套目录 TC_GCN_server 与 FBNO_time_forecast 均有 main/data/model 同名模块，分进程执行测试，避免导入串线。
