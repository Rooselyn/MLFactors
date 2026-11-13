"""通联 DataYes／优矿424因子库

公式：DIF=EMA12(C)−EMA26(C)；DEA=EMA9(DIF)；MACD=2×(DIF−DEA)；EMA均首值种子adjust=False，最后统一除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：DIF；追踪：DY0078；[来源](https://uqer.datayes.com/help/appendixFactors/)。；同定义来源别名：通联 DataYes／优矿424因子库:DIFF
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_dif_local_12_26_9d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'macd', 'n': 0, 'output': 0}, 'supplied_parameters': {'kind': 'macd', 'n': 0, 'output': 0}, 'output_index': 0, 'output_label': 'DIF', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_dif_local_12_26_9d', {})
class Factor_datayes_dif_local_12_26_9d(PublicFactor):
    name = 'datayes_dif_local_12_26_9d'
    description = 'DIF=EMA12(C)−EMA26(C)；DEA=EMA9(DIF)；MACD=2×(DIF−DEA)；EMA均首值种子adjust=False，最后统一除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：DIF；追踪：DY0078；[来源](https://uqer.datayes.com/help/appendixFactors/)。；同定义来源别名：通联 DataYes／优矿424因子库:DIFF'
    INPUTS = INPUTS
    SPEC = SPEC
