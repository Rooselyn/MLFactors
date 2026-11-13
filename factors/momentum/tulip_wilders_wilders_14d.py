"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL per = 1.0 / ((TI_REAL)period);；for (i = 0; i < period; ++i) {；sum += input[i];；TI_REAL val = sum / period;；for (i = period; i < size; ++i) {；val = (input[i]-val) * per + val;；输出wilders；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/wilders.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：WILDERS.wilders（参数：period）；追踪：PF01102；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_wilders_wilders_14d', 'root_function': 'ti_wilders', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['wilders'], 'output_index': 0, 'warmup': 13, 'kernel': 'kernel_e4dfd221a0ff9287', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_wilders_wilders_14d', {})
class Factor_tulip_wilders_wilders_14d(PublicFactor):
    name = 'tulip_wilders_wilders_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL per = 1.0 / ((TI_REAL)period);；for (i = 0; i < period; ++i) {；sum += input[i];；TI_REAL val = sum / period;；for (i = period; i < size; ++i) {；val = (input[i]-val) * per + val;；输出wilders；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/wilders.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：WILDERS.wilders（参数：period）；追踪：PF01102；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
