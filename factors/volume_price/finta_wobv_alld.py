"""FinTA

公式：固定公开源码默认参数：{'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：WOBV(cls, ohlcv: DataFrame, column: str='close'): wobv = pd.Series(ohlcv['volume'] * ohlcv[column].diff(), name='WOBV')<br>return wobv.cumsum()；原目录：WOBV（无固定窗口）；追踪：PF01010；[来源](https://github.com/peerchemist/finta)。
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
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'finta_wobv_alld', 'engine': 'finta', 'root_function': 'TA.WOBV', 'parameters': {'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_wobv_alld', {})
class Factor_finta_wobv_alld(PublicFactor):
    name = 'finta_wobv_alld'
    description = "固定公开源码默认参数：{'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：WOBV(cls, ohlcv: DataFrame, column: str='close'): wobv = pd.Series(ohlcv['volume'] * ohlcv[column].diff(), name='WOBV')<br>return wobv.cumsum()；原目录：WOBV（无固定窗口）；追踪：PF01010；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
