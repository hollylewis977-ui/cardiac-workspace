# 激活事件

阈值 −20 mV 上穿记为激活。指标：首次激活节点漏检率、误检率、匹配事件数、匹配时间 MAE；下降事件 F1 另算。
无匹配事件时 MAE=0 不表示准确；首次上穿不替代再次激活与复极检查。
实现：code/TC_GCN_server/quantify_results.py。
