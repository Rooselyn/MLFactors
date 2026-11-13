"""Tulip Indicators

公式：100×(EMA³(C,n)/delay(EMA³(C,n),1)−1)；输出trix；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/trix.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：TRIX.trix（参数：period）；追踪：PF01093；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_trix_trix_14d', 'root_function': 'ti_trix', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['trix'], 'output_index': 0, 'warmup': 40, 'kernel': 'kernel_c7db6000c26e04c0', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_trix_trix_14d', {})
class Factor_tulip_trix_trix_14d(PublicFactor):
    name = 'tulip_trix_trix_14d'
    description = "100×(EMA³(C,n)/delay(EMA³(C,n),1)−1)；输出trix；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/trix.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：TRIX.trix（参数：period）；追踪：PF01093；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
