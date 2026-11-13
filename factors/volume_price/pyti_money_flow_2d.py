"""PyTI

公式：完整数值定义为附录独立函数pyti_money_flow_money_flow；固定参数={}；原目录定义：源码算子/递推链：mf = volume * tp(close_data, high_data, low_data)；输出=mf；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/money_flow.py#L5)；原目录：money_flow.money_flow（period等由调用方指定）；追踪：PF01436；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'pyti_money_flow_2d', 'root_function': 'pyti_money_flow_money_flow', 'required_inputs': ['close_data', 'high_data', 'low_data', 'volume'], 'parameters': {}, 'supplied_parameters': {}, 'output_index': 0, 'output_label': 'money_flow', 'kernel': 'kernel_7da4d493a9482287', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_money_flow_2d', {})
class Factor_pyti_money_flow_2d(PublicFactor):
    name = 'pyti_money_flow_2d'
    description = '完整数值定义为附录独立函数pyti_money_flow_money_flow；固定参数={}；原目录定义：源码算子/递推链：mf = volume * tp(close_data, high_data, low_data)；输出=mf；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/money_flow.py#L5)；原目录：money_flow.money_flow（period等由调用方指定）；追踪：PF01436；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
