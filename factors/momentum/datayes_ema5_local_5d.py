"""通联 DataYes／优矿424因子库

公式：EMA_n从首个有效值种子，以alpha=2/(n+1)、adjust=False递推；最终除当日adj_factor，输出信号日锚定的前复权价格水平。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：EMA5；追踪：DY0327；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_ema5_local_5d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'ema', 'n': 5, 'output': 0}, 'supplied_parameters': {'kind': 'ema', 'n': 5, 'output': 0}, 'output_index': 0, 'output_label': 'EMA5', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_ema5_local_5d', {})
class Factor_datayes_ema5_local_5d(PublicFactor):
    name = 'datayes_ema5_local_5d'
    description = 'EMA_n从首个有效值种子，以alpha=2/(n+1)、adjust=False递推；最终除当日adj_factor，输出信号日锚定的前复权价格水平。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：EMA5；追踪：DY0327；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
