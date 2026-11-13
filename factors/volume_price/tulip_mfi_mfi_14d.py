"""Tulip Indicators

公式：TP=(H+L+C)/3，MF=TP×V；100−100/(1+sum(MF·I(ΔTP>0),n)/sum(MF·I(ΔTP<0),n))；输出mfi；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/mfi.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：MFI.mfi（参数：period）；追踪：PF01074；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
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
SPEC = {'name': 'tulip_mfi_mfi_14d', 'root_function': 'ti_mfi', 'required_inputs': ['high', 'low', 'close', 'volume'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['mfi'], 'output_index': 0, 'warmup': 14, 'kernel': 'kernel_b4a8440f613ccf77', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_mfi_mfi_14d', {})
class Factor_tulip_mfi_mfi_14d(PublicFactor):
    name = 'tulip_mfi_mfi_14d'
    description = "TP=(H+L+C)/3，MF=TP×V；100−100/(1+sum(MF·I(ΔTP>0),n)/sum(MF·I(ΔTP<0),n))；输出mfi；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/mfi.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：MFI.mfi（参数：period）；追踪：PF01074；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
