"""Tulip Indicators

公式：DIF=EMA(C,fast)−EMA(C,slow)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；输出macd_histogram；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/macd.c)；参数={'short_period': 12, 'long_period': 26, 'signal_period': 9}；以下完整数值核为该条目的最终计算定义。；原目录：MACD.macd_histogram（参数：short_period, long_period, signal_period）；追踪：PF01072；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_macd_macd_histogram_12_26_9d', 'root_function': 'ti_macd', 'required_inputs': ['real'], 'parameters': {'short_period': 12, 'long_period': 26, 'signal_period': 9}, 'options': [12, 26, 9], 'outputs': ['macd', 'macd_signal', 'macd_histogram'], 'output_index': 2, 'warmup': 25, 'kernel': 'kernel_e08b6d03df73b0bd', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_macd_macd_histogram_12_26_9d', {})
class Factor_tulip_macd_macd_histogram_12_26_9d(PublicFactor):
    name = 'tulip_macd_macd_histogram_12_26_9d'
    description = "DIF=EMA(C,fast)−EMA(C,slow)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；输出macd_histogram；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/macd.c)；参数={'short_period': 12, 'long_period': 26, 'signal_period': 9}；以下完整数值核为该条目的最终计算定义。；原目录：MACD.macd_histogram（参数：short_period, long_period, signal_period）；追踪：PF01072；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
