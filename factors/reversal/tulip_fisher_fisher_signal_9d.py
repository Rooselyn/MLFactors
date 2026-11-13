"""Tulip Indicators

公式：X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；输出fisher_signal；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/fisher.c)；参数={'period': 9}；以下完整数值核为该条目的最终计算定义。；原目录：FISHER.fisher_signal（参数：period）；追踪：PF01062；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'tulip_fisher_fisher_signal_9d', 'root_function': 'ti_fisher', 'required_inputs': ['high', 'low'], 'parameters': {'period': 9}, 'options': [9], 'outputs': ['fisher', 'fisher_signal'], 'output_index': 1, 'warmup': 8, 'kernel': 'kernel_79c08356c3008376', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_fisher_fisher_signal_9d', {})
class Factor_tulip_fisher_fisher_signal_9d(PublicFactor):
    name = 'tulip_fisher_fisher_signal_9d'
    description = "X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；输出fisher_signal；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/fisher.c)；参数={'period': 9}；以下完整数值核为该条目的最终计算定义。；原目录：FISHER.fisher_signal（参数：period）；追踪：PF01062；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
