"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *output = outputs[0];；const TI_REAL per = 2 / (9.0 + 1);；ti_buffer *sum = ti_buffer_new(period);；for (i = 0; i < size; ++i) {；ema = ema * per1 + hl * per;；ema2 = ema2 * per1 + ema * per;；输出mass；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/mass.c)；参数={'period': 25}；以下完整数值核为该条目的最终计算定义。；原目录：MASS.mass（参数：period）；追踪：PF01073；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'tulip_mass_mass_25d', 'root_function': 'ti_mass', 'required_inputs': ['high', 'low'], 'parameters': {'period': 25}, 'options': [25], 'outputs': ['mass'], 'output_index': 0, 'warmup': 40, 'kernel': 'kernel_92058d28d158e558', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_mass_mass_25d', {})
class Factor_tulip_mass_mass_25d(PublicFactor):
    name = 'tulip_mass_mass_25d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *output = outputs[0];；const TI_REAL per = 2 / (9.0 + 1);；ti_buffer *sum = ti_buffer_new(period);；for (i = 0; i < size; ++i) {；ema = ema * per1 + hl * per;；ema2 = ema2 * per1 + ema * per;；输出mass；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/mass.c)；参数={'period': 25}；以下完整数值核为该条目的最终计算定义。；原目录：MASS.mass（参数：period）；追踪：PF01073；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
