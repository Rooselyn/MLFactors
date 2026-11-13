"""Tulip Indicators

公式：ATR_t=(ATR_{t−1}(n−1)+TR_t)/n；首值为n期TR均值；初始化/平滑变体按来源；输出atr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/atr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ATR.atr（参数：period）；追踪：PF01045；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
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
SPEC = {'name': 'tulip_atr_atr_14d', 'root_function': 'ti_atr', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['atr'], 'output_index': 0, 'warmup': 13, 'kernel': 'kernel_0957d4b18e7b27bc', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_atr_atr_14d', {})
class Factor_tulip_atr_atr_14d(PublicFactor):
    name = 'tulip_atr_atr_14d'
    description = "ATR_t=(ATR_{t−1}(n−1)+TR_t)/n；首值为n期TR均值；初始化/平滑变体按来源；输出atr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/atr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ATR.atr（参数：period）；追踪：PF01045；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
