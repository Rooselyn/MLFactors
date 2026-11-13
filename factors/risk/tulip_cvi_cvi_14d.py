"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *output = outputs[0];；const TI_REAL per = 2 / ((TI_REAL)period + 1);；ti_buffer *lag = ti_buffer_new(period);；for (i = 1; i < period*2-1; ++i) {；val = ((high[i]-low[i])-val) * per + val;；for (i = period*2-1; i < size; ++i) {；输出cvi；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/cvi.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：CVI.cvi（参数：period）；追踪：PF01051；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'tulip_cvi_cvi_14d', 'root_function': 'ti_cvi', 'required_inputs': ['high', 'low'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['cvi'], 'output_index': 0, 'warmup': 27, 'kernel': 'kernel_7b21310e655a46fe', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_cvi_cvi_14d', {})
class Factor_tulip_cvi_cvi_14d(PublicFactor):
    name = 'tulip_cvi_cvi_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *output = outputs[0];；const TI_REAL per = 2 / ((TI_REAL)period + 1);；ti_buffer *lag = ti_buffer_new(period);；for (i = 1; i < period*2-1; ++i) {；val = ((high[i]-low[i])-val) * per + val;；for (i = period*2-1; i < size; ++i) {；输出cvi；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/cvi.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：CVI.cvi（参数：period）；追踪：PF01051；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
