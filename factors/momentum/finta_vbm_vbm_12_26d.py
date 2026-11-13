"""FinTA

公式：源码实际为(Δ_n C−lag_n C)/ATR(v)=(C−2lag_n C)/ATR(v)，与其注释(C−lag_n C)/ATR(v)不一致，需固定修正版本；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L664)。；固定默认参数={'roc_period': 12, 'atr_period': 26, 'column': 'close'}；实际单列输出='VBM'；修正公开代码额外减去滞后收盘价的错误；采用其公开说明公式(C−C.shift(12))/ATR26。；原目录：VBM（roc_period=12, atr_period=26）；追踪：PF00983；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_vbm_vbm_12_26d', 'root_function': 'TA.VBM', 'parameters': {'roc_period': 12, 'atr_period': 26, 'column': 'close'}, 'output_index': 0, 'output_label': 'VBM', 'kernel': 'kernel_4ef42a01d8f63c34', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_vbm_vbm_12_26d', {})
class Factor_finta_vbm_vbm_12_26d(PublicFactor):
    name = 'finta_vbm_vbm_12_26d'
    description = "源码实际为(Δ_n C−lag_n C)/ATR(v)=(C−2lag_n C)/ATR(v)，与其注释(C−lag_n C)/ATR(v)不一致，需固定修正版本；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L664)。；固定默认参数={'roc_period': 12, 'atr_period': 26, 'column': 'close'}；实际单列输出='VBM'；修正公开代码额外减去滞后收盘价的错误；采用其公开说明公式(C−C.shift(12))/ATR26。；原目录：VBM（roc_period=12, atr_period=26）；追踪：PF00983；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
