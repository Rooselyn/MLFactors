"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；const TI_REAL *close = inputs[2];；const TI_REAL *volume = inputs[3];；const TI_REAL short_per = 2 / ((TI_REAL)short_period + 1);；const TI_REAL long_per = 2 / ((TI_REAL)long_period + 1);；TI_REAL *output = outputs[0];；TI_REAL prev_hlc = high[0] + low[0] + close[0];；for (i = 1; i < size; ++i) {；const TI_REAL hlc = high[i] + low[i] + close[i];；cm += dm;；const TI_REAL vf = volume[i] * fabs(dm / cm * 2 - 1) * 100 * (trend ? 1.0 : -1.0);；short_ema = (vf-short_ema) * short_per + short_ema;；long_ema = (vf-long_ema) * long_per + long_ema;；输出kvo；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/kvo.c)；参数={'short_period': 34, 'long_period': 55}；以下完整数值核为该条目的最终计算定义。；原目录：KVO.kvo（参数：short_period, long_period）；追踪：PF01066；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'tulip_kvo_kvo_34_55d', 'root_function': 'ti_kvo', 'required_inputs': ['high', 'low', 'close', 'volume'], 'parameters': {'short_period': 34, 'long_period': 55}, 'options': [34, 55], 'outputs': ['kvo'], 'output_index': 0, 'warmup': 1, 'kernel': 'kernel_31af3e9a558ab2a0', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_kvo_kvo_34_55d', {})
class Factor_tulip_kvo_kvo_34_55d(PublicFactor):
    name = 'tulip_kvo_kvo_34_55d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；const TI_REAL *close = inputs[2];；const TI_REAL *volume = inputs[3];；const TI_REAL short_per = 2 / ((TI_REAL)short_period + 1);；const TI_REAL long_per = 2 / ((TI_REAL)long_period + 1);；TI_REAL *output = outputs[0];；TI_REAL prev_hlc = high[0] + low[0] + close[0];；for (i = 1; i < size; ++i) {；const TI_REAL hlc = high[i] + low[i] + close[i];；cm += dm;；const TI_REAL vf = volume[i] * fabs(dm / cm * 2 - 1) * 100 * (trend ? 1.0 : -1.0);；short_ema = (vf-short_ema) * short_per + short_ema;；long_ema = (vf-long_ema) * long_per + long_ema;；输出kvo；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/kvo.c)；参数={'short_period': 34, 'long_period': 55}；以下完整数值核为该条目的最终计算定义。；原目录：KVO.kvo（参数：short_period, long_period）；追踪：PF01066；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
