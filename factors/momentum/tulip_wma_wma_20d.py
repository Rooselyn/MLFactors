"""Tulip Indicators

公式：Σ_{j=0…n−1}(n−j)C[t−j]/(n(n+1)/2)；n=N，周期由调用方指定；本条为参数化定义，不能当作任意固定窗口已实现；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：WMA.wma（参数：period）；追踪：PF01104；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。；同定义来源别名：PyTI:linear_weighted_moving_average.linear_weighted_moving_average（period等由调用方指定）、PyTI:weighted_moving_average.weighted_moving_average（period等由调用方指定）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tulip_wma_wma_20d', 'root_function': 'ti_wma', 'required_inputs': ['real'], 'parameters': {'period': 20}, 'options': [20], 'outputs': ['wma'], 'output_index': 0, 'warmup': 19, 'kernel': 'kernel_419d14dfd451624e', 'engine': 'tulip', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('tulip_wma_wma_20d', {})
class Factor_tulip_wma_wma_20d(PublicFactor):
    name = 'tulip_wma_wma_20d'
    description = "Σ_{j=0…n−1}(n−j)C[t−j]/(n(n+1)/2)；n=N，周期由调用方指定；本条为参数化定义，不能当作任意固定窗口已实现；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；参数={'period': 20}；以下完整数值核为该条目的最终计算定义。；原目录：WMA.wma（参数：period）；追踪：PF01104；[来源](https://github.com/TulipCharts/tulipindicators/blob/be18abb13e075ba866898dcc7cb52399603302a6/indicators.h)。；同定义来源别名：PyTI:linear_weighted_moving_average.linear_weighted_moving_average（period等由调用方指定）、PyTI:weighted_moving_average.weighted_moving_average（period等由调用方指定）"
    INPUTS = INPUTS
    SPEC = SPEC
