"""Pandas TA Classic

公式：源码算子/递推链：swing_low = low.rolling(window=length).min().shift(1)；swing_high = high.rolling(window=length).max().shift(1)；body = (close - open_).abs()；lower_wick = oc.min(axis=1) - low；upper_wick = high - oc.max(axis=1)；bull_sweep = where((low < swing_low) & (close > swing_low) & (close > open_) & (lower_wick > body * wick_mult), 1, 0)；bear_sweep = where((high > swing_high) & (close < swing_high) & (close < open_) & (upper_wick > body * wick_mult), -1, 0)；result = Series(bull_sweep + bear_sweep, index=close.index)；输出=result；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/smc_sweep.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 15, 'wick_mult': 1.5, 'offset': 0}；只输出'SMC_SWEEP_15_1.5'；原目录：smc_sweep（length=15）；追踪：PF01207；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_smc_sweep_smc_sweep_15_1_5_15d', 'root_function': 'f_4f0389d840_smc_sweep', 'required_inputs': ['open_', 'high', 'low', 'close'], 'parameters': {'length': 15, 'wick_mult': 1.5, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'SMC_SWEEP_15_1.5', 'gate_bars': 1, 'kernel': 'kernel_e2742305b40339e2', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_smc_sweep_smc_sweep_15_1_5_15d', {})
class Factor_ptac_smc_sweep_smc_sweep_15_1_5_15d(PublicFactor):
    name = 'ptac_smc_sweep_smc_sweep_15_1_5_15d'
    description = "源码算子/递推链：swing_low = low.rolling(window=length).min().shift(1)；swing_high = high.rolling(window=length).max().shift(1)；body = (close - open_).abs()；lower_wick = oc.min(axis=1) - low；upper_wick = high - oc.max(axis=1)；bull_sweep = where((low < swing_low) & (close > swing_low) & (close > open_) & (lower_wick > body * wick_mult), 1, 0)；bear_sweep = where((high > swing_high) & (close < swing_high) & (close < open_) & (upper_wick > body * wick_mult), -1, 0)；result = Series(bull_sweep + bear_sweep, index=close.index)；输出=result；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/smc_sweep.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 15, 'wick_mult': 1.5, 'offset': 0}；只输出'SMC_SWEEP_15_1.5'；原目录：smc_sweep（length=15）；追踪：PF01207；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
