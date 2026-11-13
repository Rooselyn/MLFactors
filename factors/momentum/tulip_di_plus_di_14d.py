"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；const TI_REAL *close = inputs[2];；TI_REAL *plus_di = outputs[0];；TI_REAL *minus_di = outputs[1];；const TI_REAL per = ((TI_REAL)period-1) / ((TI_REAL)period);；for (i = 1; i < period; ++i) {；atr += truerange;；dmup += dp;；dmdown += dm;；for (i = period; i < size; ++i) {；atr = atr * per + truerange;；dmup = dmup * per + dp;；dmdown = dmdown * per + dm;；输出plus_di；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/di.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：DI.plus_di（参数：period）；追踪：PF01053；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_di_plus_di_14d', 'root_function': 'ti_di', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['plus_di', 'minus_di'], 'output_index': 0, 'warmup': 13, 'kernel': 'kernel_b4079c073f089819', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_di_plus_di_14d', {})
class Factor_tulip_di_plus_di_14d(PublicFactor):
    name = 'tulip_di_plus_di_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；const TI_REAL *close = inputs[2];；TI_REAL *plus_di = outputs[0];；TI_REAL *minus_di = outputs[1];；const TI_REAL per = ((TI_REAL)period-1) / ((TI_REAL)period);；for (i = 1; i < period; ++i) {；atr += truerange;；dmup += dp;；dmdown += dm;；for (i = period; i < size; ++i) {；atr = atr * per + truerange;；dmup = dmup * per + dp;；dmdown = dmdown * per + dm;；输出plus_di；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/di.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：DI.plus_di（参数：period）；追踪：PF01053；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
