"""FinTA

公式：Middle=EMA(TP,n)或EMA(C,n)；Upper/Lower=Middle±k×ATR(atr_n)，具体价格口径按来源；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1013)。；固定默认参数={'period': 20, 'atr_period': 10, 'MA': None, 'kc_mult': 2}；实际单列输出='KC_UPPER'；；原目录：KC（period=20, atr_period=10, MA=None, kc_mult=2）；追踪：PF00994；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_kc_kc_upper_20_10d', 'root_function': 'TA.KC', 'parameters': {'period': 20, 'atr_period': 10, 'MA': None, 'kc_mult': 2}, 'output_index': 0, 'output_label': 'KC_UPPER', 'kernel': 'kernel_8f18ed83a001c30c', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_kc_kc_upper_20_10d', {})
class Factor_finta_kc_kc_upper_20_10d(PublicFactor):
    name = 'finta_kc_kc_upper_20_10d'
    description = "Middle=EMA(TP,n)或EMA(C,n)；Upper/Lower=Middle±k×ATR(atr_n)，具体价格口径按来源；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1013)。；固定默认参数={'period': 20, 'atr_period': 10, 'MA': None, 'kc_mult': 2}；实际单列输出='KC_UPPER'；；原目录：KC（period=20, atr_period=10, MA=None, kc_mult=2）；追踪：PF00994；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
