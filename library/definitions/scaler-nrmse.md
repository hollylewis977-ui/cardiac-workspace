# Scaler 与 NRMSE

Scaler 固定范围 V ∈ [−100, 50] mV，Ca ∈ [0, 0.0012] mM。
NRMSE 分母固定：V 150 mV，Ca 0.0012 mM。归一化误差与物理误差分开报告。
全域 NRMSE 与活动区 NRMSE 都要给；persistence（保持 500 ms 帧不变）是必报对照。
实现：code/TC_GCN_server/data.py 的 Scaler；指标见 quantify_results.py。
