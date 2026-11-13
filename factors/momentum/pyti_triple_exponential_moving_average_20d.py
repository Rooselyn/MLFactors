"""PyTI

公式：完整数值定义为附录独立函数pyti_triple_exponential_moving_average_triple_exponential_moving_average；固定参数={'period': 20}；原目录定义：3EMA(C,n)−3EMA(EMA(C,n),n)+EMA(EMA(EMA(C,n),n),n)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/triple_exponential_moving_average.py#L7)；原目录：triple_exponential_moving_average.triple_exponential_moving_average（period等由调用方指定）；追踪：PF01455；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_triple_exponential_moving_average_20d', 'root_function': 'pyti_triple_exponential_moving_average_triple_exponential_moving_average', 'required_inputs': ['data'], 'parameters': {'period': 20}, 'supplied_parameters': {'period': 20}, 'output_index': 0, 'output_label': 'triple_exponential_moving_average', 'kernel': 'kernel_96fbb32f77497285', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_triple_exponential_moving_average_20d', {})
class Factor_pyti_triple_exponential_moving_average_20d(PublicFactor):
    name = 'pyti_triple_exponential_moving_average_20d'
    description = "完整数值定义为附录独立函数pyti_triple_exponential_moving_average_triple_exponential_moving_average；固定参数={'period': 20}；原目录定义：3EMA(C,n)−3EMA(EMA(C,n),n)+EMA(EMA(EMA(C,n),n),n)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/triple_exponential_moving_average.py#L7)；原目录：triple_exponential_moving_average.triple_exponential_moving_average（period等由调用方指定）；追踪：PF01455；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
