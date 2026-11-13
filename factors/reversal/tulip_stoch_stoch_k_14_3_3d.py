"""Tulip Indicators

公式：FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；SlowK=MA(FastK,k)；SlowD=MA(SlowK,d)；输出stoch_k；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/stoch.c)；参数={'k_period': 14, 'k_slowing_period': 3, 'd_period': 3}；以下完整数值核为该条目的最终计算定义。；原目录：STOCH.stoch_k（参数：k_period, k_slowing_period, d_period）；追踪：PF01088；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。；同定义来源别名：Pandas TA Classic:stoch（mamode='sma'）
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
SPEC = {'name': 'tulip_stoch_stoch_k_14_3_3d', 'root_function': 'ti_stoch', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'k_period': 14, 'k_slowing_period': 3, 'd_period': 3}, 'options': [14, 3, 3], 'outputs': ['stoch_k', 'stoch_d'], 'output_index': 0, 'warmup': 17, 'kernel': 'kernel_60a6b87983b94f4d', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_stoch_stoch_k_14_3_3d', {})
class Factor_tulip_stoch_stoch_k_14_3_3d(PublicFactor):
    name = 'tulip_stoch_stoch_k_14_3_3d'
    description = "FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；SlowK=MA(FastK,k)；SlowD=MA(SlowK,d)；输出stoch_k；[算法](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators/stoch.c)；参数={'k_period': 14, 'k_slowing_period': 3, 'd_period': 3}；以下完整数值核为该条目的最终计算定义。；原目录：STOCH.stoch_k（参数：k_period, k_slowing_period, d_period）；追踪：PF01088；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。；同定义来源别名：Pandas TA Classic:stoch（mamode='sma'）"
    INPUTS = INPUTS
    SPEC = SPEC
