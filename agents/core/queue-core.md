# 自动多轮研究队列

主入口 tools/research_queue.py，配置 research-queue.json；服务器 Slurm 脚本另用根目录 global-memory-queue.json。
旧 tools/conjecture_queue.py 名称保留为兼容入口。tools/cardiac_workspace.py 是队列内可调用的实验工具。

任务定义在 problems/cardiac-research/items/<slug>/task.json：目标、范围、验收、ready/enabled 与可选累计回合上限。
默认 ar-pca 任务衔接现有研究目标，启动前核对项目当前状态，避免重复其他会话正在做的实验。
add/enable 准备任务；plan/packet/once --dry-run 只读；once 调用一次 Codex；
run 连续推进；start 后台连续推进；status/watch 查看；stop 在当前回合结束后停止；
resume 恢复已暂停任务，然后 run/start 继续。

每轮自动调用 codex exec，阶段为 analyze / implement / experiment / assess。
阶段依据证据选择，可以重复或回退；不是执行完一个脚本就结束整个研究。
新调用从已封存的研究包和短状态接续，不依赖终端聊天记录，也不完整重读增长中的历史。
继承当前 CLI 的模型与 reasoning 配置；仅在研究者明确设置时覆盖，不自行更换模型。

任务状态：queued / pushing / waiting / blocked / completed / runtime-error / paused。
waiting 附外部依赖，按 poll_seconds 再查；blocked 是具体缺失条件；
连续无进展或运行故障达到配置上限，只暂停相应任务，不全局冻结。
完成必须覆盖任务原验收项并有真实文件证据及通过的检查；科学可信度仍逐项报告。
多任务按上次运行时间公平轮转，同一工作台持有单一锁，避免同时改同一心脏代码。
普通队列不自动启用多 Agent 或数学 mixed-isolated 分支。

预算沿用原版默认：单轮 90 分钟、一次启动 24 小时，默认不限制回合数。
--max-rounds / --max-hours 限制本次启动；task.json 的 max_rounds 限制该任务累计回合。
可配置 max_tokens；按每轮真实 input_tokens + output_tokens 检查，不重复加 cached_input_tokens。
token 上限是回合边界的软上限，可能被当前回合超出；用量缺失时停止该次预算运行，不当作 0。
主动重新 run/start 是新一轮启动预算，任务累计回合、状态和证据不会清零。

每个任务在 projects/cardiac-ep/queue/<slug>/ 保存短状态和证据。
worker 只改指定源码、写本轮产物、返回结构化结果；runner 验证 packet 哈希、证据与验收后统一写状态。
状态提交保留 before/after 与 COMMIT/APPLIED 日志；部分写入可在下次启动时安全补齐。
外部编辑冲突则保存材料并暂停该任务，绝不覆盖当前内容。
没有提交记录的中断回合不能自动判定完成；resume 前查看其产物和外部作业，避免重复训练。
全局 CURRENT_STATE 由交互式会话维护，队列不重写，防止覆盖其他会话的研究记录。
