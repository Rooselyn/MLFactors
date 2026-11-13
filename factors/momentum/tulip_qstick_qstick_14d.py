"""Tulip Indicators

公式：mean(C−O,n)；输出qstick；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/qstick.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：QSTICK.qstick（参数：period）；追踪：PF01084；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_qstick_qstick_14d', 'root_function': 'ti_qstick', 'required_inputs': ['open', 'close'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['qstick'], 'output_index': 0, 'warmup': 13, 'kernel': 'kernel_d36833e454a2e646', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_qstick_qstick_14d', {})
class Factor_tulip_qstick_qstick_14d(PublicFactor):
    name = 'tulip_qstick_qstick_14d'
    description = "mean(C−O,n)；输出qstick；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/qstick.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：QSTICK.qstick（参数：period）；追踪：PF01084；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
