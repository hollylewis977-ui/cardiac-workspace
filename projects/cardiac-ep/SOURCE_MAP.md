# 心脏项目源码索引

核对日期：2026-10-19（本轮更新源码目录与结论记忆；远程状态仍按各历史日期解释）。路径相对 cardiac-workspace.json 的 project_root。数据、协议与命令见 problem.md 与 README.md。
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
| code/visualization/generate_visualizations.py | 正式图：`--npz`读rollout NPZ，按results/ar/plots/calcium.pdf配色（场viridis/误差magma）与紧凑3行类型×3列时刻版式，12×9英寸/300dpi/原始节点，V/Ca分图、物理mV/nM共享显示色标；空间标题为单帧NRMSE（固定150mV/0.0012mM分母，与显示范围分开），整窗值另存metadata；保留三点traces与error对比，核查后覆盖原图。工作台plot-sci任务沿用此入口 |
| NeuralODE/visualizetions/{generate_visualizations.py,plot_snapshot_sci.py}、NeuralODE/slurm/visualizetions.sbatch | 10/22按用户指定名称整合的自包含正式绘图入口；渲染器保留原8个核心函数，批量入口可复用预测或冻结当前configs/models/scripts后导出，跨病例共享色标、逐帧指标核对、三点CSV、可选90test模型比较。交付仅PNG/CSV/量化JSON，源码/日志/预测留独立工作目录；绘制前述calcium.png和traces.png。Slurm7547已核查2例重绘与1例新导出，证据archive/visualizetions_20261022/session_001/，记忆VISUAL-SCI-PORT-001；使用见该目录README。 |
| results/ar/plots/calcium.pdf、code/TC_GCN_server/plot_results.py | provided-source配色/版式参考：真实与预测viridis、物理绝对误差magma、三行类型三列时间；7284实际PDF渲染与原始PDF哈希一致。10/15起预览/引用副本及冻结源码位于archive/neural_ode_full500/evaluation_20261014/plots_sci_20261014/source/；展示结果目录仅保留图和量化 |
| code/visualization/visualize_dataset_dynamics.py | 从 v10 NPZ 直接画单例 V/Ca 动态 |
| code/FBNO_time_forecast/main.py、model.py、data.py | 历史条件直接时间查询；未来预测之间没有回灌 |
| code/FBNO_time_forecast/audit_data.py | 专项全批次头/坐标/初值与部分轨迹核查；比 doctor 更重 |
| code/NeuralODE/ | 2026-10-19 起的统一目录（EMMS 式）：configs/（默认值与 parse_args、data_loader.py、metrics.py）、models/（ar_ode、pure_ode、graph_ode、trainer、latent_ode、codec）、scripts/（run.py 六种 --mode、evaluate_shape.py、train/evaluate_latent.py）、tests/、slurm/、data/、results/；四个 --model：graph_memory_v1、graph_memory、pure、boundary。与整理前各目录对照：新旧代码 18 案例 CPU 训练产物比对通过，细节见 docs/neural_ode/design.md 2026-10-19 节 |
| archive/source_reorganization_20261019/neural_ode_before_unify/ | 整理前 9 个 NeuralODE_* 目录的原样备份（77 文件，sha256 在上级目录）：九组训练运行器 TrainingSuite、快照评估 Snapshot、推理加速 InferenceSpeed、run_suite.py、preflight.py、real_check.py 及旧 sbatch；这些一次性脚本不在活跃 code/ 区 |
| archive/source_reorganization_20261019/neural_ode_before_unify/NeuralODE_Snapshot/evaluate_snapshot.py、compare_snapshot.py | Slurm内冻结Pure最佳权重、完整90例评估及历史模型对照；10/14中途权重结果不是500轮完成成绩 |
| code/NeuralODE_Latent/{codec.py,opnn.py,main.py,evaluate.py}、slurm/{screen,train250}.sbatch | 可复用4096系数+64记忆RecoveryLatentODE、RK4 2ms，40train/3val；7377已完成1000更新。main支持累计epoch目标、恢复优化器/RNG、校验复用缓存与继承best；7440从1000续到50000（250×200），冻结archive/latent_ode_train_20261019/epochs_250_001/，运行中非结果。真实全窗误差/事件和完整推理计时由evaluate给出；重构记忆NODE-LATENT-RECON-001及冻结诊断保留，原一次性脚本仍仅在归档 |
| archive/source_reorganization_20261019/neural_ode_before_unify/NeuralODE_Snapshot/plot_snapshot_sci.py、slurm/snapshot_plot_sci.sbatch | 冻结Pure导出指定病例并调用SCI脚本绘图（`--cases batch_0XX/sampleYY`，默认原两例；sbatch透传额外参数，10/19 Slurm7368用它出了b023_s13）；10/14原结果、预测与指标保持原路径 |
| archive/source_reorganization_20261019/neural_ode_before_unify/NeuralODE_Snapshot/slurm/snapshot_replot_sci.sbatch | 复用已有预测的CPU重绘；600/800/1000ms合图、共享色标与单帧NRMSE |
| archive/neural_ode_full500/evaluation_20261014/plots_sci_20261014/ | 原绘图运行记录归档：source/、predictions/、manifest、logs和调度查询保留；relocation.json记录原路径到当前路径，cleanup_sha256.txt记录全部50文件哈希。重绘--reuse-predictions传此目录，--output-dir使用含source/的独立归档运行区；完成后只发布PNG/CSV/纯量化JSON到results/.../plots_sci_20261014/ |
| archive/dataset_checks/{quiescence_scan_20261019,truth_timeline_20261019}/source/ | 只读memmap v10 NPZ的数据集核查工具（10/19）：scan_quiescence.py扫90例上冲/静息，inspect_case.py打印单例原值，plot_truth_timeline.py画单例0–2000ms真值V/Ca网格与激活曲线；Slurm7374/7376/7380，输出在同目录，不涉及模型 |
| code/NeuralODE/models/pure_ode.py（--model boundary）；real_check.py 在备份目录 | Pure 独立副本；内部/有向界面先提取位置与动态特征，再融合进 24 维 H，无独立 E；Slurm 7207 完整网格有限性检查及 7208 最终 23 测试通过；无新正式训练/GPU 测速 |
| code/DATASET/total_generator_normalize_v10.py | 当前二维 CRN 合成数据来源 |
| code/lddmm/ | 历史 MATLAB 几何工具；当前本机没有旧 README 引用的 bridge/ 目录，几何 sidecar 需另核来源 |
| docs/pca/design.md、audit.md | PCA 设计/审查；部分"未拿到数据"描述是当时历史，优先核对当前实现 |
| results/ar/report.md、full/suite.json、audit_20261008/summary.json | 已有实验和诊断证据；阅读相关段，实时状态另核查 |
| slurm/README.md、ar.sbatch、pca.md、pca_p500.sbatch | 服务器部署路径、资源与启动方式；ar.sbatch 使用服务器 code/ar 冻结部署包，与本机 code/TC_GCN_server 不同 |

code/TC+GCN_original 是原版直接轨迹模型；TC+GCN、FNO、V_single、backup_code 和 Original 是其他分支/参考。
不要从相似目录名把它们当作当前服务器主线。dataset/crn 是另一套三维资料，不能套用 v10 读取协议。
两套目录 TC_GCN_server 与 FBNO_time_forecast 均有 main/data/model 同名模块，分进程执行测试，避免导入串线。
