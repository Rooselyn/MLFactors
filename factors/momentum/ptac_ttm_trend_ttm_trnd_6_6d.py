"""Pandas TA Classic

公式：源码算子/递推链：trend_avg = hl2(high, low).shift(1).rolling(length).mean()；tm_trend = ((close > trend_avg).astype(int) * 2 - 1).where(trend_avg.notna() & close.notna())；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/ttm_trend.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 6, 'offset': 0}；只输出'TTM_TRND_6'；原目录：ttm_trend（length=6）；追踪：PF01289；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_ttm_trend_ttm_trnd_6_6d', 'root_function': 'f_cfd74e41c5_ttm_trend', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'length': 6, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'TTM_TRND_6', 'gate_bars': 1, 'kernel': 'kernel_b429c4afa843c834', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_ttm_trend_ttm_trnd_6_6d', {})
class Factor_ptac_ttm_trend_ttm_trnd_6_6d(PublicFactor):
    name = 'ptac_ttm_trend_ttm_trnd_6_6d'
    description = "源码算子/递推链：trend_avg = hl2(high, low).shift(1).rolling(length).mean()；tm_trend = ((close > trend_avg).astype(int) * 2 - 1).where(trend_avg.notna() & close.notna())；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/ttm_trend.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 6, 'offset': 0}；只输出'TTM_TRND_6'；原目录：ttm_trend（length=6）；追踪：PF01289；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
