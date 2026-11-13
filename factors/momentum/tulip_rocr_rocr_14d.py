"""Tulip Indicators

公式：C/C[-n]；输出rocr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/rocr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ROCR.rocr（参数：period）；追踪：PF01086；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_rocr_rocr_14d', 'root_function': 'ti_rocr', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['rocr'], 'output_index': 0, 'warmup': 14, 'kernel': 'kernel_b055aeee9d9864f0', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_rocr_rocr_14d', {})
class Factor_tulip_rocr_rocr_14d(PublicFactor):
    name = 'tulip_rocr_rocr_14d'
    description = "C/C[-n]；输出rocr；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/rocr.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：ROCR.rocr（参数：period）；追踪：PF01086；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
