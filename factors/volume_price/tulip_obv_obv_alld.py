"""Tulip Indicators

公式：OBV_t=OBV_{t−1}+sign(ΔC_t)×V_t；平盘/初始值按来源；输出obv；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/obv.c)；参数={}；以下完整数值核为该条目的最终计算定义。；原目录：OBV.obv（参数：none）；追踪：PF01080；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'tulip_obv_obv_alld', 'root_function': 'ti_obv', 'required_inputs': ['close', 'volume'], 'parameters': {}, 'options': [], 'outputs': ['obv'], 'output_index': 0, 'warmup': 0, 'kernel': 'kernel_0c0d6a827334f674', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_obv_obv_alld', {})
class Factor_tulip_obv_obv_alld(PublicFactor):
    name = 'tulip_obv_obv_alld'
    description = 'OBV_t=OBV_{t−1}+sign(ΔC_t)×V_t；平盘/初始值按来源；输出obv；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/obv.c)；参数={}；以下完整数值核为该条目的最终计算定义。；原目录：OBV.obv（参数：none）；追踪：PF01080；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。'
    INPUTS = INPUTS
    SPEC = SPEC
