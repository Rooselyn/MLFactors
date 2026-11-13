"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；输出linregslope；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/linregslope.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：LINREGSLOPE.linregslope（参数：period）；追踪：PF01069；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_linregslope_linregslope_20d', 'root_function': 'ti_linregslope', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['linregslope'], 'output_index': 0, 'warmup': 19, 'kernel': 'kernel_539ea3d5c12f49e2', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_linregslope_linregslope_20d', {})
class Factor_tulip_linregslope_linregslope_20d(PublicFactor):
    name = 'tulip_linregslope_linregslope_20d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；输出linregslope；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/linregslope.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：LINREGSLOPE.linregslope（参数：period）；追踪：PF01069；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
