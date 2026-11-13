"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL short_div = 1.0 / short_period;；const TI_REAL long_div = 1.0 / long_period;；for (i = 0; i < long_period; ++i) {；short_sum += input[i];；long_sum += input[i];；const TI_REAL savg = short_sum * short_div;；const TI_REAL lavg = long_sum * long_div;；for (i = long_period; i < size; ++i) {；输出vosc；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vosc.c)；参数={'short_period': 5, 'long_period': 10}；以下完整数值核为该条目的最终计算定义。；原目录：VOSC.vosc（参数：short_period, long_period）；追踪：PF01099；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'tulip_vosc_vosc_5_10d', 'root_function': 'ti_vosc', 'required_inputs': ['volume'], 'parameters': {'short_period': 5, 'long_period': 10}, 'options': [5, 10], 'outputs': ['vosc'], 'output_index': 0, 'warmup': 9, 'kernel': 'kernel_39a7183d69402b45', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_vosc_vosc_5_10d', {})
class Factor_tulip_vosc_vosc_5_10d(PublicFactor):
    name = 'tulip_vosc_vosc_5_10d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL short_div = 1.0 / short_period;；const TI_REAL long_div = 1.0 / long_period;；for (i = 0; i < long_period; ++i) {；short_sum += input[i];；long_sum += input[i];；const TI_REAL savg = short_sum * short_div;；const TI_REAL lavg = long_sum * long_div;；for (i = long_period; i < size; ++i) {；输出vosc；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vosc.c)；参数={'short_period': 5, 'long_period': 10}；以下完整数值核为该条目的最终计算定义。；原目录：VOSC.vosc（参数：short_period, long_period）；追踪：PF01099；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
