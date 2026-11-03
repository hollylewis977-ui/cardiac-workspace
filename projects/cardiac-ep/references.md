# 文献与架构对照表

来源标签：internal / provided-source / web-source。阅读状态：read / abstract-only / GAP。核查记录见项目 results/ar/analysis/summary.json: ar_physics_literature（2026-09-16）。

| 方法 | 论文或代码 | 对象层级 | 状态与观测 | 算子类型 | 时间处理 | 几何处理 | 训练数据规模 | 指标 | 与本项目差异 / 可借鉴 | 来源 | 阅读状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Buoso2021 参数化心肌力学PINN（2026-10-27写作核查） | [正式论文](https://doi.org/10.1016/j.media.2021.102066)，PMID33951597；[作者代码](https://github.com/sbuoso/Cardio-PINN)；原PDF位于项目paper/3.2.1_LDDMM补写/引用论文/Buoso_2021_Cardiac_Parametric_PINN_PMID33951597.pdf | 三维左心室 | 输入心内膜压力p_endo、预设主动应力Ta，输出位移；不联立求解电压和钙传播 | Dense网络预测POD位移系数，固定投影层；势能训练 | 准静态条件映射，结合预设活化时程与简化循环模型推进心动周期 | 75例影像形状模型；每种个体几何需重新训练相应PINN | 100个合成几何、每例30帧用于构造位移基；每个PINN以400组压力/主动应力输入训练 | EF、峰值收缩压、每搏功、应变；本轮不复核性能数值 | 可借用正式原文式(6)势能目标；原文HO本构和体积惩罚不等同Guccione混合压力形式，CaT/Land驱动及心房应用为项目拟扩展。不能把已有电压钙预测或跨几何通用模型能力归于该文 | web-source | read：正文§2.2–2.3、§3.2；打印页3–5/仓储PDF4–6原式逐页查看，作者CardioLoss只读未运行；记录archive/editorial_20261027/v7_buoso2021_audit.json |
| DIMON | 项目 docs/（原仓库 DIMON 参考资料） | 组织 | 参考域场 | DeepONet 类 | 参数化时间查询 | 微分同胚映到参考域 | 见原文 | 场误差 | 本项目参考域思想来源；无时间窗外推 | provided-source | read |
| DIMON 几何框架与预测网络解耦（2026-10-22核查） | [原文PDF](https://d-nb.info/1358331472/34)，doi:10.1038/s43588-024-00732-2 | 通用PDE/心脏组织 | 各几何上的输入与输出函数，统一搬到参考域 | 文中采用MIONet；框架允许选择其他神经算子 | 原文含时间依赖算子；不等同本项目历史条件外推 | 微分同胚、几何条件、预测后回映；同一参考域上的算子仍依赖原几何 | 本轮未逐项摘录（GAP） | 本轮仅核查框架，未摘录误差/耗时数值 | 可保留DIMON外层，以几何条件Neural ODE学习0–500→502–1000ms；这是本项目提案，尚未实现或验证，不能直接继承原MIONet定理。当前v10几何不进入动力学，不能据此认证未见几何泛化 | web-source | read：Problem formulation式1、Fig.1、网络选择段及Laplace变换式3；仅上述框架部分 |
| FBNO | code/FBNO_time_forecast（借用思想） | 组织 | 自由边界 H | 参考域直接算子 | 直接查询 | 自由边界 | 见原文 | 场误差 | 本项目未实现完整自由边界 H 与 CRN 残差 | provided-source | abstract-only |
| 可微心脏电生理仿真（状态与参数估计） | Differentiable Cardiac Electrophysiology Simulations for Dynamical State and Parameter Estimation，arXiv 2607.15492 v1（2026-07-16），https://arxiv.org/html/2607.15492v1；本地 docs/papers/differentiable.pdf | 组织 | AP/MS 恢复状态，观测窗内估计后自由演化；钙成像作电压代理 | 可微物理模型拟合 | 连续 | 固定 | 见原文 | 场误差 | 支持"状态估计"候选，不是 CRN 代理；逐例拟合不同于共享预训练 AR（AR-LIT-001） | web-source | read（II.1、II.3.3-5、III.2、III.7、图 5-6、17） |
| 高维离子模型 FNO | Learning high-dimensional ionic model dynamics using Fourier Neural Operators，2025-12-08，https://link.springer.com/article/10.1007/s44379-025-00046-8；代码 https://github.com/MaxGhi8/HyperNOs；数据 https://doi.org/10.5281/zenodo.14865789 | 单细胞 | 电流函数 → 完整离子轨迹（含 41 态 ORd），全分量监督 | FNO | 自回归/算子 | 无 | 见原文 | 轨迹误差 | 细胞 ODE 算子；本项目是部分观测空间预测、≤500 ms 监督 | web-source | read（第 2 节式 1-3、3.1、Limitations、附录 A.3、B） |
| 全心电机械 Latent Neural ODE | Whole-heart electromechanical simulations using Latent Neural Ordinary Differential Equations，npj Digit. Med. 2024-04-11，https://www.nature.com/articles/s41746-024-01084-x；索引全文 https://pmc.ncbi.nlm.nih.gov/articles/PMC11009296/ | 全心 | 压力容积 | Latent Neural ODE | 连续 | 无 | 见原文 | 时间序列误差 | 学压力容积动力学而非 V/Ca 场；隐空间思想对应本项目 Neural ODE 分支 | web-source | abstract-only（出版社摘要与索引的方法/讨论节选，整页访问失败） |

联网调研回合按 agents/protocols/literature-check.md 追加行；没读到原文的行阅读状态保持 GAP。

## 2026-10-15：Pure 推理速度与低维动力学

研究者授权联网；完整源码映射、数学限制与实验卡在项目 `docs/neural_ode/design.md` 的同日章节。以下均为外部文献事实，不是本项目的新预测或加速结果。

| 方法 | 论文或代码链接 | 对象层级 | 状态与观测 | 算子类型 | 时间处理 | 几何处理 | 训练数据规模 | 指标 | 与本项目差异和可借鉴点 | 来源标签 | 阅读状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Latent ODE | [Rubanova等，NeurIPS2019](https://proceedings.neurips.cc/paper_files/paper/2019/file/42a6845a557bef704ad8ac9cb4461d43-Paper.pdf) | 通用时序，非心脏 | 历史推断初始latent，解码观测 | 概率Latent ODE | 连续 | 无心脏几何 | 多数据集，逐集规模本轮未摘录GAP | 重建/外推/分类 | 分离历史推断、低维RHS与解码；不必照搬ODE历史编码器或概率模型 | web-source | read，§3.2式5–9、实验 |
| LDNet | [Regazzoni等，Nat Commun2024](https://www.nature.com/articles/s41467-024-45323-x)；[SI](https://media.springernature.com/original/springer-static/esm/art:10.1038%2Fs41467-024-45323-x/MediaObjects/41467_2024_45323_MOESM1_ESM.pdf) | 心肌组织1D/2D及其他PDE | AP两变量真值，代理输出电势、全局latent | Neural ODE+坐标解码 | 连续，固定Euler | 固定域，解码器按坐标查询 | 1D100训练/100测试；2D200训练验证/75测试 | 归一化场误差、推进与重建分项时间 | 低维推进不调用细网格；原版固定初值，未做CRN/Ca；全场解码仍有成本 | web-source | read，架构、心脏结果、Methods、SI§3.3–3.4 |
| IC-LDNet | [Pizzamiglio等，2026-10-06预印本](https://arxiv.org/html/2610.08475v1) | ADR/流体/固体，无心脏 | 早期观测适应初始latent | Latent ODE，auto-decoder/meta-learning | 连续，Euler | 坐标解码，不依赖固定输出网格 | ADR800/100/100；其他任务逐项见正文 | 场误差、逐例推理时间（含初态适应成本） | 对应变化初态缺口；逐例优化可能慢；encoder版仅讨论未实现，不能照搬为已验证心脏方法 | web-source | read，§2.4–3、Tables1–2 |
| POD-DL-ROM | [Fresca等，Front Physiol2021](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.679076/full) | 组织/理想左房 | AP或R-M简化模型，跨膜/胞外电势 | POD+非线性decoder+参数映射 | 参数/时间直接查询 | 固定理想左房 | Test2为18训练参数×200时刻、14测试；各测试不同 | 场误差、激活图、全流程成本 | 支持非线性波前表示；已知参数输入不同于本题历史推断，未验证CRN/Ca | web-source | read，Methods、Tests1–3、Discussion |
| Whole-heart LNODE | [Salvador等，npj Digit Med2024](https://www.nature.com/articles/s41746-024-01084-x) | 全心电机械，代理为集总输出 | 四腔压力/容积8态，最终无额外latent | 参数条件Neural ODE | 连续，第5心动周期 | 同一患者解剖 | 400训练验证、10折；5独立测试；43参数 | 压力/容积、敏感性与反演 | 更新上方abstract-only记录：本轮读正文；不是V/Ca全场，不能引用其加速倍数作本项目承诺 | web-source | read，Results、Methods、Discussion |
| Neural Flows | [Biloš等，NeurIPS2021](https://proceedings.neurips.cc/paper_files/paper/2021/file/b21f9f98829dea9a48fd8aaddc1f159d-Paper.pdf) | 通用时序/刚性玩具ODE | 时间条件latent解映射 | Flow | 直接查询，无积分循环 | 无心脏几何 | 多时序数据集，逐集规模本轮未完整摘录GAP | 时序误差、分类、训练时间 | 可作低维学生/速度对照；不自动满足自治半群；未证明心脏窗口外泛化 | web-source | read，§2、§4 |
| 向量场正则 | [Finlay等，ICML2020](https://proceedings.mlr.press/v119/finlay20a/finlay20a.pdf) | 通用生成模型 | 流状态、Jacobian/kinetic约束 | Neural ODE | 连续、自适应积分 | 无 | MNIST/CIFAR等，精确样本数未摘录GAP | 似然、NFE、训练时间 | 固定1ms/RK4不会自动降NFE；心脏上升沿可能被过正则；Jacobian估计并非免费 | web-source | read，§3–5、Algorithm1 |
| 求解器依赖诊断 | [Ott等，ICLR2021](https://arxiv.org/pdf/2007.15386) | 合成动力学/分类 | 训练所得向量场与离散积分组合 | Neural ODE数值分析 | 多solver/步长 | 无 | 合成集与图像分类，规模未摘录GAP | 换solver性能、步长敏感性 | 必须在同权重上验证数值法，精细solver也可能揭示训练对离散误差的依赖 | web-source | read，正文数值方法与跨solver实验 |
| ODE模型降阶 | [Lehtimäki等，2021预印本/2022online/2024卷期](https://arxiv.org/pdf/2105.14070) | 分类网络，非心脏 | 高维NODE状态→POD/DEIM | 降阶Neural ODE | 连续 | 无 | 小型分类任务，逐项规模未摘录GAP | CPU加速、分类准确率 | 只压状态仍调用全维f可能无主要收益；本题应直接学低维RHS；未验证GPU心脏加速 | web-source | read，§III.B、§IV–V |

当前建议为项目推断：先区分18.7分钟完整评估与3.518秒纯网络；固定权重做RK4/Heun消融，再以已有PCA512+64作为诊断对照，优先探索保留传播结构的多尺度latent ODE。没有运行这些实验，不宣称新性能、稳定性或新颖性。

## 同日续：训练与推理同时提速的替代框架

本轮优先级因用户增加训练成本目标而调整：先比较直接latent时间查询与小latent离散推进，连续ODE保留对照。以下是文献机制；本项目适配均planned，无新实验。

| 方法 | 论文或代码链接 | 对象层级 | 状态与观测 | 算子类型 | 时间处理 | 几何处理 | 训练数据规模 | 指标 | 与本项目差异和可借鉴点 | 来源标签 | 阅读状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepONet | [Lu等2021](https://www.nature.com/articles/s42256-021-00302-5)；[作者预印本](https://arxiv.org/pdf/1910.03193) | 通用函数/反应扩散，非心脏 | 输入函数branch→位置/时间trunk | 直接算子 | query监督，无ODE/长unroll要求 | 示例规则域 | 预印本反应扩散100输入函数×1000查询；非10万独立轨迹 | 点值误差/数据效率 | 历史branch与潜态query可去长链；正式版实验变化未逐项核查GAP | web-source | read，预印本架构、§4.3；不声称正式版全读 |
| Poseidon | [Herde等2024](https://arxiv.org/html/2405.19101v2) | 多PDE，无心脏 | 状态快照/lead time | 时间条件Swin算子 | all2all pair训练，direct/AR推理 | 规则网格 | 77840预训练轨迹×11帧；21M/158M/629M模型 | 测试误差/迁移样本效率 | 借随机pair不借大模型；V/Ca需历史而非单帧闭包；穷举pair成本T² | web-source | read，§2式5–8、SM D.6.1–2 |
| UPT | [Alkin等NeurIPS2024](https://arxiv.org/html/2402.12365v5) | 流体/粒子，无心脏 | 场→supernodes→少量latent | 离散latent Transformer | latent-only rollout | 稀疏radius聚合、坐标解码 | 流体8000/1000/1000轨迹，约29–59K点→2048 supernodes→512tokens | 轨迹误差、推理与训练成本 | 避免细图反复推进；原训练有额外decode/re-encode，不保证训练快；需补历史 | web-source | read，§3–4、A/D.5/F.4 |
| RIGNO | [2025正文](https://arxiv.org/html/2501.19205v2) | 多PDE/固流体，无心脏 | 细点→区域图→细点 | 多尺度图lead-time算子 | pair/all2all，direct/AR | regional支持域、多级边 | 通常1024/128/256、13任务，各任务有差异 | 不同推理路径误差、训练时间 | 原版非latent-only；原边不自动尊重绝缘孔洞；固定域训练未必快于GINO | web-source | read，§2、SM A/C/E/F.10 |
| GINO | [2023原稿](https://arxiv.org/html/2309.00583v1) | 稳态车辆气动，非心脏 | SDF/几何→压力 | GNO+FNO | 原任务稳态 | 不规则→规则latent grid→查询 | Ahmed500训练/51验证 | 压力/阻力及CFD成本 | 只借规则latent骨架，不把稳态速度转成250帧预测保证 | web-source | read，原稿§3–4 |
| S4 | [Gu等ICLR2022](https://arxiv.org/pdf/2111.00396) | 通用序列，非心脏 | 结构化线性状态空间 | SSM | recurrent/并行卷积等价 | 无空间图定义 | 长序列多任务，逐集样本数本轮未摘录GAP | 序列误差、吞吐 | 适合压缩历史时间编码；不自动解决空间传播/未来闭包 | web-source | read，§2.3–2.4、§3 |
| Mamba | [Gu与Dao2023/2024](https://arxiv.org/html/2312.00752v2) | 语言/音频/DNA，无心脏 | 输入条件化离散SSM | selective SSM | 融合parallel scan，非LTI卷积 | 无图拓扑 | 多任务，语言规模非本题；逐集样本数GAP | 吞吐/显存、序列指标 | 优先压缩后替换时间encoder；251帧收益待测；AR未来仍有依赖 | web-source | read，§3.2–3.3、§4.5、附录D |
| LaMO | [Tiwari等ICML2025](https://proceedings.mlr.press/v267/tiwari25a.html)；[全文](https://arxiv.org/html/2505.19105v2) | 固体/流体，无心脏 | 场→latent tokens双向SSM→场 | latent Mamba operator | 算子/序列映射，非自动latent-only rollout | 网格/点云 | NS1000训练/200测试，64²点、10→10帧 | 场误差、训练/推理成本 | 空间token扫描不同于251帧历史预测，不能把Mamba名称当心脏性能证明 | web-source | read，§3、D/E/G |
| Koopman线性嵌入 | [Lusch等2018](https://www.nature.com/articles/s41467-018-07210-0) | 经典非线性动力系统，无心脏 | 非线性编码+线性latent+解码 | Koopman近似 | K^m多步 | 无心脏几何 | 多个合成系统，逐集规模未摘录GAP | 重建、线性一致性、多步误差 | 有限维线性闭包非自动成立；历史初始化、解析块推进是项目方案 | web-source | read，正文及补充网络/损失 |
| Flow Matching | [Lipman等ICLR2023](https://arxiv.org/html/2210.02747v2) | 生成模型，无心脏 | 噪声/目标样本与路径速度 | 连续生成流 | 训练simulation-free，推理仍ODE | 无 | ImageNet128示例500k迭代、batch约1.5k | 生成质量、NFE | 不等于一步推理；生成时间非物理毫秒，不优先用于确定性双加速 | web-source | read，§3–4、§6.2 |

## 2026-10-17：现有权重加速调研

范围为冻结 epoch246 PureGraphODE，不重训、不改归一化与图权重。历史 `archive/neural_ode_results_reorg_20261102/NeuralODE/results/ode_pure/eval/inference.json` 的3.518秒纯网络基准来自RTX4090、PyTorch 2.11.0+cu130、CUDA13、float32、matmul `highest`、TF32 matmul关闭；它已使用 `model.eval()` 与 `inference_mode`，不能重复计作开关收益。本轮主代理核实的本地环境为Windows、RTX5070 Laptop 8GB、Python3.14、PyTorch 2.10.0+cu128、CUDA12.8；用户随后明确授权“请在本地实验”，本任务本地实验按该授权执行。以下官方链接据此改用2.10，须先在本机建立同权重原RK4基线，不能把历史4090耗时当本机基线或混合计算加速比。下表为文档机制与项目适配推断，不代表已取得实测收益；P1先核查实现与评估开销，P2再测同离散模型的执行后端，P3属于允许数值变化后才考虑的近似。

| 做法 | 能否完全保持数值 | 本项目适用条件与限制 | 原始来源、阅读范围 | 优先级 |
|---|---|---|---|---|
| 全量评估采用 `eval()` + `inference_mode()` | 不改变求解公式或dtype，目标为逐位一致；仍须实测 | 比 `no_grad` 额外省view tracking/version counter；不自动设置eval。历史纯网络基准已启用，本机收益按相同路径另测；产生的tensor不再送入训练autograd | [官方inference_mode](https://docs.pytorch.org/docs/2.10/generated/torch.autograd.grad_mode.inference_mode.html)，read API及警告，web-source | P1 |
| 输出只保存V/Ca副本或预分配写入，释放全隐态引用 | 相同dtype的直接复制可保留场值；以逐位一致验收 | `state[..., :2]` 是共享底层storage的view；保存250个view可能保留250份66维状态。clone或copy只保留2维场，推进与RK4运算顺序保持不变；不能用detach代替复制 | [官方Tensor Views](https://docs.pytorch.org/docs/2.10/tensor_view.html)、[clone](https://docs.pytorch.org/docs/2.10/generated/torch.clone.html)，read storage语义，web-source；占用推断来自项目源码 | P1 |
| 复用一次D2H后的数组，复用指标中间量，流水处理CPU指标/绘图 | 复制复用可保留预测；指标须保持dtype及运算定义 | 避免case_report与shape_metrics重复搬运同一全场；异步copy必须在CPU读取前等待完成并保持buffer寿命。单纯non_blocking不保证重叠；分别报告网络、搬运、指标与全90例墙钟 | [官方CUDA异步执行与streams](https://docs.pytorch.org/docs/2.10/notes/cuda.html#asynchronous-execution)，read 对应章节，web-source | P1 |
| 固定邻接矩阵一次性COO→CSR，继续 `sparse.mm` | 数学相同，不能保证逐位一致 | 2.10支持COO/CSR；保留已coalesce的索引与数值，仅在建图时转换，不能每次RHS转换。CUDA SpMM是否更快取决于稀疏结构与B×C宽度；文档的CSR优势不能当本任务加速保证；核查全500ms累积偏差 | [官方sparse.mm](https://docs.pytorch.org/docs/2.10/generated/torch.sparse.mm.html)、[浮点准确性](https://docs.pytorch.org/docs/2.10/notes/numerical_accuracy.html)，read API与非结合性说明，web-source | P2，低改动先测 |
| 相同图的病例batch，共享邻接矩阵 | 独立病例的数学不变；batch与逐例浮点结果不保证相同 | 现graph_mean已将B×C展平后做共享图SpMM，无需复制图；本机8GB先测B=1/2，B=4仅在显存允许时测，先修复隐态view滞留。比较cases/s与完整评估吞吐，同时核查尾batch与每例顺序；不能用单batch延迟当单例时间 | [官方Batched computations](https://docs.pytorch.org/docs/2.10/notes/numerical_accuracy.html#batched-computations-or-slice-computations)，read 对应章节，web-source；展平机制来自项目源码 | P2 |
| `torch.compile` 编译可支持的RHS或单步区域 | 不主动换solver；融合/归约可能改变舍入，不能承诺逐位一致 | 本机编译后端及稀疏路径兼容性为GAP，先诊断graph break；不要先假定500步整段可编译。`fullgraph=True`可用于暴露断图；`reduce-overhead`借CUDA graphs、可能额外占显存且不保证适用。冷编译/预热与稳态90例时间分列 | [官方torch.compile](https://docs.pytorch.org/docs/2.10/generated/torch.compile.html)，read 参数、modes与限制，web-source | P2，兼容后测 |
| 原生CUDA Graph捕获固定形状的RK4单步或短块后replay | 重放kernel可保持公式；仍须核查捕获前后差异，稀疏算法不一概保证逐位确定 | 主要省CPU提交，不减少2000次RHS；需静态shape/control、稳定地址、侧stream预热，捕获内不能CPU同步。CUDA12.8 cuSPARSE明确支持SpMM capture，但不代表PyTorch2.10整条sparse.mm路径已保证；固定并预先coalesce/转换邻接，在本机先小块验证捕获及replay，不能在捕获内重建图；8GB慎用整500步捕获 | [官方CUDA Graphs](https://docs.pytorch.org/docs/2.10/notes/cuda.html#cuda-graphs)、[cuSPARSE12.8 SpMM](https://docs.nvidia.com/cuda/archive/12.8.0/cusparse/index.html#cusparsespmm)，read API、constraints、partial capture与SpMM properties，web-source | P2，确认CPU提交占比后 |
| `set_float32_matmul_precision('high')` 或TF32 | 否；输出仍float32也不代表内部精度相同 | 2.10的high可选TF32或两个BF16展开算法，快算法不可用时退回highest，不能把high等同固定TF32。主要可能加速dense Linear/GRU相关矩阵乘，稀疏乘收益另测；先保留highest基线，验证全窗V/Ca与事件；不要混用新fp32_precision与旧allow_tf32设置 | [官方TF32与新旧接口](https://docs.pytorch.org/docs/2.10/notes/cuda.html#tensorfloat-32-tf32-on-ampere-and-later-devices)、[matmul precision](https://docs.pytorch.org/docs/2.10/generated/torch.set_float32_matmul_precision.html)，read 对应章节/API，web-source | P3 |
| RK4 1ms→2ms，或更换Heun/自适应solver | 否；相同权重不代表相同离散预测器 | 改变数值流及累计误差；输出2ms间隔不等于原内步2ms。先以验证病例比较原1ms、候选与更细参考的全窗误差/非有限值/激活和复极事件，再定方案；更精细solver也不保证预测更准。文献为合成分类/CIFAR10，不能直接断言本心脏模型失效 | [Ott等，ResNet After All? ICLR2021](https://arxiv.org/pdf/2007.15386)，read §2–3及跨solver结果，web-source | P3，明确近似消融 |

验收区分“预测逐位一致”“仅浮点小差异”“改变离散解”三类。冻结权重哈希、原RK4 1ms与训练统计作为基线；候选先在验证集定配置，再固定方案核查90例，不能用测试误差反复选速率/精度阈值。同步计时或CUDA events计时，预热与稳态分开；本次本地实验依据用户新授权执行，须与历史4090/254服务器结果分列。cuSPARSE的capture支持与逐位确定性是不同性质，后者依具体算法，不能以捕获成功代替一致性核查。本表只提供证据与待测优先级，不承诺速度倍数。

### 同日续：RK4宏步与2ms稠密输出

这是已知数值技术，可保留冻结权重与同一ODE向量场，但改变离散解，属于P3数值近似、planned，必须先val，不作新颖性或无损加速宣称。

| 原始来源 | 正文直接支持 | 对本项目的适用边界 | 阅读状态 |
|---|---|---|---|
| [Bianco、Puppo、Russo，SIAM J Sci Comput21(1999)294–322](https://math.umd.edu/~tadmor/centpack/publications/files/BPR3.SISSC99-centpack.pdf) | §2.4.1、式(2.25)、p302–303给出RK4的三次NCE系数，称其order three；复用4阶段，每宏步仍4次f | 经典RK4三阶连续延拓有原始正文依据；不是四阶连续延拓，也不能将RK内部stage状态直接当中间时刻解 | web-source，read 指定章节；原任务为守恒律，非心脏 |
| [Qiu、Shu，J Comput Phys183(2002)187–209](https://www.math.umd.edu/~tadmor/centpack/publications/files/Qiu_Shu_central_WENO_JCP02-centpack.pdf) | §2、式(2.12)后、p195–196列出同一公式；从精确步初值出发，区间内函数值误差为O(H^4)，端点等于RK4更新 | 这里的O(H^4)是单区间插值误差，不能把它写成四阶连续方法所需的局部O(H^5)，也不能据此断言本模型4/8ms足够准确 | web-source，read 指定正文与参考文献 |

以上论文把NCE理论追溯到[Zennaro，Math Comp46(1986)119–133](https://doi.org/10.1090/S0025-5718-1986-0815835-1)；本轮该文全文获取失败，标GAP，不把未读全文当作系数的独立核验。

设H为宏步、θ=(t−t_n)/H∈[0,1]，k_i为原经典RK4的4个RHS斜率（未乘H），则

\[
\widetilde y(t_n+\theta H)=y_n+H\sum_{i=1}^4 b_i(\theta)k_i,\quad
b_1=\theta-\tfrac32\theta^2+\tfrac23\theta^3,\quad
b_2=b_3=\theta^2-\tfrac23\theta^3,\quad
b_4=-\tfrac12\theta^2+\tfrac23\theta^3.
\]

这些系数在θ=1恢复(1/6,1/3,1/3,1/6)。项目实现推断：宏步只推进完整66维状态一次，再按θ保存V/Ca；因场输出是线性切片，可仅插值y_n与k_i的2维场，避免逐输出重建66维隐态。保存的插值值不反馈为下一宏步初值；下一步使用完整RK4端点。沿用原时间单位与归一化，H不能直接替换输出间隔变量。

500–1000ms的计算量推算：H=4ms时125宏步、500次RHS，查询θ=1/2、1；H=8ms时62个8ms步加末尾4ms步，共63宏步、252次RHS，完整步查询θ=1/4、1/2、3/4、1。相较原1ms的2000次RHS，减少的是向量场调用，稠密输出的线性组合、历史编码和评估成本仍存在；这些计数不等于墙钟加速倍数。

稠密输出不扩大RK4稳定域，也不能修复宏步跨过快速上升沿的误差；某些b_i可为负，不能保证Ca正性或无过冲。应先固定权重在验证病例比较1/2/4/8ms、全部250帧V/Ca误差、峰值、激活/复极事件和非有限值，分清宏步端点与区间内部的误差；必要时更细步仅作数值收敛诊断，不能代替数据真值。该方案不需要重训，但是否满足当前低误差目标仍是实测GAP。本轮仅查文献、编辑本表，未执行代码或占用GPU。

### 同日续：同一Neural ODE向量场的求解器替换

术语核查：Adams属于ODE求解器；[Adam](https://docs.pytorch.org/docs/2.10/generated/torch.optim.Adam.html)与[AdamW](https://docs.pytorch.org/docs/2.10/generated/torch.optim.AdamW.html)属于梯度优化器（web-source，read官方参数与更新公式），不能直接替换RK4。冻结Pure源码main.py:490已经使用torch.optim.AdamW；本轮固定权重推理不执行optimizer.step，因此不改变训练优化器。

本轮按用户要求保留Neural ODE，不替换为直接预测器。固定历史编码初值、图与epoch246参数，令z=(V,Ca,h₆₄)，仍求解 `z(t)=z(500)+∫₅₀₀ᵗ fθ(s,z(s))ds`；更换的是积分近似。此分离来自[Chen等NeurIPS2018正文式(3)及§6](https://proceedings.neurips.cc/paper_files/paper/2018/file/69386f6bb1dfed68692a24c8686939b9-Paper.pdf)（web-source，read）。已有权重是否依赖原经典RK4的1ms离散化，仍须按上文Ott研究做验证；更精细积分不等于更准确预测。主代理通报联合2ms/CSR/high方案验证退化，因此先独立比较原COO/highest下的RK4 1/2ms，再固定1ms分别切换CSR和精度，不能把联合差异全归因于步长。以下优先级为本轮求解器试验顺序，不表示已经通过val。

| 路线 | 同一fθ下的近似及函数调用量 | 稳定性与工程限制 | 可复用原始来源与阅读范围 | 优先级 |
|---|---|---|---|---|
| 自适应Dopri5(5/4) | 共享阶段求z⁽⁵⁾、z⁽⁴⁾，e=z⁽⁵⁾−z⁽⁴⁾，接受后用五阶解，按误差调h；源码缓存f₀，每个attempt另做6次f，拒绝同样付费，初始化/跳点可另加调用 | 可在缓慢区放大、快速区缩步，2ms输出可由内部插值取得，无需每2ms重启求解器。显式法仍受稳定性限制；必须记录NFE、接受/拒绝数、步长分布和墙钟，不能保证比RK4快 | [官方dopri5系数](https://github.com/rtqichen/torchdiffeq/blob/master/torchdiffeq/_impl/dopri5.py)、[RK推进及插值源码](https://github.com/rtqichen/torchdiffeq/blob/master/torchdiffeq/_impl/rk_common.py)，web-source，read 对应函数 | 先测 |
| 1ms Adams–PECE | 缓存历史f，以AB预测、AM校正；AB3预测+AM4单次校正可维持四阶，启动后理想约2次新f/步，500ms约1000次加启动成本 | 可以保持1ms而减少重复RHS。多步稳定性与RK4不同；少量固定点校正不继承充分收敛隐式法的稳定性，可能发散。官方implicit_adams的rtol/atol管校正收敛，不是自适应时间误差；迭代越多NFE越高 | [官方fixed_adams.py](https://github.com/rtqichen/torchdiffeq/blob/master/torchdiffeq/_impl/fixed_adams.py)、[solver选项](https://github.com/rtqichen/torchdiffeq/blob/master/FURTHER_DOCUMENTATION.md)，web-source，read 系数、启动、迭代与警告；max_order=4时源码为AB3预测/AM4校正，不能误写AB4 | 随后测 |
| RK2/Heun | k₁=f(tₙ,zₙ)，k₂=f(tₙ+h,zₙ+hk₁)，zₙ₊₁=zₙ+h(k₁+k₂)/2；每步2次f | 1ms约1000次RHS但降为二阶；0.5ms约2000次，已无理想NFE优势。线性测试的放大因子为1+q+q²/2，不能沿用RK4稳定域；更低阶段数不保证目标误差达标 | [官方fixed_grid.py](https://github.com/rtqichen/torchdiffeq/blob/master/torchdiffeq/_impl/fixed_grid.py)、[registry](https://github.com/rtqichen/torchdiffeq/blob/master/torchdiffeq/_impl/odeint.py)，web-source，read Heun2及注册；已对照本机0.2.5，确有heun2 | 低成本对照 |
| Rosenbrock/W/Krylov | 各阶段解 `(I−γhJₙ)kᵢ=阶段RHS`，再加权更新；Jₙ=∂fθ/∂z；避免完整非线性迭代，但需要线性解/JVP | 仅在诊断支持刚性且线性代数成本可控时研究。NFE之外必须计JVP、Krylov正交化和线性解；不能把它理解成少调用几次神经网络即可大步稳定 | [PETSc TSROSW开发公式](https://petsc.org/release/manualpages/TS/TSROSW/)、[Tranquilli与Sandu，SIAM2014原文](https://arxiv.org/pdf/1305.5481)，web-source，read 公式、论文§2/§3.3–3.4；论文非心脏Neural ODE | 有刚性证据后 |
| BDF | 如BDF2：`3zₙ₊₁−4zₙ+zₙ₋₁=2h fθ(tₙ₊₁,zₙ₊₁)`；需解非线性残差，Newton矩阵为I−(2h/3)J | 成本含Newton、Jacobian/预条件及线性解，不能仅比NFE。官方CVODE把Adams用于非刚性、BDF用于刚性；本模型刚性尚为GAP，不能因原CRN方程或2ms误差退化便认定学习向量场刚性 | [SUNDIALS CVODE数学公式](https://sundials.readthedocs.io/en/latest/cvode/Mathematics_link.html)、[SciPy BDF官方文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.BDF.html)，web-source，read 多步、Newton、Jacobian及容差；SciPy实现为变阶1–5 | 有刚性证据后 |

自适应误差控制须专门处理全场隐态。官方torchdiffeq对单tensor默认 `RMS(e/(atol+rtol·max(|zₙ|,|zₙ₊₁|)))`；tuple默认各tensor RMS再取max，见[选项](https://github.com/rtqichen/torchdiffeq/blob/master/FURTHER_DOCUMENTATION.md)与[实际norm/误差缩放源码](https://github.com/rtqichen/torchdiffeq/blob/master/torchdiffeq/_impl/misc.py)（web-source，read）。本项目64/66≈97%的分量是hidden；它既可能主导误差，也可能稀释物理场误差。项目数学推断：若只有V/Ca两通道有同量级归一化误差q，hidden误差近零，全状态RMS只有q/√33；窄波前在43573节点上还会被空间平均。不能把默认RMS≤1解释为V/Ca每点均达标。

候选norm可对已按各通道容差缩放的r使用 `max(RMS(rV),RMS(rCa),RMS(rhidden))`，batch时先逐例再取max；物理场另核查局部最大误差/分位数与事件。hidden与物理场耦合，不能直接把hidden从norm删除，也不能把仅用于adjoint的seminorm文献当作前向提速保证。绝对容差需按冻结训练变换换算mV/nM与hidden尺度；rtol/atol仅控制局部估计误差，不保证500ms累计误差或激活F1。作为计算量诊断，忽略初始化时Dopri5约6(A+R)次f，对比原2000次，平均接受步长需大于约1.5·(1+R/A)ms才有NFE优势；这是推算，仍须计GPU同步与插值成本。

PECE示例（fⱼ=fθ(tⱼ,zⱼ)，固定h）：

\[
z^p_{n+1}=z_n+\frac h{12}(23f_n-16f_{n-1}+5f_{n-2}),\qquad
z_{n+1}=z_n+\frac h{24}\{9f_\theta(t_{n+1},z^p_{n+1})+19f_n-5f_{n-1}+f_{n-2}\}.
\]

校正态导数供后续历史使用；启动方法、阶数、校正次数及重启均须显式记录。torchdiffeq的 `method='rk4'` 实为3/8-rule，和本项目经典RK4不同，不能直接当作相同基线；其Adams启动也调用该变体。本轮已只读核查主代理安装的PyPI0.2.5源码：位于 `archive/ode_inference_speed_20261017/solver_env/Lib/site-packages/torchdiffeq/_impl/`，registry支持dopri8/dopri5/bosh3/fehlberg2/adaptive_heun、euler/midpoint/heun2/heun3/rk4、explicit_adams/implicit_adams（fixed_adams别名）、scipy_solver；上述Dopri5阶段、RMS norm、Heun与Adams行为均已对照。在线master仅作可访问原始来源链接；master新增的tsit5、trbdf2及其他隐式solver不列为本轮0.2.5已可用。Rosenbrock/BDF没有0.2.5原生GPU接口，BDF只可经scipy_solver包装，属于后续工程路线。

原生PyTorch solver可复用现有fθ包装，不需要重训或adjoint；直接odeint返回250帧完整66态会重新产生大量hidden输出存储，工程实现应保持solver历史连续并只保存V/Ca，不能每2ms重启以省输出。

隐式路线的规模限制是项目推算：43573×66=2875818维，单个稠密float32 Jacobian已约33TB，本机8GB无法采用此路径；需矩阵自由JVP/Krylov或经验证的稀疏/块预条件方案。[官方SciPy wrapper](https://github.com/rtqichen/torchdiffeq/blob/master/torchdiffeq/_impl/scipy_wrapper.py)每次f都在CPU NumPy与原device之间转换，且未传jac/jac_sparsity，因此 `scipy_solver+BDF` 不作为当前大规模GPU提速捷径（web-source，read wrapper源码）。所有方案都保留Neural ODE方程，但改变离散预测；先val选型，保留1ms原模型与全部冻结统计，不承诺任何solver的新误差或速度。本轮仅调研并修改本文件，未运行代码。

### 同日续：心脏文献“毫秒级”究竟计算什么

研究者明确要求联网核查。以下是原作者报告，不是本项目复现或本项目新测速；重点区分计算墙钟、所模拟的生理时间和时间预测误差。不能把所有毫秒级结果都解释成单帧：确有整段电压场的毫秒级代理，同时也有只输出激活图或低维状态的结果。

| 方法 | 论文或代码链接 | 对象层级 | 状态与观测 | 算子类型 | 时间处理 | 几何处理 | 训练数据规模 | 指标 | 与本项目差异和可借鉴点 | 来源标签 | 阅读状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| POD-DL-ROM | [Fresca、Manzoni，CMAME388(2022)114181](https://doi.org/10.1016/j.cma.2021.114181)；[可读作者原稿](https://arxiv.org/html/2101.11845) | 二维心肌组织，Monodomain+Aliev–Panfilov | 已知纵横向电导率及时间→电压全场；固定初态 | POD压缩+非线性decoder+时间/参数映射 | 直接时间查询，非Neural ODE | 固定10×10cm方域，4096/16384/65536节点 | 25训练参数×1000时刻，16测试参数 | 整例1000时刻覆盖0–400ms：15/60/3000ms，随上述三种节点数改变；GTX1070 8GB | 包含非线性解码和最终POD全场重构；无历史初态推断、Ca或CRN。原文明确重构规模导致耗时上升，不把15ms外推到任意网格 | web-source | read，§4.1计时定义、§4.2心脏案例；原稿Table2–3，正式版Table3–4 |
| 几何无关ViT神经算子 | [Zhou等，arXiv2512.01702v2，2026-01-04](https://arxiv.org/html/2512.01702v2) | 左房，补充验证左室 | 解剖、导电率、刺激位点→首次局部激活时间LAT图 | PointNet投影+ViT encoder/conv decoder | 一次输出LAT空间图，无电压时间轴 | UAC/UVC坐标；主模型50×50单通道输出；另有100×100左房与50³左室迁移案例 | 147例解剖×7位点×300参数=308700模拟LAT图，非308700位独立患者 | 作者报0.12ms/sample、LAT MAE5.1ms | §2.4只说现代NVIDIA GPU；具体推理GPU、batch、同步和映射回原网格计时为GAP。FEM生成标签的A100不能冒充推理硬件；非V/Ca全轨迹 | web-source | read，§2.4、§2.7、§4.2–4.3 |
| LAT/RPT FNO与KOL | [Ziarelli等，PLOS Comput Biol22(2026)e1013920](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013920)；[代码](https://github.com/edoardo100/timeactml) | 2D/3D组织及左室；3D为Ten Tusscher+Monodomain | 刺激区域→激活时间或复极时间图，分别训练 | FNO/非均匀DFT；核算子 | 直接终点图预测，不输出逐帧V或Ca | 固定左室不规则约35k DOFs | 较大左室组2000刺激样本，1600训练/400测试 | 单次FNO8.5ms、KOL56ms；Apple M1 Pro CPU-only | Results“3D unstructured ventricle”表4后给时延；未明确两终点合计耗时或I/O。节点数近本题，但每节点仅一个时间标量 | web-source | read，Dataset generation/Results/3D unstructured ventricle |
| MAPS-Net | [Lyu等，MICCAI2026 DT4H工作坊官方页](https://papers.miccai.org/miccai-2026-sat/DT4H_029.html)；[作者终稿PDF](https://papers.miccai.org/miccai-2026-sat/paper/DT4H_029.pdf) | 双心室电生理与ECG | 9维已知生理参数→PCA电势系数序列及ECG；数据为PDRE+Mitchell–Schaeffer | 参数条件Mamba/SSM+PCA/ECG分支，非Neural ODE | 参数编码后输出时间序列 | 5例双心室几何；跨几何是否共用权重/基底未明示 | 5例×400参数序列，每例250训练/50验证/100测试 | 单次forward1.5–2ms；PDRE一次QRST8–10s；患者反演10–15min | RTX A5500+Xeon W7-2495X；未给清晰N/K/T、物理采样率、batch/同步及2ms是否含完整PCA网格重构，均保留GAP。图2横轴t是序列索引，不能当ms。完整生成数据+训练+反演约65min，不能说患者孪生只需2ms | web-source | read，官方终稿§2.1–2.2、§3.1–3.2；本机archive/ode_inference_speed_20261017/literature_sources/有原PDF与阅读文本 |

既有论文补充速度口径：

- **LDNet，Nat Commun2024**（上表已有链接）：Table2二维AP online=0.139s，即139ms；沿用Table1 caption定义，仅低维动力学积分，**不含output-field evaluation**。补充§3.4二维预测450ms、100×100mm²域、FOM h=0.5mm/dt=0.25ms，保存2694空间点×180时刻、一个AP变量；输入是刺激半径和第二刺激波形、共同预处理初态，不是历史推断。CPU Intel Xeon E5-2640 2.4GHz。正文另报二维decoder每时空查询点约3.9微秒，与139ms分列；不能将这个单点成本等同于批量全场解码时延，也不移用1D的解码时间。
- **Fresca等，Front Physiol2021**（上表已有链接）：Table2–4分别有0.3s、0.2s、0.32/0.77s在线时延，Tesla V10032GB；前两组200ms窗口，折返例只取300–500ms的1000时刻。Table2正文“实时”措辞和表中0.3s略有冲突，以表值记录；精确批量/I/O计时未明示。
- **全心LNODE，npj Digit Med2024**（[正文](https://www.nature.com/articles/s41746-024-01084-x)，[官方补充](https://media.springernature.com/original/springer-static/esm/art:10.1038%2Fs41746-024-01084-x/MediaObjects/41746_2024_1084_MOESM1_ESM.pdf)）：补充§7、PDF第15页明确说明，在普通笔记本单处理器上，一个约1秒心搏可用1/300秒，即约3.3ms模拟完成。它是已知43参数和初始状态驱动的8维四腔压力/容积ODE，不输出电压、Ca或机械位移全场。补充§2的实际心搏周期为0.854s，§5前向Euler dt=1ms；不能把1ms积分步长写成推理墙钟。CPU型号、全帧导出成本未明示；本文“约3.3ms”来自作者对1/300秒的明示解释，不是从未知条件的加速倍数自行反推。
- **单细胞41态FNO，2025**：本轮核读找到训练耗时，但未核验到明确推理墙钟；不列入毫秒级实证。

对照解释（项目推断，不是文献原报）：同一节点数下，一张LAT图每节点仅一个时间值，而本题每节点250帧×2场=500个输出值；43573×250×2=21786500个float32，约87.15MB/例。输出规模不能直接换算成速度倍数。POD-DL-ROM确有整轨迹15ms的正例，其65k节点3s又说明全场解码的成本不可忽略；不能一概用口径差异解释本项目慢，也不能把小域、参数已知、单电压场的时延直接作为本题CRN双场历史预测的现成性能。

建议比较单位为“一例、固定历史输入、完整250帧V/Ca、全43573节点”，并分别计历史编码、潜态求解、全场解码和D2H；GPU同步及B1/实际batch需写明。沿用10/17本机既有实测，2.69s预测500ms对应约5.4倍物理时长。若示例目标为100ms/例，90例串行纯模型约9s；10ms/例则约0.9s，均不包含CPU评分/绘图，亦非本项目已达结果。此次仅文献阅读与记录，没有训练或新增模型实验。

## 2026-10-20：扩散系数、传导与持续活动数据设计

- [openCARP CV标定官方教程](https://opencarp.org/documentation/examples/02_ep_tissue/03a_study_prep_tunecv)，web-source，read关系式及CV对网格/离子模型/数值方案的依赖：均匀连续平面波假设下CV与单域电导率平方根成比例，教程以1D实测传播速度迭代标定。项目D_code为未除网格尺度的图L前系数，不能直接等同S/m；0.08→0.06/0.04的.866/.707仅同动力学连续近似的比值推算，不是当前数据测得CV。
- [Krogh-Madsen等，PLOS Comput Biol2012](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002390)，web-source，read Abstract、Introduction、Results及Discussion：CRN基础三维心房模拟中，降低耦合导致传导减慢、波长缩短，与更长折返持续时间相关；波长可近似用CV×ERP表示，研究实际以APD×CV估计并讨论偏差。该结果支持扫描D的机制动机，不保证本项目二维图中D越低活动越持久，也不把其cm阈值移作本题标准。
- [openCARP折返诱导官方教程](https://opencarp.org/documentation/examples/02_ep_tissue/21_reentry_induction)，web-source，read Setup及Prepace/RP/PSD/PEERP：采用AF重构CRN、实测CV标定及诱导后持续性核查；同一组织可因刺激协议变化得到持续或终止活动。本题应保存完整21维初态、D和刺激/初相位元数据，先小样本配对而非直接改物理参数后重做750例。当前本题750例全部只读审计中，尚无D新仿真。
