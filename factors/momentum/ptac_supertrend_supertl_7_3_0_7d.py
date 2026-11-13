"""Pandas TA Classic

公式：基础上下轨=(H+L)/2±kATR(n)；按前轨与前收盘递推最终轨道，收盘穿轨改变方向；输出当时可知轨道；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/supertrend.py#L67)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 7, 'multiplier': 3.0, 'offset': 0}；只输出'SUPERTl_7_3.0'；原目录：supertrend（length=7）；追踪：PF01245；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_supertrend_supertl_7_3_0_7d', 'root_function': 'f_91c63715cd_supertrend', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'length': 7, 'multiplier': 3.0, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'SUPERTl_7_3.0', 'gate_bars': 1, 'kernel': 'kernel_ddd88457cfd8cf7a', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_supertrend_supertl_7_3_0_7d', {})
class Factor_ptac_supertrend_supertl_7_3_0_7d(PublicFactor):
    name = 'ptac_supertrend_supertl_7_3_0_7d'
    description = "基础上下轨=(H+L)/2±kATR(n)；按前轨与前收盘递推最终轨道，收盘穿轨改变方向；输出当时可知轨道；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/supertrend.py#L67)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 7, 'multiplier': 3.0, 'offset': 0}；只输出'SUPERTl_7_3.0'；原目录：supertrend（length=7）；追踪：PF01245；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
