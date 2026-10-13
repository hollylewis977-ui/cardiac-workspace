# 流映射 Φ_τ

Φ_τ: y(t) ↦ y(t+τ)，y ∈ R^{N×21}，由 y' = D·L y + R(y) 的数值积分定义：每步 0.02 ms，先扩散并裁剪 V，再离子步进。
实现：code/DATASET/total_generator_normalize_v10.py 的 simulate_200ms_and_sample（名称过时，实际 total_ms=2000）。
代理模型逼近的不是 Φ_τ 本身，而是观测序列上的复合 O∘Φ_τ 在历史条件下的推进。
