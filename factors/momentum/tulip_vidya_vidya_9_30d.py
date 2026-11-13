"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL short_div = 1.0 / short_period;；const TI_REAL long_div = 1.0 / long_period;；for (i = 0; i < long_period; ++i) {；long_sum += input[i];；long_sum2 += input[i] * input[i];；short_sum += input[i];；short_sum2 += input[i] * input[i];；TI_REAL short_stddev = sqrt(short_sum2 * short_div - (short_sum * short_div) * (short_sum * short_div));；TI_REAL long_stddev = sqrt(long_sum2 * long_div - (long_sum * long_div) * (long_sum * long_div));；TI_REAL k = short_stddev / long_stddev;；if (k != k) k = 0; /* In some conditions it works out that we take the sqrt(-0.0), which gives NaN.；k *= alpha;；输出vidya；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vidya.c)；参数={'short_period': 9, 'long_period': 30, 'alpha': 0.2}；以下完整数值核为该条目的最终计算定义。；原目录：VIDYA.vidya（参数：short_period, long_period, alpha）；追踪：PF01097；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_vidya_vidya_9_30d', 'root_function': 'ti_vidya', 'required_inputs': ['real'], 'parameters': {'short_period': 9, 'long_period': 30, 'alpha': 0.2}, 'options': [9, 30, 0.2], 'outputs': ['vidya'], 'output_index': 0, 'warmup': 28, 'kernel': 'kernel_5917830facb05a18', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_vidya_vidya_9_30d', {})
class Factor_tulip_vidya_vidya_9_30d(PublicFactor):
    name = 'tulip_vidya_vidya_9_30d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *output = outputs[0];；const TI_REAL short_div = 1.0 / short_period;；const TI_REAL long_div = 1.0 / long_period;；for (i = 0; i < long_period; ++i) {；long_sum += input[i];；long_sum2 += input[i] * input[i];；short_sum += input[i];；short_sum2 += input[i] * input[i];；TI_REAL short_stddev = sqrt(short_sum2 * short_div - (short_sum * short_div) * (short_sum * short_div));；TI_REAL long_stddev = sqrt(long_sum2 * long_div - (long_sum * long_div) * (long_sum * long_div));；TI_REAL k = short_stddev / long_stddev;；if (k != k) k = 0; /* In some conditions it works out that we take the sqrt(-0.0), which gives NaN.；k *= alpha;；输出vidya；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vidya.c)；参数={'short_period': 9, 'long_period': 30, 'alpha': 0.2}；以下完整数值核为该条目的最终计算定义。；原目录：VIDYA.vidya（参数：short_period, long_period, alpha）；追踪：PF01097；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
