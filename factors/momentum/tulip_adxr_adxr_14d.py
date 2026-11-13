"""Tulip Indicators

公式：(ADX_t+ADX_{t−(n−1)})/2；滞后n或n−1按来源；输出adxr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/adxr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ADXR.adxr（参数：period）；追踪：PF01040；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'tulip_adxr_adxr_14d', 'root_function': 'ti_adxr', 'required_inputs': ['high', 'low'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['adxr'], 'output_index': 0, 'warmup': 39, 'kernel': 'kernel_1c0a3eaf67197aa2', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_adxr_adxr_14d', {})
class Factor_tulip_adxr_adxr_14d(PublicFactor):
    name = 'tulip_adxr_adxr_14d'
    description = "(ADX_t+ADX_{t−(n−1)})/2；滞后n或n−1按来源；输出adxr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/adxr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ADXR.adxr（参数：period）；追踪：PF01040；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
