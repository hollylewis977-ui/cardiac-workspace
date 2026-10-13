# 跨会话记录

CURRENT_STATE.md 只保存当前目标、有效证据、限制和下一动作，不复制增长中的历史。
progress.md 追加每轮做了什么、运行命令/结果路径和剩余问题。
verification-ledger.md 将结论与直接证据对应；evidence-map.md 保存影响关系。
原始日志、checkpoint/基底来源、数据与代码清单优先于摘要。

自动队列的每项任务使用 projects/cardiac-ep/queue/<slug>/ 下的同名记录。
worker 返回结构化结果，runner 验证并通过 before/after、COMMIT/APPLIED 提交；不重写全局研究状态。
单轮实验工具使用回合内 EXPERIMENT_CONFIG.json，将日志保存到 artifacts/experiments/。

区分软件适配完成、实验运行完成和科学假设得到支持。运行计数、读文件数、
格式整理、训练 loss 下降均不能单独代表预测或个体化能力取得进展。
