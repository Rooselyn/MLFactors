"""Tulip Indicators

公式：3EMA(C,n)−3EMA(EMA(C,n),n)+EMA(EMA(EMA(C,n),n),n)；输出tema；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/tema.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：TEMA.tema（参数：period）；追踪：PF01091；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_tema_tema_20d', 'root_function': 'ti_tema', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['tema'], 'output_index': 0, 'warmup': 57, 'kernel': 'kernel_5ec0d4795b87e310', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_tema_tema_20d', {})
class Factor_tulip_tema_tema_20d(PublicFactor):
    name = 'tulip_tema_tema_20d'
    description = "3EMA(C,n)−3EMA(EMA(C,n),n)+EMA(EMA(EMA(C,n),n),n)；输出tema；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/tema.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：TEMA.tema（参数：period）；追踪：PF01091；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
