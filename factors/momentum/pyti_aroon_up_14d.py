"""PyTI

公式：完整数值定义为附录独立函数pyti_aroon_aroon_up；固定参数={'period': 14}；原目录定义：源码算子/递推链：a_up = [(period - list(reversed(data[idx - period:idx + 1])).index(max(data[idx - period:idx + 1]))) / float(period) * 100 for idx in range(period, len(data))]；输出=a_up；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/aroon.py#L6)；原目录：aroon.aroon_up（period等由调用方指定）；追踪：PF01401；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_aroon_up_14d', 'root_function': 'pyti_aroon_aroon_up', 'required_inputs': ['data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'aroon_up', 'kernel': 'kernel_f4db87645bd1b20b', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_aroon_up_14d', {})
class Factor_pyti_aroon_up_14d(PublicFactor):
    name = 'pyti_aroon_up_14d'
    description = "完整数值定义为附录独立函数pyti_aroon_aroon_up；固定参数={'period': 14}；原目录定义：源码算子/递推链：a_up = [(period - list(reversed(data[idx - period:idx + 1])).index(max(data[idx - period:idx + 1]))) / float(period) * 100 for idx in range(period, len(data))]；输出=a_up；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/aroon.py#L6)；原目录：aroon.aroon_up（period等由调用方指定）；追踪：PF01401；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
