"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；const TI_REAL *close = inputs[2];；TI_REAL *output = outputs[0];；for (i = 1; i < size; ++i) {；sum += c - MIN(yc, low[i]);；sum += c - MAX(yc, high[i]);；输出wad；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/wad.c)；参数={}；以下完整数值核为该条目的最终计算定义。；原目录：WAD.wad（参数：none）；追踪：PF01101；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
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
SPEC = {'name': 'tulip_wad_wad_alld', 'root_function': 'ti_wad', 'required_inputs': ['high', 'low', 'close'], 'parameters': {}, 'options': [], 'outputs': ['wad'], 'output_index': 0, 'warmup': 1, 'kernel': 'kernel_edecf471335a8af7', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_wad_wad_alld', {})
class Factor_tulip_wad_wad_alld(PublicFactor):
    name = 'tulip_wad_wad_alld'
    description = '源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；const TI_REAL *close = inputs[2];；TI_REAL *output = outputs[0];；for (i = 1; i < size; ++i) {；sum += c - MIN(yc, low[i]);；sum += c - MAX(yc, high[i]);；输出wad；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/wad.c)；参数={}；以下完整数值核为该条目的最终计算定义。；原目录：WAD.wad（参数：none）；追踪：PF01101；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。'
    INPUTS = INPUTS
    SPEC = SPEC
