"""Tulip Indicators

公式：ER=abs(C−C[-n])/Σabs(ΔC)；α=(ER(2/(fast+1)−2/(slow+1))+2/(slow+1))²；K_t=K_{t−1}+α(C_t−K_{t−1})；输出kama；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/kama.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：KAMA.kama（参数：period）；追踪：PF01065；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_kama_kama_14d', 'root_function': 'ti_kama', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['kama'], 'output_index': 0, 'warmup': 13, 'kernel': 'kernel_c5f1dcf184a1f738', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_kama_kama_14d', {})
class Factor_tulip_kama_kama_14d(PublicFactor):
    name = 'tulip_kama_kama_14d'
    description = "ER=abs(C−C[-n])/Σabs(ΔC)；α=(ER(2/(fast+1)−2/(slow+1))+2/(slow+1))²；K_t=K_{t−1}+α(C_t−K_{t−1})；输出kama；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/kama.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：KAMA.kama（参数：period）；追踪：PF01065；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
