"""Tulip Indicators

公式：E_t=αC_t+(1−α)E_{t−1}，α=2/(n+1)；输出ema；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/ema.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：EMA.ema（参数：period）；追踪：PF01059；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_ema_ema_20d', 'root_function': 'ti_ema', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['ema'], 'output_index': 0, 'warmup': 0, 'kernel': 'kernel_5e3cf44a2335c124', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_ema_ema_20d', {})
class Factor_tulip_ema_ema_20d(PublicFactor):
    name = 'tulip_ema_ema_20d'
    description = "E_t=αC_t+(1−α)E_{t−1}，α=2/(n+1)；输出ema；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/ema.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：EMA.ema（参数：period）；追踪：PF01059；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
