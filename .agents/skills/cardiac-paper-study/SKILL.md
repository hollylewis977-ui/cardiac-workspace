---
name: cardiac-paper-study
description: Translate a cardiac electrophysiology or neural-operator paper into a reproducible implementation and experiment plan for the linked PDE project; also use when drafting methods/results from its actual experiments.
---

# 从论文方法到心脏代码

技能目录上溯三级到工作台。先读 [源码索引](../../../projects/cardiac-ep/SOURCE_MAP.md) 和
[文献核查](../../../agents/protocols/literature-check.md)，再按用户材料读取原文。
没有原文时只给待核查假设，不补造公式、性能或新颖性。

提取可实施要素：研究对象、完整/观测状态、单位、几何/边界/刺激、算子/网络、
训练信息、损失、对照、选模和测试协议。
将每项映射到项目实际变量、函数和文件；说明缺少的数据或接口。

复现先给最小可执行基线与验收，再按授权实现、运行和比较。
区分源论文、项目历史实现、本次修改。当前 Direct 借用 FBNO 参考域算子思想，
不能把它写成已实现移动边界 H；当前 v10 也不支持凭几何编码宣称个体化验证。

写方法/结果时读 [研究写作](../../../agents/instructions/paper-writing.md)。
所有实验数值追溯到原始日志/权重/清单，图输出 PNG；未运行项目保持“方案/待验证”。
