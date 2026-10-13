# 进展判定

每轮 ROUND_RESULT 的 progress 对象：claimed_kind、main_problem_effect、scope_limitations、evidence_level（≤ proof-draft）。

| claimed_kind | 判据 | 后续 |
|---|---|---|
| frontier-advance | 在声明范围内缩小核心缺口，有证据 | 继续下一个有界目标 |
| route-elimination | 严格排除某构造、参数范围或整个方法族 | 停止被排除部分 |
| enabling-result | 新工具或条件结果，核心难点未闭合 | 做能判断其用途的测试 |
| experimental-signal | 只有数值信号 | 复现、找失效案例或补协议 |
| reformulation | 难点换了形式，未证明更易 | 检验新表示是否带来机制 |
| repeat | 同一障碍再次出现 | 满足门槛后换机制 |
| inconclusive | 完成尝试但无法判断 | 保留记录，不包装成推进 |
| regression | 原依赖出错 | 冻结受影响分支并修复 |
| candidate-solution | 声称主命题成立 | 进入 claim-audit，不由脚本宣布完成 |

连续两轮同一障碍上 repeat 或 reformulation，下轮必须换方法族，或在计划中写 reopening_basis 指向具体新机制。连续三轮无 frontier-advance，下轮计划带 strategy_review：替代方法族比较与继续/暂停建议。
建议模式：runner 只校验格式，不自动 blocked、不改等级。审查者可以否定作者的分类，二者都保留。
