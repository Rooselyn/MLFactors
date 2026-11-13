"""Pandas TA Classic

公式：源码算子/递推链：po = 100 * (close - lr) / lr.replace(0, float('nan'))；输出=po；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/po.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'offset': 0}；只输出'PO_14'；原目录：po（length=14）；追踪：PF01198；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_po_po_14_14d', 'root_function': 'f_cba40d7e56_po', 'required_inputs': ['close'], 'parameters': {'length': 14, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PO_14', 'gate_bars': 1, 'kernel': 'kernel_944fcc4cf0c03152', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_po_po_14_14d', {})
class Factor_ptac_po_po_14_14d(PublicFactor):
    name = 'ptac_po_po_14_14d'
    description = "源码算子/递推链：po = 100 * (close - lr) / lr.replace(0, float('nan'))；输出=po；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/po.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'offset': 0}；只输出'PO_14'；原目录：po（length=14）；追踪：PF01198；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
