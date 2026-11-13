"""Pandas TA Classic

公式：C[t−floor(n/2)−1]−mean(C,n)；用于时点t，不能将此输出回填到较早日期；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/dpo.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'centered': False, 'offset': 0}；只输出'DPO_20'；原目录：dpo（length=20）；追踪：PF01277；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_dpo_dpo_20_20d', 'root_function': 'f_e63d4642d1_dpo', 'required_inputs': ['close'], 'parameters': {'length': 20, 'centered': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'DPO_20', 'gate_bars': 1, 'kernel': 'kernel_f6dce2cc981d78b2', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_dpo_dpo_20_20d', {})
class Factor_ptac_dpo_dpo_20_20d(PublicFactor):
    name = 'ptac_dpo_dpo_20_20d'
    description = "C[t−floor(n/2)−1]−mean(C,n)；用于时点t，不能将此输出回填到较早日期；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/dpo.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'centered': False, 'offset': 0}；只输出'DPO_20'；原目录：dpo（length=20）；追踪：PF01277；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
