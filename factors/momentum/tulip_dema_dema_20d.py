"""Tulip Indicators

公式：2EMA(C,n)−EMA(EMA(C,n),n)；输出dema；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/dema.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：DEMA.dema（参数：period）；追踪：PF01052；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_dema_dema_20d', 'root_function': 'ti_dema', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['dema'], 'output_index': 0, 'warmup': 38, 'kernel': 'kernel_085b1acc7e8cfbbe', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_dema_dema_20d', {})
class Factor_tulip_dema_dema_20d(PublicFactor):
    name = 'tulip_dema_dema_20d'
    description = "2EMA(C,n)−EMA(EMA(C,n),n)；输出dema；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/dema.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：DEMA.dema（参数：period）；追踪：PF01052；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
