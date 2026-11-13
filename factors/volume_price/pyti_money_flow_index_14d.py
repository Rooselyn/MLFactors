"""PyTI

公式：完整数值定义为附录独立函数pyti_money_flow_index_money_flow_index；固定参数={'period': 14}；原目录定义：源码算子/递推链：pf = [mf[idx] if tp[idx] > tp[idx - 1] else 0 for idx in range(1, len(tp))]；nf = [mf[idx] if tp[idx] < tp[idx - 1] else 0 for idx in range(1, len(tp))]；pmf = [sum(pf[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(pf))]；nmf = [sum(nf[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(nf))]；mfi = 100 - 100 / (1 + money_ratio)；输出=mfi；money_ratio = array(pmf) / array(nmf)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/money_flow_index.py#L9)；原目录：money_flow_index.money_flow_index（period等由调用方指定）；追踪：PF01437；[来源](https://github.com/kylejusticemagnuson/pyti)。
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
SPEC = {'name': 'pyti_money_flow_index_14d', 'root_function': 'pyti_money_flow_index_money_flow_index', 'required_inputs': ['close_data', 'high_data', 'low_data', 'volume'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'money_flow_index', 'kernel': 'kernel_f069ed36105c376c', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_money_flow_index_14d', {})
class Factor_pyti_money_flow_index_14d(PublicFactor):
    name = 'pyti_money_flow_index_14d'
    description = "完整数值定义为附录独立函数pyti_money_flow_index_money_flow_index；固定参数={'period': 14}；原目录定义：源码算子/递推链：pf = [mf[idx] if tp[idx] > tp[idx - 1] else 0 for idx in range(1, len(tp))]；nf = [mf[idx] if tp[idx] < tp[idx - 1] else 0 for idx in range(1, len(tp))]；pmf = [sum(pf[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(pf))]；nmf = [sum(nf[idx + 1 - period:idx + 1]) for idx in range(period - 1, len(nf))]；mfi = 100 - 100 / (1 + money_ratio)；输出=mfi；money_ratio = array(pmf) / array(nmf)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/money_flow_index.py#L9)；原目录：money_flow_index.money_flow_index（period等由调用方指定）；追踪：PF01437；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
