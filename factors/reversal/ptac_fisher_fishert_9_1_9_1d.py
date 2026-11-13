"""Pandas TA Classic

公式：X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/fisher.py#L36)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 9, 'signal': 1, 'offset': 0}；只输出'FISHERT_9_1'；原目录：fisher（length=9, signal=1）；追踪：PF01188；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ptac_fisher_fishert_9_1_9_1d', 'root_function': 'f_2beb0b229f_fisher', 'required_inputs': ['high', 'low'], 'parameters': {'length': 9, 'signal': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'FISHERT_9_1', 'gate_bars': 1, 'kernel': 'kernel_d0dcb3b2d1646dbb', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_fisher_fishert_9_1_9_1d', {})
class Factor_ptac_fisher_fishert_9_1_9_1d(PublicFactor):
    name = 'ptac_fisher_fishert_9_1_9_1d'
    description = "X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/fisher.py#L36)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 9, 'signal': 1, 'offset': 0}；只输出'FISHERT_9_1'；原目录：fisher（length=9, signal=1）；追踪：PF01188；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
