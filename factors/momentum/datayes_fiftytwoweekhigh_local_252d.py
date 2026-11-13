"""通联 DataYes／优矿424因子库

公式：C/HHV(C,252)，输出距一年最高收盘价的比值。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：FiftyTwoWeekHigh；追踪：DY0268；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_fiftytwoweekhigh_local_252d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'fifty_two_high', 'n': 252, 'output': 0}, 'supplied_parameters': {'kind': 'fifty_two_high', 'n': 252, 'output': 0}, 'output_index': 0, 'output_label': 'FiftyTwoWeekHigh', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_fiftytwoweekhigh_local_252d', {})
class Factor_datayes_fiftytwoweekhigh_local_252d(PublicFactor):
    name = 'datayes_fiftytwoweekhigh_local_252d'
    description = 'C/HHV(C,252)，输出距一年最高收盘价的比值。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：FiftyTwoWeekHigh；追踪：DY0268；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
