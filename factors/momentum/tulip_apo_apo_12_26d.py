"""Tulip Indicators

公式：MA(C,fast)−MA(C,slow)；输出apo；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/apo.c)；参数={'short_period': 12, 'long_period': 26}；以下完整数值核为该条目的最终计算定义。；原目录：APO.apo（参数：short_period, long_period）；追踪：PF01041；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_apo_apo_12_26d', 'root_function': 'ti_apo', 'required_inputs': ['real'], 'parameters': {'short_period': 12, 'long_period': 26}, 'options': [12, 26], 'outputs': ['apo'], 'output_index': 0, 'warmup': 1, 'kernel': 'kernel_d7124ac15750561c', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_apo_apo_12_26d', {})
class Factor_tulip_apo_apo_12_26d(PublicFactor):
    name = 'tulip_apo_apo_12_26d'
    description = "MA(C,fast)−MA(C,slow)；输出apo；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/apo.c)；参数={'short_period': 12, 'long_period': 26}；以下完整数值核为该条目的最终计算定义。；原目录：APO.apo（参数：short_period, long_period）；追踪：PF01041；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
