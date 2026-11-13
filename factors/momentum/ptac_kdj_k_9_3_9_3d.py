"""Pandas TA Classic

公式：RSV=100(C−min(L,n))/(max(H,n)−min(L,n))；K=SMA递推(RSV,3,1)，D=SMA递推(K,3,1)，J=3K−2D；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/kdj.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 9, 'signal': 3, 'offset': 0}；只输出'K_9_3'；原目录：kdj（length=9, signal=3）；追踪：PF01191；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_kdj_k_9_3_9_3d', 'root_function': 'f_097c8d216d_kdj', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'length': 9, 'signal': 3, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'K_9_3', 'gate_bars': 1, 'kernel': 'kernel_561b8d700d8cfd4a', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_kdj_k_9_3_9_3d', {})
class Factor_ptac_kdj_k_9_3_9_3d(PublicFactor):
    name = 'ptac_kdj_k_9_3_9_3d'
    description = "RSV=100(C−min(L,n))/(max(H,n)−min(L,n))；K=SMA递推(RSV,3,1)，D=SMA递推(K,3,1)，J=3K−2D；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/kdj.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 9, 'signal': 3, 'offset': 0}；只输出'K_9_3'；原目录：kdj（length=9, signal=3）；追踪：PF01191；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
