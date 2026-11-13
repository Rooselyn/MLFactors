"""Tulip Indicators

公式：两次SMA：奇数n用(n+1)/2与(n+1)/2，偶数n用n/2与n/2+1；具体初始化按来源；输出trima；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/trima.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：TRIMA.trima（参数：period）；追踪：PF01092；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_trima_trima_20d', 'root_function': 'ti_trima', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['trima'], 'output_index': 0, 'warmup': 19, 'kernel': 'kernel_7f98368fcbe266c8', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_trima_trima_20d', {})
class Factor_tulip_trima_trima_20d(PublicFactor):
    name = 'tulip_trima_trima_20d'
    description = "两次SMA：奇数n用(n+1)/2与(n+1)/2，偶数n用n/2与n/2+1；具体初始化按来源；输出trima；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/trima.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：TRIMA.trima（参数：period）；追踪：PF01092；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
