"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *plus_dm = outputs[0];；TI_REAL *minus_dm = outputs[1];；const TI_REAL per = ((TI_REAL)period-1) / ((TI_REAL)period);；for (i = 1; i < period; ++i) {；dmup += dp;；dmdown += dm;；for (i = period; i < size; ++i) {；dmup = dmup * per + dp;；dmdown = dmdown * per + dm;；输出minus_dm；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/dm.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：DM.minus_dm（参数：period）；追踪：PF01056；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'tulip_dm_minus_dm_14d', 'root_function': 'ti_dm', 'required_inputs': ['high', 'low'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['plus_dm', 'minus_dm'], 'output_index': 1, 'warmup': 13, 'kernel': 'kernel_b4766f8dbd1eba0c', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_dm_minus_dm_14d', {})
class Factor_tulip_dm_minus_dm_14d(PublicFactor):
    name = 'tulip_dm_minus_dm_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *plus_dm = outputs[0];；TI_REAL *minus_dm = outputs[1];；const TI_REAL per = ((TI_REAL)period-1) / ((TI_REAL)period);；for (i = 1; i < period; ++i) {；dmup += dp;；dmdown += dm;；for (i = period; i < size; ++i) {；dmup = dmup * per + dp;；dmdown = dmdown * per + dm;；输出minus_dm；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/dm.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：DM.minus_dm（参数：period）；追踪：PF01056；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
