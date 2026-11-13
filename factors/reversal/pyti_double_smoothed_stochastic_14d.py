"""PyTI

公式：完整数值定义为附录独立函数pyti_double_smoothed_stochastic_double_smoothed_stochastic；固定参数={'period': 14}；原目录定义：源码算子/递推链：lows = [data[idx] - min(data[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(data))]；highs = [max(data[idx + 1 - period:idx + 1]) - min(data[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(data))]；dss = sm_lows / sm_highs * 100；输出=dss；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/double_smoothed_stochastic.py#L9)；原目录：double_smoothed_stochastic.double_smoothed_stochastic（period等由调用方指定）；追踪：PF01424；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_double_smoothed_stochastic_14d', 'root_function': 'pyti_double_smoothed_stochastic_double_smoothed_stochastic', 'required_inputs': ['data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'double_smoothed_stochastic', 'kernel': 'kernel_36ebeec7ea50e69f', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_double_smoothed_stochastic_14d', {})
class Factor_pyti_double_smoothed_stochastic_14d(PublicFactor):
    name = 'pyti_double_smoothed_stochastic_14d'
    description = "完整数值定义为附录独立函数pyti_double_smoothed_stochastic_double_smoothed_stochastic；固定参数={'period': 14}；原目录定义：源码算子/递推链：lows = [data[idx] - min(data[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(data))]；highs = [max(data[idx + 1 - period:idx + 1]) - min(data[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(data))]；dss = sm_lows / sm_highs * 100；输出=dss；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/double_smoothed_stochastic.py#L9)；原目录：double_smoothed_stochastic.double_smoothed_stochastic（period等由调用方指定）；追踪：PF01424；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
