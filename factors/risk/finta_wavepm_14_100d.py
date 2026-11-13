"""FinTA

公式：固定公开源码默认参数：{'period': 14, 'lookback_period': 100, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：WAVEPM(cls, ohlc: DataFrame, period: int=14, lookback_period: int=100, column: str='close'): ma = ohlc[column].rolling(window=period).mean()<br>std = ohlc[column].rolling(window=period).std(ddof=0)<br>def tanh(x):<br>    two = np.where(x > 0, -2, 2)<br>    what = two * x<br>    ex = np.exp(what)<br>    j = 1 - ex<br>    k = ex - 1<br>    l = np.where(x > 0, j, k)<br>    output = l / (1 + ex)<br>    return output<br>def osc(input_dev, mean, power):<br>    variance = Series(power).rolling(window=lookback_period).sum() / lookback_period<br>    calc_dev = np.sqrt(variance) * mean<br>    y = input_dev / calc_dev<br>    oscLine = tanh(y)<br>    return oscLine<br>dev = 3.2 * std<br>power = np.power(dev / ma, 2)<br>wavepm = osc(dev, ma, power)<br>return pd.Series(wavepm, name='{0} period WAVEPM'.format(period))；原目录：WAVEPM（period=14, lookback_period=100）；追踪：PF01036；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_wavepm_14_100d', 'engine': 'finta', 'root_function': 'TA.WAVEPM', 'parameters': {'period': 14, 'lookback_period': 100, 'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_wavepm_14_100d', {})
class Factor_finta_wavepm_14_100d(PublicFactor):
    name = 'finta_wavepm_14_100d'
    description = "固定公开源码默认参数：{'period': 14, 'lookback_period': 100, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：WAVEPM(cls, ohlc: DataFrame, period: int=14, lookback_period: int=100, column: str='close'): ma = ohlc[column].rolling(window=period).mean()<br>std = ohlc[column].rolling(window=period).std(ddof=0)<br>def tanh(x):<br>    two = np.where(x > 0, -2, 2)<br>    what = two * x<br>    ex = np.exp(what)<br>    j = 1 - ex<br>    k = ex - 1<br>    l = np.where(x > 0, j, k)<br>    output = l / (1 + ex)<br>    return output<br>def osc(input_dev, mean, power):<br>    variance = Series(power).rolling(window=lookback_period).sum() / lookback_period<br>    calc_dev = np.sqrt(variance) * mean<br>    y = input_dev / calc_dev<br>    oscLine = tanh(y)<br>    return oscLine<br>dev = 3.2 * std<br>power = np.power(dev / ma, 2)<br>wavepm = osc(dev, ma, power)<br>return pd.Series(wavepm, name='{0} period WAVEPM'.format(period))；原目录：WAVEPM（period=14, lookback_period=100）；追踪：PF01036；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
