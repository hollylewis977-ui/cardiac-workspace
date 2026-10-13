# 心脏项目源码索引

核对日期：2026-09-16。路径相对 cardiac-workspace.json 的 project_root。
2026-10-10 增量：区域内部/边界融合记忆分支已实现并通过 Slurm 检查，见下表。
以下为当前本机源码事实；历史文档和远程任务状态不能替代本次核验。

## 主要入口

| 路径 | 作用与适用场景 |
|---|---|
| code/TC_GCN_server/main.py | inspect/train/rollout/evaluate/fit-pca/diagnose-pca；AR 与低维 PCA 共用训练评价 |
| code/TC_GCN_server/model.py | ReferenceOperator（GRU+图传播的一步算子）；FixedPCACodec、PCALatentOperator |
| code/TC_GCN_server/data.py | NpzBatch 内存映射、Scaler、参考图、可选几何 sidecar、数据切分 |
| code/TC_GCN_server/ar_experiments.py | 7 组 AR 消融、smoke、train、diagnose、suite；oracle 诊断需与自主预测区分 |
| code/TC_GCN_server/run_pca.py | 固定 PCA256+256、GRU256 或无记忆 MLP、混合展开 16/32/64/128/192 |
| code/TC_GCN_server/neural_ode.py、run_neural_ode.py | 独立 PCA 系数/隐特征 ODE；0–1000 ms 监督、502–1000 ms 验证选模，区别于严格 ≤500 ms AR 消融；本轮只核查，见 AR-ODE-001 |
| code/TC_GCN_server/quantify_results.py、plot_results.py | 固定权重量化和 PNG 图 |
| code/FBNO_time_forecast/main.py、model.py、data.py | 历史条件直接时间查询；未来预测之间没有回灌 |
| code/FBNO_time_forecast/audit_data.py | 专项全批次头/坐标/初值与部分轨迹核查；比 doctor 更重 |
| code/NeuralODE_BoundaryMemory/opnn.py、main.py、real_check.py | Pure独立副本；内部/有向界面先提取位置与动态特征，再融合进24维H，无独立E；Slurm7207完整网格有限性检查及7208最终23测试通过；无新正式训练/GPU测速 |
| code/DATASET/total_generator_normalize_v10.py | 当前二维 CRN 合成数据来源 |
| code/lddmm/ | 历史 MATLAB 几何工具；当前本机没有旧 README 引用的 bridge/ 目录，几何 sidecar 需另核来源 |
| docs/pca/design.md、audit.md | PCA 设计/审查；部分“未拿到数据”描述是当时历史，优先核对当前实现 |
| results/ar/report.md、full/suite.json | 已有实验和诊断证据；阅读相关段，实时状态另核查 |
| slurm/README.md、ar.sbatch、pca.md、pca_p500.sbatch | 服务器部署路径、资源与启动方式 |

code/TC+GCN_original 是原版直接轨迹模型；TC+GCN、FNO、V_single、backup_code 和 Original 是其他分支/参考。
不要从相似目录名把它们当作当前服务器主线。dataset/crn 是另一套三维资料，不能套用 v10 读取协议。

## v10 的数据与物理边界

- 本机数据：dataset/750sample/batch_v10/data/batch_000.npz 到 batch_024.npz。
- u/ca 是 V/Ca，常见 shape=[30,1001,43573]、float16。x_uni/x_mesh 的节点下标对应，不再重排。
- 默认切分：20/2/3 个完整文件，600/60/90 个合成样本。750 例的 0–500 ms 观测历史无精确重复，见 AR-DATA-002；近重复、样本独立性及所有值的质量仍未认证。
- CRN 类 Courtemanche1998 的 NEQ=21，full_init 保存完整初值；V 位于索引 0，Ca_i 位于 18。
- simulate_200ms_and_sample 实际 total_ms=2000、dt=0.02 ms、sample_interval_ms=2；名称和“41 帧”注释过时。
- 演化使用 ref_nm 的邻居差分及 CRN 反应；grid 参数未进入公式，x_mesh 形变不改变该版动力学。
- 实际扩散系数 D=0.08，和邻近注释推算不一致。不能从注释宣称已达到某个传导速度。
- 生成器先做扩散、裁剪 V 再离子步进；修改物理模型需记录这一离散与裁剪，重新验证。
- 冻结 AR 与生成器的距离规则相同，但 cKDTree/KDTree 默认 leafsize=16/10 的等距选边在 7,405 节点不同（边的 2.43%）；本地与服务器已核对，检查进程设 leafsize=10 在当前网格匹配生成器。正式图未改，见 AR-GRAPH-001。
- 500 ms 单细胞模板用于初始相位，不表示二维场必然每 500 ms 周期复制。

这些是源码检查结论。doctor 只读 NPZ 头，不能验证完整 PDE、空间收敛或个体化能力。

## 时间、模型与结果协议

AR：输入截至 500 ms（251 帧），共享 2 ms 一步算子预测 502–1000 ms（250 步）。
history_steps 控制梯度历史尾部，不等于只看最后这些帧；GRU 隐状态不是测得的完整离子状态。
main.py 默认训练目标止于 500 ms；--supervision-end-ms 1000 扩大训练标签范围。
默认验证使用 500–1000 ms；--strict-validation 使用 100/250/400 ms 锚点、目标止于 500 ms。
因此“训练标签未过 500 ms”和“选模也未过 500 ms”必须分别写。

PCA：分通道固定空间基底编码/仿射解码，联合 V/Ca 系数与全局 GRU 推进。
run_pca.py 核对训练文件、9600 个拟合快照、fit_end_ms=500、每通道 rank=256；
默认 negative_ca 软约束、feedback_clamp=False、strict_validation=True。
几何 PCA 特征与动态 V/Ca PCA 是不同对象，不混用基底。拟合/重载先核查清单、归一化和节点哈希。

Direct：历史编码后直接查询未来，默认训练监督至 1000 ms。
--supervision-end-ms 500 仅限制梯度标签；该入口当前没有 --strict-validation 开关。
若要严格时间外推开发协议，必须另实现许可窗口选模或预固定 epoch，不能借用 AR 参数。
它借用参考域直接算子思想，没有实现完整 FBNO 的自由边界 H 或 CRN PDE 残差。

Scaler：V [-100,50] mV，Ca [0,0.0012] mM。NRMSE 固定分母 150 mV/0.0012 mM。
主要指标：全域/活动区 V、Ca NRMSE；persistence；首次激活漏检/误检、匹配数、时间 MAE；
必要时补再次激活与复极。无匹配时 MAE=0 不是准确，已知 500 ms 帧不计未来误差。
clamp 策略必须从权重/代码核实，不能把旧 AR、PCA 与 Direct 当作相同处理。

## 可执行命令

在工作台根目录，环境依赖存在时：

```powershell
python tools/cardiac_workspace.py doctor
python tools/cardiac_workspace.py run server-tests
python tools/cardiac_workspace.py run direct-tests
python tools/cardiac_workspace.py run inspect-data
python tools/cardiac_workspace.py plan smoke-ar
python tools/cardiac_workspace.py run smoke-ar
```

也可在实际项目根目录独立运行两套测试，各用一个 Python 进程：

```powershell
python -B -m unittest discover -s code/TC_GCN_server -p "test_*.py" -v
python -B -m unittest discover -s code/FBNO_time_forecast -p "test_*.py" -v
python code/TC_GCN_server/main.py --help
python code/TC_GCN_server/run_pca.py --help
python code/TC_GCN_server/ar_experiments.py --help
```

正式 PCA 运行需现有基底及数据；不得因缺基底自动重拟合覆盖。
Slurm ar.sbatch 使用服务器 code/ar 冻结部署包，与本机 code/TC_GCN_server 不同；
它的 #SBATCH --time=0 也不是本地 smoke 的预算。先核查当前包/数据/作业，再提交已授权工作。

## 已知环境与后续个体化路线

本次发现本机 Python 3.14.0、PyTorch 2.10.0+cu128、NumPy 2.3.5、SciPy 1.16.3，CUDA 可用；
每次执行需再次读取环境，服务器环境另查。不引入 graphlab/Lean/Rethlas。
当前实际源码存在用户未提交修改；本适配不覆盖它们。

近期完成基线、可靠评价和消融；后续再按用户目标引入会影响动力学的几何、纤维、
导电/离子/刺激参数、观测噪声与校准。先定义可识别参数和独立验证数据，
不能把合成初值条件预测自动称为患者数字孪生。

## Neural ODE 原始网格分支（2026-09-17）

`code/TC_GCN_server/graph_neural_ode.py`：连续 V/Ca/h，含局部反应候选和 AR 权重初始化的连续记忆候选。
原 `main.py` 支持这两个模型类型；仅其训练历史锚点额外封顶 500 ms，未来监督按用户授权可至 1000 ms。
`verify_graph_ode.py` 检查真实网格、步长、标签遮蔽、重载，可做无优化更新的完整反向检查。
`evaluate_graph_ode.py` 复用原场/事件指标并生成配对 AR 自由预测；`analysis/scripts/graph_ode_pilot.py` 设置本地硬时限。
设计在 `docs/neural_ode/design.md`；记录在 `results/neural_ode/session_20260916`，与严格 AR 消融分开。
旧 `neural_ode.py`/`run_neural_ode.py` 的 PCA 原型仍保留；不能用旧部署脚本自动提交当前图模型。
