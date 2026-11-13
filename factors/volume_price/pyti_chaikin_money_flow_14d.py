"""PyTI

公式：完整数值定义为附录独立函数pyti_chaikin_money_flow_chaikin_money_flow；固定参数={'period': 14}；原目录定义：sum(V×(2C−H−L)/(H−L),n)/sum(V,n)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/chaikin_money_flow.py#L6)；原目录：chaikin_money_flow.chaikin_money_flow（period等由调用方指定）；追踪：PF01412；[来源](https://github.com/kylejusticemagnuson/pyti)。
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
SPEC = {'name': 'pyti_chaikin_money_flow_14d', 'root_function': 'pyti_chaikin_money_flow_chaikin_money_flow', 'required_inputs': ['close_data', 'high_data', 'low_data', 'volume'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'chaikin_money_flow', 'kernel': 'kernel_585de1b57d0c23b9', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_chaikin_money_flow_14d', {})
class Factor_pyti_chaikin_money_flow_14d(PublicFactor):
    name = 'pyti_chaikin_money_flow_14d'
    description = "完整数值定义为附录独立函数pyti_chaikin_money_flow_chaikin_money_flow；固定参数={'period': 14}；原目录定义：sum(V×(2C−H−L)/(H−L),n)/sum(V,n)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/chaikin_money_flow.py#L6)；原目录：chaikin_money_flow.chaikin_money_flow（period等由调用方指定）；追踪：PF01412；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
