"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *sine = outputs[0];；TI_REAL *lead = outputs[1];；const TI_REAL tpi = 2 * pi;；for (i = period; i < size; ++i) {；for (j = 0; j < period; ++j) {；rp = rp + cos(tpi * j / period) * weight;；ip = ip + sin(tpi * j / period) * weight;；phase = atan(ip/rp);；phase = tpi / 2.0 * (ip < 0 ? -1.0 : 1.0);；if (rp < 0.0) phase += pi;；phase += pi/2.0;；if (phase < 0.0) phase += tpi;；输出msw_sine；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/msw.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：MSW.msw_sine（参数：period）；追踪：PF01076；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_msw_msw_sine_14d', 'root_function': 'ti_msw', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['msw_sine', 'msw_lead'], 'output_index': 0, 'warmup': 14, 'kernel': 'kernel_f3c849535be80b4b', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_msw_msw_sine_14d', {})
class Factor_tulip_msw_msw_sine_14d(PublicFactor):
    name = 'tulip_msw_msw_sine_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *input = inputs[0];；TI_REAL *sine = outputs[0];；TI_REAL *lead = outputs[1];；const TI_REAL tpi = 2 * pi;；for (i = period; i < size; ++i) {；for (j = 0; j < period; ++j) {；rp = rp + cos(tpi * j / period) * weight;；ip = ip + sin(tpi * j / period) * weight;；phase = atan(ip/rp);；phase = tpi / 2.0 * (ip < 0 ? -1.0 : 1.0);；if (rp < 0.0) phase += pi;；phase += pi/2.0;；if (phase < 0.0) phase += tpi;；输出msw_sine；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/msw.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：MSW.msw_sine（参数：period）；追踪：PF01076；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
