"""通联 DataYes／优矿424因子库

公式：最近20个简单日收益的无偏偏度，使用Pandas rolling(20,min_periods=20).skew()。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：Skewness；追踪：DY0299；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_skewness_local_20d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'skew', 'n': 20, 'output': 0}, 'supplied_parameters': {'kind': 'skew', 'n': 20, 'output': 0}, 'output_index': 0, 'output_label': 'Skewness', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_skewness_local_20d', {})
class Factor_datayes_skewness_local_20d(PublicFactor):
    name = 'datayes_skewness_local_20d'
    description = '最近20个简单日收益的无偏偏度，使用Pandas rolling(20,min_periods=20).skew()。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：Skewness；追踪：DY0299；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
