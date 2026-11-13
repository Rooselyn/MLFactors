"""通联 DataYes／优矿424因子库

公式：(mean(C,3)+mean(C,6)+mean(C,12)+mean(C,24))/4/当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：BBI；追踪：DY0320；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_bbi_local_3_6_12_24d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'bbi', 'n': 0, 'output': 0}, 'supplied_parameters': {'kind': 'bbi', 'n': 0, 'output': 0}, 'output_index': 0, 'output_label': 'BBI', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_bbi_local_3_6_12_24d', {})
class Factor_datayes_bbi_local_3_6_12_24d(PublicFactor):
    name = 'datayes_bbi_local_3_6_12_24d'
    description = '(mean(C,3)+mean(C,6)+mean(C,12)+mean(C,24))/4/当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：BBI；追踪：DY0320；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
