"""Tulip Indicators

公式：C/C[-n]−1；Tulip原实现不乘100，不能与百分数ROC合并；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/roc.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ROC.roc（参数：period）；追踪：PF01085；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_roc_roc_14d', 'root_function': 'ti_roc', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['roc'], 'output_index': 0, 'warmup': 14, 'kernel': 'kernel_9f067737fe7c380b', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_roc_roc_14d', {})
class Factor_tulip_roc_roc_14d(PublicFactor):
    name = 'tulip_roc_roc_14d'
    description = "C/C[-n]−1；Tulip原实现不乘100，不能与百分数ROC合并；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/roc.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ROC.roc（参数：period）；追踪：PF01085；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
