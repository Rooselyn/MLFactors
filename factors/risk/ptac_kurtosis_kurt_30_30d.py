"""Pandas TA Classic

公式：E[(C−μ)^4]/σ^4；超额峰度是否减3按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/kurtosis.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'offset': 0}；只输出'KURT_30'；原目录：kurtosis（length=30）；追踪：PF01258；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_kurtosis_kurt_30_30d', 'root_function': 'f_a590e78f12_kurtosis', 'required_inputs': ['close'], 'parameters': {'length': 30, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'KURT_30', 'gate_bars': 1, 'kernel': 'kernel_58a9ba24956bf99e', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_kurtosis_kurt_30_30d', {})
class Factor_ptac_kurtosis_kurt_30_30d(PublicFactor):
    name = 'ptac_kurtosis_kurt_30_30d'
    description = "E[(C−μ)^4]/σ^4；超额峰度是否减3按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/kurtosis.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'offset': 0}；只输出'KURT_30'；原目录：kurtosis（length=30）；追踪：PF01258；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
