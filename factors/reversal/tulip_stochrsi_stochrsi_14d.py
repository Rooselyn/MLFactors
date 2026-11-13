"""Tulip Indicators

公式：(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；输出stochrsi；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/stochrsi.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：STOCHRSI.stochrsi（参数：period）；追踪：PF01090；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_stochrsi_stochrsi_14d', 'root_function': 'ti_stochrsi', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['stochrsi'], 'output_index': 0, 'warmup': 27, 'kernel': 'kernel_fdfa9cfd1b1e14b4', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_stochrsi_stochrsi_14d', {})
class Factor_tulip_stochrsi_stochrsi_14d(PublicFactor):
    name = 'tulip_stochrsi_stochrsi_14d'
    description = "(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；输出stochrsi；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/stochrsi.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：STOCHRSI.stochrsi（参数：period）；追踪：PF01090；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
