"""FinTA

公式：Tenkan=(max(H,n1)+min(L,n1))/2；Kijun同式n2；SpanA=(Tenkan+Kijun)/2，SpanB同式n3；绘图前移和Chikou后移不能产生提前可知信号；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1852)。；固定默认参数={'tenkan_period': 9, 'kijun_period': 26, 'senkou_period': 52, 'chikou_period': 26}；实际单列输出='KIJUN'；；原目录：ICHIMOKU（tenkan_period=9, kijun_period=26, senkou_period=52, chikou_period=26）；追踪：PF01025；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_ichimoku_kijun_9_26_52_26d', 'root_function': 'TA.ICHIMOKU', 'parameters': {'tenkan_period': 9, 'kijun_period': 26, 'senkou_period': 52, 'chikou_period': 26}, 'output_index': 1, 'output_label': 'KIJUN', 'kernel': 'kernel_34ad41fd7cad2286', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_ichimoku_kijun_9_26_52_26d', {})
class Factor_finta_ichimoku_kijun_9_26_52_26d(PublicFactor):
    name = 'finta_ichimoku_kijun_9_26_52_26d'
    description = "Tenkan=(max(H,n1)+min(L,n1))/2；Kijun同式n2；SpanA=(Tenkan+Kijun)/2，SpanB同式n3；绘图前移和Chikou后移不能产生提前可知信号；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1852)。；固定默认参数={'tenkan_period': 9, 'kijun_period': 26, 'senkou_period': 52, 'chikou_period': 26}；实际单列输出='KIJUN'；；原目录：ICHIMOKU（tenkan_period=9, kijun_period=26, senkou_period=52, chikou_period=26）；追踪：PF01025；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
