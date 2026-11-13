"""Tulip Indicators

公式：((H+L)/2−(H[-1]+L[-1])/2)×(H−L)/V；成交量缩放及平滑按来源；输出emv；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/emv.c)；参数={}；以下完整数值核为该条目的最终计算定义。；原目录：EMV.emv（参数：none）；追踪：PF01060；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。；同定义来源别名：Pandas TA Classic:emv（drift=None）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'tulip_emv_emv_2d', 'root_function': 'ti_emv', 'required_inputs': ['high', 'low', 'volume'], 'parameters': {}, 'options': [], 'outputs': ['emv'], 'output_index': 0, 'warmup': 1, 'kernel': 'kernel_2b3ef21071231abb', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_emv_emv_2d', {})
class Factor_tulip_emv_emv_2d(PublicFactor):
    name = 'tulip_emv_emv_2d'
    description = '((H+L)/2−(H[-1]+L[-1])/2)×(H−L)/V；成交量缩放及平滑按来源；输出emv；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/emv.c)；参数={}；以下完整数值核为该条目的最终计算定义。；原目录：EMV.emv（参数：none）；追踪：PF01060；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。；同定义来源别名：Pandas TA Classic:emv（drift=None）'
    INPUTS = INPUTS
    SPEC = SPEC
