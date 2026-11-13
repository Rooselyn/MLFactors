"""FinTA

公式：Long=max(H,long_period)−kATR(22)，Short=min(L,short_period)+kATR(22)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1746)。；固定默认参数={'short_period': 22, 'long_period': 22, 'k': 3}；实际单列输出='Short.'；；原目录：CHANDELIER（short_period=22, long_period=22, k=3）；追踪：PF01021；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_chandelier_short_22_22d', 'root_function': 'TA.CHANDELIER', 'parameters': {'short_period': 22, 'long_period': 22, 'k': 3}, 'output_index': 0, 'output_label': 'Short.', 'kernel': 'kernel_5619d85d352d50fa', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_chandelier_short_22_22d', {})
class Factor_finta_chandelier_short_22_22d(PublicFactor):
    name = 'finta_chandelier_short_22_22d'
    description = "Long=max(H,long_period)−kATR(22)，Short=min(L,short_period)+kATR(22)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1746)。；固定默认参数={'short_period': 22, 'long_period': 22, 'k': 3}；实际单列输出='Short.'；；原目录：CHANDELIER（short_period=22, long_period=22, k=3）；追踪：PF01021；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
