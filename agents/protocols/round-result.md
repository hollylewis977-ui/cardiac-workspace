# 自动研究回合与实验运行结果

自动队列使用 templates/cardiac-round-result.schema.json。每轮目录：
projects/cardiac-ep/queue/<slug>/.runtime/rounds/<round-id>/。

读取 RESEARCH_PACKET.md 与 PACKET.json。固定字段：
schema_version=1、round_id、packet_sha256；
status=continue/waiting/blocked/completed；
next_phase=analyze/implement/experiment/assess；
progress_made、summary、next_action、current_state、blocker；
evidence、checks、acceptance。

- current_state 是下一轮短索引，最多 12 KiB/300 行；不覆盖全局项目状态。
- continue 必须有可执行下一步；waiting/blocked 必须指出具体外部依赖或缺口。
- evidence 为 workspace:<相对工作台路径> 或 project:<相对心脏项目路径> 字符串列表；
  引用实际存在且 <=16 MiB 的文件，大权重/数据引用小型哈希清单或报告。
- checks 为 {command, exit_code, log}，log 必须出现在 evidence 中；没有执行时不能填 0。
- acceptance 为 {id, outcome, evidence}，原 task.json 的每个验收 ID 都必须出现且不能新增；
  outcome=passed/failed/not-run。passed 需要直接证据。
- completed 要求全部原验收通过、检查退出码均为 0 且不存在 blocker。
  这仍是 Agent 根据证据报告任务完成，不是对临床能力或所有科学结论的独立认证。

用 --output-schema 请求结构化最终回复，--output-last-message 保存为 ROUND_RESULT.json。
复制 PACKET.json 中的 ID/哈希；不要自己改 runner 保护的 state.json、CURRENT_STATE、progress 或台账。
原始调用记录为 events.jsonl、stderr.log、PROCESS.json、RUN.json，代码和临时实验产物保留。
正常结果由 runner 提交；失败/超时仍保留历史，不能写成 completed。
下一轮先检查上轮遗留产物、checkpoint 与作业状态，不盲目重跑。

独立实验工具 tools/cardiac_workspace.py 的 runs/<id>/run.json 继续适用：
completed 仅表示脚本退出 0，evidence 中预测/个体化等维度不会因此自动提高。
它可以被自动研究回合调用，结果路径作为当前回合的直接证据。
