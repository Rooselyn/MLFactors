"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL scale = 1.0 / period;；const TI_REAL annual = sqrt(252); /* Multiplier, number of trading days in year. */；for (i = 1; i <= period; ++i) {；sum += c;；sum2 += c * c;；for (i = period+1; i < size; ++i) {；sum2 -= cp * cp;；输出volatility；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/volatility.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：VOLATILITY.volatility（参数：period）；追踪：PF01098；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_volatility_volatility_14d', 'root_function': 'ti_volatility', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['volatility'], 'output_index': 0, 'warmup': 14, 'kernel': 'kernel_b445e266b0035d72', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_volatility_volatility_14d', {})
class Factor_tulip_volatility_volatility_14d(PublicFactor):
    name = 'tulip_volatility_volatility_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL scale = 1.0 / period;；const TI_REAL annual = sqrt(252); /* Multiplier, number of trading days in year. */；for (i = 1; i <= period; ++i) {；sum += c;；sum2 += c * c;；for (i = period+1; i < size; ++i) {；sum2 -= cp * cp;；输出volatility；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/volatility.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：VOLATILITY.volatility（参数：period）；追踪：PF01098；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
