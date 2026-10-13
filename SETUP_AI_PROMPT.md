# 心脏项目启动提示

读取本目录 AGENTS.md、projects/cardiac-ep/CURRENT_STATE.md、SOURCE_MAP.md 和 cardiac-workspace.json。
用配置解析上一级心脏项目，读取其 AGENTS.md、CODEX.md，并检查 Git status/diff。
我的重点是心脏电生理与 AI 个体化建模，目前先做 TC_GCN_server 的 AR/PCA 及直接时间预测对照，主要交付代码和实验。

先运行只读 doctor，依据真实文件确认数据、Python 和设备。
按本次任务实施最小修改，运行受影响测试与必要的真实数据短实验。
保存协议、源码哈希、命令、种子、预算、原始日志、退出状态和证据路径。
分别报告实现正确性与预测/个体化有效性；跨会话更新短状态，不自动复用旧服务器运行状态。
已有授权范围内持续完成；缺少远程地址或资源时先完成本地可审阅代码和命令，再指出具体缺口。
自动多轮推进使用 tools/research_queue.py，先读 agents/core/queue-core.md 和 problems/cardiac-research/README.md。
根据研究目标使用现有任务或新增 task.json；runner 自动传递研究包、状态与下一动作。
在自动回合中使用研究包提供的 EXPERIMENT_CONFIG.json 运行实验工具，保护状态交给 runner 提交。
不要运行归档的数学队列、创建 graphlab 或修改正式数据/权重。
