"""Pandas TA Classic

公式：源码算子/递推链：pdist = 2 * (high - low)；pdist += (open_ - close.shift(drift)).abs()；pdist -= (close - open_).abs()；输出=pdist；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/pdist.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'drift': 1, 'offset': 0}；只输出'PDIST'；原目录：pdist（drift=None）；追踪：PF01306；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_pdist_pdist_2d', 'root_function': 'f_6880755d41_pdist', 'required_inputs': ['open_', 'high', 'low', 'close'], 'parameters': {'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PDIST', 'gate_bars': 1, 'kernel': 'kernel_7c576eb429b77d2a', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_pdist_pdist_2d', {})
class Factor_ptac_pdist_pdist_2d(PublicFactor):
    name = 'ptac_pdist_pdist_2d'
    description = "源码算子/递推链：pdist = 2 * (high - low)；pdist += (open_ - close.shift(drift)).abs()；pdist -= (close - open_).abs()；输出=pdist；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/pdist.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'drift': 1, 'offset': 0}；只输出'PDIST'；原目录：pdist（drift=None）；追踪：PF01306；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
