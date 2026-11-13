"""Pandas TA Classic

公式：ΣC[t−n+1+i]exp(−(i−offset(n−1))²/(2(n/sigma)²))/Σ权重；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/alma.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'sigma': 6.0, 'distribution_offset': 0.85, 'offset': 0}；只输出'ALMA_10_6.0_0.85'；原目录：alma（length=10）；追踪：PF01221；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_alma_alma_10_6_0_0_85_10d', 'root_function': 'f_8550f6e43b_alma', 'required_inputs': ['close'], 'parameters': {'length': 10, 'sigma': 6.0, 'distribution_offset': 0.85, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'ALMA_10_6.0_0.85', 'gate_bars': 1, 'kernel': 'kernel_e553771da45438c1', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_alma_alma_10_6_0_0_85_10d', {})
class Factor_ptac_alma_alma_10_6_0_0_85_10d(PublicFactor):
    name = 'ptac_alma_alma_10_6_0_0_85_10d'
    description = "ΣC[t−n+1+i]exp(−(i−offset(n−1))²/(2(n/sigma)²))/Σ权重；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/alma.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'sigma': 6.0, 'distribution_offset': 0.85, 'offset': 0}；只输出'ALMA_10_6.0_0.85'；原目录：alma（length=10）；追踪：PF01221；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
