"""FinTA

公式：源码算子/递推链：sp = ohlc['high'] - ohlc['close']；bp = ohlc['close'] - ohlc['low']；spavg = sp.ewm(span=period, adjust=adjust).mean()；bpavg = bp.ewm(span=period, adjust=adjust).mean()；nbp = bp / bpavg；nsp = sp / spavg；varg = ohlc['volume'].ewm(span=period, adjust=adjust).mean()；nv = ohlc['volume'] / varg；nbf = Series((nbp * nv).ewm(span=20, adjust=adjust).mean(), name='Buy.')；nsf = Series((nsp * nv).ewm(span=20, adjust=adjust).mean(), name='Sell.')；输出=concat([nbf, nsf], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1694)。；固定默认参数={'period': 40, 'adjust': True}；实际单列输出='Buy.'；；原目录：BASPN（period=40）；追踪：PF01019；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_baspn_buy_40d', 'root_function': 'TA.BASPN', 'parameters': {'period': 40, 'adjust': True}, 'output_index': 0, 'output_label': 'Buy.', 'kernel': 'kernel_07857876443d309c', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_baspn_buy_40d', {})
class Factor_finta_baspn_buy_40d(PublicFactor):
    name = 'finta_baspn_buy_40d'
    description = "源码算子/递推链：sp = ohlc['high'] - ohlc['close']；bp = ohlc['close'] - ohlc['low']；spavg = sp.ewm(span=period, adjust=adjust).mean()；bpavg = bp.ewm(span=period, adjust=adjust).mean()；nbp = bp / bpavg；nsp = sp / spavg；varg = ohlc['volume'].ewm(span=period, adjust=adjust).mean()；nv = ohlc['volume'] / varg；nbf = Series((nbp * nv).ewm(span=20, adjust=adjust).mean(), name='Buy.')；nsf = Series((nsp * nv).ewm(span=20, adjust=adjust).mean(), name='Sell.')；输出=concat([nbf, nsf], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1694)。；固定默认参数={'period': 40, 'adjust': True}；实际单列输出='Buy.'；；原目录：BASPN（period=40）；追踪：PF01019；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
