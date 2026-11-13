"""Tulip Indicators

公式：100×(C−TSF(C,n))/C；输出fosc；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/fosc.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：FOSC.fosc（参数：period）；追踪：PF01063；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_fosc_fosc_20d', 'root_function': 'ti_fosc', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['fosc'], 'output_index': 0, 'warmup': 20, 'kernel': 'kernel_8c5f711fbd5d9ff2', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_fosc_fosc_20d', {})
class Factor_tulip_fosc_fosc_20d(PublicFactor):
    name = 'tulip_fosc_fosc_20d'
    description = "100×(C−TSF(C,n))/C；输出fosc；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/fosc.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：FOSC.fosc（参数：period）；追踪：PF01063；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
