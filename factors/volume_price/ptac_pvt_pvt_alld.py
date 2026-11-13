"""Pandas TA Classic

公式：累计[V×(C/C[-1]−1)]；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/pvt.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'drift': 1, 'offset': 0}；只输出'PVT'；原目录：pvt（drift=None）；追踪：PF01322；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_pvt_pvt_alld', 'root_function': 'f_e940aef813_pvt', 'required_inputs': ['close', 'volume'], 'parameters': {'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PVT', 'gate_bars': 1, 'kernel': 'kernel_113e8495ce49777f', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_pvt_pvt_alld', {})
class Factor_ptac_pvt_pvt_alld(PublicFactor):
    name = 'ptac_pvt_pvt_alld'
    description = "累计[V×(C/C[-1]−1)]；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/pvt.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'drift': 1, 'offset': 0}；只输出'PVT'；原目录：pvt（drift=None）；追踪：PF01322；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
