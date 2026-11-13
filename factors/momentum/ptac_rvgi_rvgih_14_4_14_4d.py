"""Pandas TA Classic

公式：源码算子/递推链：high_low_range = high - low；close_open_range = close - open_；numerator = swma(close_open_range, length=swma_length).rolling(length).sum()；denominator = swma(high_low_range, length=swma_length).rolling(length).sum()；rvgi = (numerator / denominator.where(denominator != 0)).mask(denominator == 0, 0.0)；histogram = rvgi - signal；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/rvgi.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'swma_length': 4, 'offset': 0}；只输出'RVGIh_14_4'；原目录：rvgi（length=14）；追踪：PF01205；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_rvgi_rvgih_14_4_14_4d', 'root_function': 'f_02cc89aad1_rvgi', 'required_inputs': ['open_', 'high', 'low', 'close'], 'parameters': {'length': 14, 'swma_length': 4, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'RVGIh_14_4', 'gate_bars': 1, 'kernel': 'kernel_82e38e504cfd1223', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_rvgi_rvgih_14_4_14_4d', {})
class Factor_ptac_rvgi_rvgih_14_4_14_4d(PublicFactor):
    name = 'ptac_rvgi_rvgih_14_4_14_4d'
    description = "源码算子/递推链：high_low_range = high - low；close_open_range = close - open_；numerator = swma(close_open_range, length=swma_length).rolling(length).sum()；denominator = swma(high_low_range, length=swma_length).rolling(length).sum()；rvgi = (numerator / denominator.where(denominator != 0)).mask(denominator == 0, 0.0)；histogram = rvgi - signal；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/rvgi.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'swma_length': 4, 'offset': 0}；只输出'RVGIh_14_4'；原目录：rvgi（length=14）；追踪：PF01205；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
