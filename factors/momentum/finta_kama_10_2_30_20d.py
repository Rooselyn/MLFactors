"""FinTA

公式：固定公开源码默认参数：{'er': 10, 'ema_fast': 2, 'ema_slow': 30, 'period': 20, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：KAMA(cls, ohlc: DataFrame, er: int=10, ema_fast: int=2, ema_slow: int=30, period: int=20, column: str='close'): er = cls.ER(ohlc, er)<br>fast_alpha = 2 / (ema_fast + 1)<br>slow_alpha = 2 / (ema_slow + 1)<br>sc = pd.Series((er * (fast_alpha - slow_alpha) + slow_alpha) ** 2, name='smoothing_constant')<br>sma = pd.Series(ohlc[column].rolling(period).mean(), name='SMA')<br>kama = []<br>for s, ma, price in zip(sc.iteritems(), sma.shift().iteritems(), ohlc[column].iteritems()):<br>    try:<br>        kama.append(kama[-1] + s[1] * (price[1] - kama[-1]))<br>    except (IndexError, TypeError):<br>        if pd.notnull(ma[1]):<br>            kama.append(ma[1] + s[1] * (price[1] - ma[1]))<br>        else:<br>            kama.append(None)<br>sma['KAMA'] = pd.Series(kama, index=sma.index, name='{0} period KAMA.'.format(period))<br>return sma['KAMA']；ER(cls, ohlc: DataFrame, period: int=10, column: str='close'): change = ohlc[column].diff(period).abs()<br>volatility = ohlc[column].diff().abs().rolling(window=period).sum()<br>return pd.Series(change / volatility, name='{0} period ER'.format(period))；原目录：KAMA（er=10, ema_fast=2, ema_slow=30, period=20）；追踪：PF00972；[来源](https://github.com/peerchemist/finta)。
本地数值修正：完整平价效率窗口E=0，非法递推状态从有效历史种子重新初始化，禁止最终结果前向填充。
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
SPEC = {'name': 'finta_kama_10_2_30_20d', 'engine': 'finta', 'root_function': 'TA.KAMA', 'parameters': {'er': 10, 'ema_fast': 2, 'ema_slow': 30, 'period': 20, 'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_kama_10_2_30_20d', {})
class Factor_finta_kama_10_2_30_20d(PublicFactor):
    name = 'finta_kama_10_2_30_20d'
    description = 'KAMA，er=10、ema_fast=2、ema_slow=30、period=20。完整平价10间隔效率比率按0处理；以前20条均值作为首次递推种子；无效状态从有效种子恢复，不对输出前向回填。'
    INPUTS = INPUTS
    SPEC = SPEC
