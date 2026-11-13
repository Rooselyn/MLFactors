"""Tulip Indicators

公式：源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *output = outputs[0];；for (i = 1; i < size; ++i) {；sar = (extreme - sar) * accel + sar;；accel += accel_step;；输出psar；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/psar.c)；参数={'acceleration_factor_step': 0.02, 'acceleration_factor_maximum': 0.2}；以下完整数值核为该条目的最终计算定义。；原目录：PSAR.psar（参数：acceleration_factor_step, acceleration_factor_maximum）；追踪：PF01082；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'tulip_psar_psar_alld', 'root_function': 'ti_psar', 'required_inputs': ['high', 'low'], 'parameters': {'acceleration_factor_step': 0.02, 'acceleration_factor_maximum': 0.2}, 'options': [0.02, 0.2], 'outputs': ['psar'], 'output_index': 0, 'warmup': 1, 'kernel': 'kernel_bb5d0afcb63e6f59', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_psar_psar_alld', {})
class Factor_tulip_psar_psar_alld(PublicFactor):
    name = 'tulip_psar_psar_alld'
    description = "源码核心递推表达式（完整分支/参数见链接）：const TI_REAL *high = inputs[0];；const TI_REAL *low = inputs[1];；TI_REAL *output = outputs[0];；for (i = 1; i < size; ++i) {；sar = (extreme - sar) * accel + sar;；accel += accel_step;；输出psar；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/psar.c)；参数={'acceleration_factor_step': 0.02, 'acceleration_factor_maximum': 0.2}；以下完整数值核为该条目的最终计算定义。；原目录：PSAR.psar（参数：acceleration_factor_step, acceleration_factor_maximum）；追踪：PF01082；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。"
    INPUTS = INPUTS
    SPEC = SPEC
