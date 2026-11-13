"""Tulip Indicators

公式：(max(C,n)−min(C,n))/sum(abs(ΔC),n)；输出vhf；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vhf.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：VHF.vhf（参数：period）；追踪：PF01096；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_vhf_vhf_14d', 'root_function': 'ti_vhf', 'required_inputs': ['real'], 'parameters': {'period': 14}, 'options': [14], 'outputs': ['vhf'], 'output_index': 0, 'warmup': 14, 'kernel': 'kernel_e8769201a868c9f2', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_vhf_vhf_14d', {})
class Factor_tulip_vhf_vhf_14d(PublicFactor):
    name = 'tulip_vhf_vhf_14d'
    description = "(max(C,n)−min(C,n))/sum(abs(ΔC),n)；输出vhf；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/vhf.c)；参数={'period': 14}；以下完整数值核为该条目的最终计算定义。；原目录：VHF.vhf（参数：period）；追踪：PF01096；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
