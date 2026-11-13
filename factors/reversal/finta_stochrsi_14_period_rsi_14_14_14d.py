"""FinTA

公式：(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1228)。；固定默认参数={'rsi_period': 14, 'stoch_period': 14}；实际单列输出='14 period RSI'；修正全样本RSI极值造成的未来依赖：极值仅取过去14个RSI；保留原代码最后14期均值平滑。此为明确修正版，不冒充原包逐值结果。；原目录：STOCHRSI（rsi_period=14, stoch_period=14）；追踪：PF01001；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_stochrsi_14_period_rsi_14_14_14d', 'root_function': 'TA.STOCHRSI', 'parameters': {'rsi_period': 14, 'stoch_period': 14}, 'output_index': 0, 'output_label': '14 period RSI', 'kernel': 'kernel_5ef5d3afc4ae8ab1', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_stochrsi_14_period_rsi_14_14_14d', {})
class Factor_finta_stochrsi_14_period_rsi_14_14_14d(PublicFactor):
    name = 'finta_stochrsi_14_period_rsi_14_14_14d'
    description = "(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1228)。；固定默认参数={'rsi_period': 14, 'stoch_period': 14}；实际单列输出='14 period RSI'；修正全样本RSI极值造成的未来依赖：极值仅取过去14个RSI；保留原代码最后14期均值平滑。此为明确修正版，不冒充原包逐值结果。；原目录：STOCHRSI（rsi_period=14, stoch_period=14）；追踪：PF01001；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
