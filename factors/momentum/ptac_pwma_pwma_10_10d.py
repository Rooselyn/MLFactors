"""Pandas TA Classic

公式：源码算子/递推链：triangle = pascals_triangle(n=length - 1, weighted=True)；输出=pwma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/pwma.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0}；只输出'PWMA_10'；原目录：pwma（length=10）；追踪：PF01239；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_pwma_pwma_10_10d', 'root_function': 'f_530df50555_pwma', 'required_inputs': ['close'], 'parameters': {'length': 10, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PWMA_10', 'gate_bars': 1, 'kernel': 'kernel_791b40da100a5fac', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_pwma_pwma_10_10d', {})
class Factor_ptac_pwma_pwma_10_10d(PublicFactor):
    name = 'ptac_pwma_pwma_10_10d'
    description = "源码算子/递推链：triangle = pascals_triangle(n=length - 1, weighted=True)；输出=pwma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/pwma.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0}；只输出'PWMA_10'；原目录：pwma（length=10）；追踪：PF01239；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
