"""Tulip Indicators

公式：sum(C×V,n)/sum(V,n)；输出vwma；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vwma.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：VWMA.vwma（参数：period）；追踪：PF01100；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'tulip_vwma_vwma_20d', 'root_function': 'ti_vwma', 'required_inputs': ['close', 'volume'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['vwma'], 'output_index': 0, 'warmup': 19, 'kernel': 'kernel_58a597f053bf5c60', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_vwma_vwma_20d', {})
class Factor_tulip_vwma_vwma_20d(PublicFactor):
    name = 'tulip_vwma_vwma_20d'
    description = "sum(C×V,n)/sum(V,n)；输出vwma；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vwma.c)；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：VWMA.vwma（参数：period）；追踪：PF01100；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
