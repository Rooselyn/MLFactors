"""Pandas TA Classic

公式：ER=abs(C−C[-n])/Σabs(ΔC)；α=(ER(2/(fast+1)−2/(slow+1))+2/(slow+1))²；K_t=K_{t−1}+α(C_t−K_{t−1})；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/kama.py#L33)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'fast': 2, 'slow': 30, 'talib': False, 'drift': 1, 'offset': 0}；只输出'KAMA_10_2_30'；原目录：kama（length=10, fast=2, slow=30）；追踪：PF01231；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_kama_kama_10_2_30_10_2_30d', 'root_function': 'f_cba8f676b7_kama', 'required_inputs': ['close'], 'parameters': {'length': 10, 'fast': 2, 'slow': 30, 'talib': False, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'KAMA_10_2_30', 'gate_bars': 30, 'kernel': 'kernel_60dd23b12491710c', 'engine': 'ptac', 'minimum': 30}

@register_factor
@fixed_factor('ptac_kama_kama_10_2_30_10_2_30d', {})
class Factor_ptac_kama_kama_10_2_30_10_2_30d(PublicFactor):
    name = 'ptac_kama_kama_10_2_30_10_2_30d'
    description = "ER=abs(C−C[-n])/Σabs(ΔC)；α=(ER(2/(fast+1)−2/(slow+1))+2/(slow+1))²；K_t=K_{t−1}+α(C_t−K_{t−1})；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/kama.py#L33)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'fast': 2, 'slow': 30, 'talib': False, 'drift': 1, 'offset': 0}；只输出'KAMA_10_2_30'；原目录：kama（length=10, fast=2, slow=30）；追踪：PF01231；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
