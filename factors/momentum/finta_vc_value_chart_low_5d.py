"""FinTA

公式：源码算子/递推链：float_axis = ((ohlc.high + ohlc.low) / 2).rolling(window=period).mean()；vol_unit = (ohlc.high - ohlc.low).rolling(window=period).mean() * 0.2；value_chart_high = Series((ohlc.high - float_axis) / vol_unit, name='Value Chart High')；value_chart_low = Series((ohlc.low - float_axis) / vol_unit, name='Value Chart Low')；value_chart_close = Series((ohlc.close - float_axis) / vol_unit, name='Value Chart Close')；value_chart_open = Series((ohlc.open - float_axis) / vol_unit, name='Value Chart Open')；输出=concat([value_chart_high, value_chart_low, value_chart_close, value_chart_open], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L2244)。；固定默认参数={'period': 5}；实际单列输出='Value Chart Low'；；原目录：VC（period=5）；追踪：PF01035；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_vc_value_chart_low_5d', 'root_function': 'TA.VC', 'parameters': {'period': 5}, 'output_index': 1, 'output_label': 'Value Chart Low', 'kernel': 'kernel_3f993d52484e2b63', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_vc_value_chart_low_5d', {})
class Factor_finta_vc_value_chart_low_5d(PublicFactor):
    name = 'finta_vc_value_chart_low_5d'
    description = "源码算子/递推链：float_axis = ((ohlc.high + ohlc.low) / 2).rolling(window=period).mean()；vol_unit = (ohlc.high - ohlc.low).rolling(window=period).mean() * 0.2；value_chart_high = Series((ohlc.high - float_axis) / vol_unit, name='Value Chart High')；value_chart_low = Series((ohlc.low - float_axis) / vol_unit, name='Value Chart Low')；value_chart_close = Series((ohlc.close - float_axis) / vol_unit, name='Value Chart Close')；value_chart_open = Series((ohlc.open - float_axis) / vol_unit, name='Value Chart Open')；输出=concat([value_chart_high, value_chart_low, value_chart_close, value_chart_open], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L2244)。；固定默认参数={'period': 5}；实际单列输出='Value Chart Low'；；原目录：VC（period=5）；追踪：PF01035；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
