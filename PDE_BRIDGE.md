# 项目连接

实际项目由 cardiac-workspace.json 的 project_root 指定，默认 ..（本工作台的上一级目录）。
该项目的 AGENTS.md 是薄入口，要求读取此工作台的规则、SOURCE_MAP 和 CURRENT_STATE。
路径变动时同步更新配置及该薄入口；配置不会改变 Codex 的操作系统权限。
项目已有 CODEX.md/CLAUDE.md 保留，模型、数据、权重与原 Slurm 脚本均没有因适配而改写。
自动多轮队列从本工作台 tools/research_queue.py 启动，工作目录为心脏项目；每轮额外可写目录为当前任务目录。
队列读取全局研究状态，独立维护 projects/cardiac-ep/queue/<slug>/，避免覆盖并行会话的记录。
