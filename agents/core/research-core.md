# 心脏计算研究核心

先读 projects/cardiac-ep/problem.md：对象、观测算子、数据切分、归一化、四个时间范围和主命题。名称相似不是协议相同的依据。

区分四类对象：生成器的完整状态 y、保存的观测 (V, Ca)、模型内部表示（GRU 隐状态、区域记忆态 H）、可识别的个体参数。未知量写未知；不从文件名推断物理或生理有效性。

默认探索：从当前缺口推进，按 agents/protocols/explore.md 维护方法族。先复现再改进；多因素改动承认是联合比较。训练、预处理拟合、选模、测试的病例和时间范围分别记录；测试集已用于诊断时声明开发暴露。

证据等级七级：conjecture 只有假设；experimental 单种子、短预算或合成数据上的数值信号，smoke、低 loss、单病例图止于此；partial-result 只在受限范围成立；proof-draft 完整协议下成立但只有自报；agent-verified 独立重算一致且 claim-audit 十项通过；human-verified 研究者逐项接受；formalized 在开发中从未接触的数据上成立。自检最高 proof-draft。每条命题另记验证维度 code / numerics / data / prediction / personalization / uncertainty，各为 not-assessed / supported / failed。

认证触发：某路线声称决定性子目标在完整协议下成立，或某病例严格否定一条命题，进入 claim-audit 或 failure-case-audit，冻结依赖节点。其他中间结果局部检查后继续。

来源逐条标 internal / provided-source / web-source。外部文献、项目历史记录和本次实际运行分别标明。

每轮交付之一：已验证修复、可复现基线、消融比较、定位到代码或数据的失败、认证过的失效案例、明确实验方案。按 agents/protocols/progress-assessment.md 归类进展。CURRENT_STATE 是索引，证据冲突以原始材料为准。文件数量、重命名和状态整理不算推进。
