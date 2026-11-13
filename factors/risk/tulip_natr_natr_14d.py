"""Tulip Indicators

公式：100×ATR(n)/C；输出natr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/natr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：NATR.natr（参数：period）；追踪：PF01078；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_natr_natr_14d', 'root_function': 'ti_natr', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['natr'], 'output_index': 0, 'warmup': 13, 'kernel': 'kernel_68b0d5ff80ebfc02', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_natr_natr_14d', {})
class Factor_tulip_natr_natr_14d(PublicFactor):
    name = 'tulip_natr_natr_14d'
    description = "100×ATR(n)/C；输出natr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/natr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：NATR.natr（参数：period）；追踪：PF01078；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
