"""Tulip Indicators

公式：a+bn；输出tsf；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/tsf.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：TSF.tsf（参数：period）；追踪：PF01094；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_tsf_tsf_20d', 'root_function': 'ti_tsf', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['tsf'], 'output_index': 0, 'warmup': 19, 'kernel': 'kernel_d4684a365e5be679', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_tsf_tsf_20d', {})
class Factor_tulip_tsf_tsf_20d(PublicFactor):
    name = 'tulip_tsf_tsf_20d'
    description = "a+bn；输出tsf；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/tsf.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：TSF.tsf（参数：period）；追踪：PF01094；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
