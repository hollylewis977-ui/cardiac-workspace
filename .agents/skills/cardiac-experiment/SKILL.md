---
name: cardiac-experiment
description: Modify, debug, reproduce and validate cardiac electrophysiology experiments in the linked PDE project, especially TC_GCN_server AR/PCA and FBNO_time_forecast. Use for code, data protocol, training, evaluation and experiment analysis; not for generic medical advice.
---

# 心脏代码与实验

从技能目录上溯三级到工作台，读 [源码索引](../../../projects/cardiac-ep/SOURCE_MAP.md)、
[短状态](../../../projects/cardiac-ep/CURRENT_STATE.md) 与 cardiac-workspace.json。
解析 project_root 后检查其 AGENTS.md/CODEX.md 和 Git diff；已有用户修改优先保留。

依据请求选择实际目录：AR/PCA 用 TC_GCN_server，直接查询用 FBNO_time_forecast。
先复现问题或跑受影响测试，再做最小修改；两套 main/data/model 分进程导入。
可用工作台 tools/cardiac_workspace.py doctor / plan / run 保存有上限的本地验证。
正式实验复用项目现有入口，核查 --help，按已授权预算继续；不自动提交/取消远程作业。

- 数据/泄漏任务读 [数据协议](../../../agents/protocols/data-validation.md)。
- 模型修改、性能任务读 [代码实验](../../../agents/protocols/computation.md)。
- 精度/生理/个体化结论读 [模型验证](../../../agents/protocols/model-validation.md)。

特别核对观测、梯度监督、PCA 拟合和验证选模的时间范围。
v10 形变坐标未进入动力学；单帧 V/Ca 未包含完整 21 维状态；
Direct 没有 AR 的 strict-validation 参数；图差分损失不是完整 CRN 残差。

记录源码/数据/基底来源、命令、种子、设备、预算和退出状态。
交付实际改动、运行结果与路径；smoke 只能支持软件可执行性，未来预测和个体化结论另需证据。
更新工作台短状态和台账，不把整理本身记为科学结果。
