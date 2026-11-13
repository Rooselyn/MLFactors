"""Pandas TA Classic

公式：源码算子/递推链：输出=quantile；输出=None；result_arr[length - 1:] = quantile(windows, q, axis=1)；result_arr[pos] = quantile(values[:pos + 1], q)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/quantile.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'q': 0.5, 'offset': 0}；只输出'QTL_30_0.5'；原目录：quantile（length=30）；追踪：PF01261；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_quantile_qtl_30_0_5_30d', 'root_function': 'f_7487fe34f4_quantile', 'required_inputs': ['close'], 'parameters': {'length': 30, 'q': 0.5, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'QTL_30_0.5', 'gate_bars': 1, 'kernel': 'kernel_266a5ab8465b51d7', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_quantile_qtl_30_0_5_30d', {})
class Factor_ptac_quantile_qtl_30_0_5_30d(PublicFactor):
    name = 'ptac_quantile_qtl_30_0_5_30d'
    description = "源码算子/递推链：输出=quantile；输出=None；result_arr[length - 1:] = quantile(windows, q, axis=1)；result_arr[pos] = quantile(values[:pos + 1], q)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/quantile.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'q': 0.5, 'offset': 0}；只输出'QTL_30_0.5'；原目录：quantile（length=30）；追踪：PF01261；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
