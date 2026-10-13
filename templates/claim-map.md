# 命题依赖图

## 当前状态
- 目标命题：
- 当前最高等级：
- 当前最小缺口：
- 最近一次审查报告：

## 依赖图
```mermaid
flowchart BT
    D1["D1 定义<br/>human-verified"]
    S1["S1 辅助命题<br/>conjecture"]
    A1["A1 路线命题<br/>proof-draft"]
    P0["P0 主命题<br/>conjecture"]
    E1["E1 实验<br/>experimental"]
    D1 --> A1
    S1 --> A1
    A1 --> P0
    E1 -.->|supports only| A1
```

## 节点登记表
| ID | 命题 | 验证维度 | 等级 | 证据（台账 ID / 文件） | 当前 GAP |
|---|---|---|---|---|---|

## GAP 登记
### GAP-A1-1
- 位置：
- 所需结论：
- 已试路线：
- 失效案例测试：
- 影响节点：
- 下一步：
