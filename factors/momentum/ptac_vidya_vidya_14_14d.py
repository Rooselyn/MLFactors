"""Pandas TA Classic

公式：源码算子/递推链：alpha = 2 / (length + 1)；vidya_arr[length - 1] = close.iloc[:length].mean()；输出=vidya；输出=None；mom = source.diff(d)；pos_sum = positive.rolling(n).sum()；neg_sum = negative.rolling(n).sum()；denominator = pos_sum + neg_sum；输出=((pos_sum - neg_sum) / denominator).mask(denominator == 0, 0.0)；vidya_arr[i] = alpha * cmo_arr[i] * c_arr[i] + vidya_arr[i - 1] * (1 - alpha * cmo_arr[i])；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/vidya.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'drift': 1, 'offset': 0}；只输出'VIDYA_14'；原目录：vidya（length=14）；追踪：PF01250；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_vidya_vidya_14_14d', 'root_function': 'f_24520a72e2_vidya', 'required_inputs': ['close'], 'parameters': {'length': 14, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'VIDYA_14', 'gate_bars': 1, 'kernel': 'kernel_cd3f5a348320806d', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_vidya_vidya_14_14d', {})
class Factor_ptac_vidya_vidya_14_14d(PublicFactor):
    name = 'ptac_vidya_vidya_14_14d'
    description = "源码算子/递推链：alpha = 2 / (length + 1)；vidya_arr[length - 1] = close.iloc[:length].mean()；输出=vidya；输出=None；mom = source.diff(d)；pos_sum = positive.rolling(n).sum()；neg_sum = negative.rolling(n).sum()；denominator = pos_sum + neg_sum；输出=((pos_sum - neg_sum) / denominator).mask(denominator == 0, 0.0)；vidya_arr[i] = alpha * cmo_arr[i] * c_arr[i] + vidya_arr[i - 1] * (1 - alpha * cmo_arr[i])；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/vidya.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'drift': 1, 'offset': 0}；只输出'VIDYA_14'；原目录：vidya（length=14）；追踪：PF01250；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
