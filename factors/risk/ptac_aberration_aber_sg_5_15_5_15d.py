"""Pandas TA Classic

公式：源码算子/递推链：sg = zg + atr_；xg = zg - atr_；输出=aberdf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/aberration.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 5, 'atr_length': 15, 'offset': 0}；只输出'ABER_SG_5_15'；原目录：aberration（length=5）；追踪：PF01293；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_aberration_aber_sg_5_15_5_15d', 'root_function': 'f_d7b1f23a34_aberration', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'length': 5, 'atr_length': 15, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'ABER_SG_5_15', 'gate_bars': 1, 'kernel': 'kernel_b6f3b2da8085734d', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_aberration_aber_sg_5_15_5_15d', {})
class Factor_ptac_aberration_aber_sg_5_15_5_15d(PublicFactor):
    name = 'ptac_aberration_aber_sg_5_15_5_15d'
    description = "源码算子/递推链：sg = zg + atr_；xg = zg - atr_；输出=aberdf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/aberration.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 5, 'atr_length': 15, 'offset': 0}；只输出'ABER_SG_5_15'；原目录：aberration（length=5）；追踪：PF01293；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
