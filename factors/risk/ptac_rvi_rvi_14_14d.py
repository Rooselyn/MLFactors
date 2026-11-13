"""Pandas TA Classic

公式：源码算子/递推链：输出=(result, '') if result is not None else None；输出=(0.5 * (high_rvi + low_rvi), 'r')；输出=((high_rvi + low_rvi + close_rvi) / 3.0, 't')；输出=None；源码算子/递推链：输出=rvi；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/rvi.py#L61)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'scalar': 100, 'refined': False, 'thirds': False, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'RVI_14'；原目录：rvi（length=14, mamode='ema'）；追踪：PF01307；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_rvi_rvi_14_14d', 'root_function': 'f_0d314e3263_rvi', 'required_inputs': ['close', 'high', 'low'], 'parameters': {'length': 14, 'scalar': 100, 'refined': False, 'thirds': False, 'mamode': 'ema', 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'RVI_14', 'gate_bars': 1, 'kernel': 'kernel_5ff91f09bfd4a150', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_rvi_rvi_14_14d', {})
class Factor_ptac_rvi_rvi_14_14d(PublicFactor):
    name = 'ptac_rvi_rvi_14_14d'
    description = "源码算子/递推链：输出=(result, '') if result is not None else None；输出=(0.5 * (high_rvi + low_rvi), 'r')；输出=((high_rvi + low_rvi + close_rvi) / 3.0, 't')；输出=None；源码算子/递推链：输出=rvi；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/rvi.py#L61)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'scalar': 100, 'refined': False, 'thirds': False, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'RVI_14'；原目录：rvi（length=14, mamode='ema'）；追踪：PF01307；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
