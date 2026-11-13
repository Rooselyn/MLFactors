"""FinTA

公式：固定公开源码默认参数：{'period': 16, 'batch': 10}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：FRAMA(cls, ohlc: DataFrame, period: int=16, batch: int=10): assert period % 2 == 0, print('FRAMA period must be even')<br>c = ohlc.close.copy()<br>window = batch * 2<br>hh = c.rolling(batch).max()<br>ll = c.rolling(batch).min()<br>n1 = (hh - ll) / batch<br>n2 = n1.shift(batch)<br>hh2 = c.rolling(window).max()<br>ll2 = c.rolling(window).min()<br>n3 = (hh2 - ll2) / window<br>D = (np.log(n1 + n2) - np.log(n3)) / np.log(2)<br>alp = np.exp(-4.6 * (D - 1))<br>alp = np.clip(alp, 0.01, 1).values<br>filt = c.values<br>for i, x in enumerate(alp):<br>    cl = c.values[i]<br>    if i < window:<br>        continue<br>    filt[i] = cl * x + (1 - x) * filt[i - 1]<br>return pd.Series(filt, index=ohlc.index, name='{0} period FRAMA.'.format(period))；原目录：FRAMA（period=16, batch=10）；追踪：PF00978；[来源](https://github.com/peerchemist/finta)。
本地数值修正：完整window=2*batch=20条平价收盘窗口使n3=0且n1+n2=0时，明确alpha=1，跟随唯一已观测价格，避免NaN永久污染；其他分形维数与裁剪公式不变。
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
SPEC = {'name': 'finta_frama_16_10d', 'engine': 'finta', 'root_function': 'TA.FRAMA', 'parameters': {'period': 16, 'batch': 10}, 'output_index': 0, 'minimum': 16}

@register_factor
@fixed_factor('finta_frama_16_10d', {})
class Factor_finta_frama_16_10d(PublicFactor):
    name = 'finta_frama_16_10d'
    description = 'FRAMA，period=16、batch=10，实际极差窗口20条。本地数值修正：完整window=2*batch=20条平价收盘窗口使n3=0且n1+n2=0时，明确alpha=1，跟随唯一已观测价格，避免NaN永久污染；其他分形维数与裁剪公式不变。'
    INPUTS = INPUTS
    SPEC = SPEC
