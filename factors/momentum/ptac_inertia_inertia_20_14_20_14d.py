"""Pandas TA Classic

公式：源码算子/递推链：输出=('', rvi(close, length=rvi_length, scalar=scalar, mamode=mamode))；输出=('r', rvi(close, high=high, low=low, length=rvi_length, scalar=scalar, refined=refined, mamode=mamode))；输出=('t', rvi(close, high=high, low=low, length=rvi_length, scalar=scalar, thirds=thirds, mamode=mamode))；源码算子/递推链：输出=inertia；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/inertia.py#L61)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'rvi_length': 14, 'scalar': 100, 'refined': False, 'thirds': False, 'mamode': 'ema', 'offset': 0}；只输出'INERTIA_20_14'；原目录：inertia（length=20, mamode='ema'）；追踪：PF01190；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ptac_inertia_inertia_20_14_20_14d', 'root_function': 'f_fd56a005ff_inertia', 'required_inputs': ['close', 'high', 'low'], 'parameters': {'length': 20, 'rvi_length': 14, 'scalar': 100, 'refined': False, 'thirds': False, 'mamode': 'ema', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'INERTIA_20_14', 'gate_bars': 1, 'kernel': 'kernel_8bec343bf458fc51', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_inertia_inertia_20_14_20_14d', {})
class Factor_ptac_inertia_inertia_20_14_20_14d(PublicFactor):
    name = 'ptac_inertia_inertia_20_14_20_14d'
    description = "源码算子/递推链：输出=('', rvi(close, length=rvi_length, scalar=scalar, mamode=mamode))；输出=('r', rvi(close, high=high, low=low, length=rvi_length, scalar=scalar, refined=refined, mamode=mamode))；输出=('t', rvi(close, high=high, low=low, length=rvi_length, scalar=scalar, thirds=thirds, mamode=mamode))；源码算子/递推链：输出=inertia；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/inertia.py#L61)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'rvi_length': 14, 'scalar': 100, 'refined': False, 'thirds': False, 'mamode': 'ema', 'offset': 0}；只输出'INERTIA_20_14'；原目录：inertia（length=20, mamode='ema'）；追踪：PF01190；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
