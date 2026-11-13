"""Pandas TA Classic

公式：源码算子/递推链：输出=jma；del1 = price - uBand；del2 = price - lBand；v_sum[i] = v_sum[i - 1] + (volty[i] - volty[max(i - sum_length, 0)]) / sum_length；avg_volty = mean(v_sum[max(i - 65, 0):i + 1])；d_volty = 0.0 if avg_volty == 0 else volty[i] / avg_volty；r_volty = max(1.0, min(power(length1, 1.0 / pow1), d_volty))；uBand = price if del1 > 0 else price - kv * del1；lBand = price if del2 < 0 else price - kv * del2；ma1 = (1 - alpha) * price + alpha * ma1；det0 = (price - ma1) * (1 - beta) + beta * det0；ma2 = ma1 + pr * det0；det1 = (ma2 - jma[i - 1]) * (1 - alpha) * (1 - alpha) + alpha * alpha * det1；jma[i] = jma[i - 1] + det1；源码算子/递推链：输出=1.5 + phase * 0.01；输出=0.5；输出=2.5；源码算子/递推链：length = 0.5 * (_length - 1)；length1 = max(log(sqrt(length)) / log(2.0) + 2.0, 0)；pow1 = max(length1 - 2.0, 0.5)；length2 = length1 * sqrt(length)；bet = length2 / (length2 + 1)；beta = 0.45 * (_length - 1) / (0.45 * (_length - 1) + 2.0)；jma[0:_length - 1] = nan；输出=jma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/jma.py#L98)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 3.0, 'phase': 0, 'offset': 0}；只输出'JMA_7_0'；原目录：jma（length=None, phase=None）；追踪：PF01230；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_jma_jma_7_0_3d', 'root_function': 'f_2aea572da6_jma', 'required_inputs': ['close'], 'parameters': {'length': 3.0, 'phase': 0, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'JMA_7_0', 'gate_bars': 1, 'kernel': 'kernel_4725f27f123ecbb0', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_jma_jma_7_0_3d', {})
class Factor_ptac_jma_jma_7_0_3d(PublicFactor):
    name = 'ptac_jma_jma_7_0_3d'
    description = "源码算子/递推链：输出=jma；del1 = price - uBand；del2 = price - lBand；v_sum[i] = v_sum[i - 1] + (volty[i] - volty[max(i - sum_length, 0)]) / sum_length；avg_volty = mean(v_sum[max(i - 65, 0):i + 1])；d_volty = 0.0 if avg_volty == 0 else volty[i] / avg_volty；r_volty = max(1.0, min(power(length1, 1.0 / pow1), d_volty))；uBand = price if del1 > 0 else price - kv * del1；lBand = price if del2 < 0 else price - kv * del2；ma1 = (1 - alpha) * price + alpha * ma1；det0 = (price - ma1) * (1 - beta) + beta * det0；ma2 = ma1 + pr * det0；det1 = (ma2 - jma[i - 1]) * (1 - alpha) * (1 - alpha) + alpha * alpha * det1；jma[i] = jma[i - 1] + det1；源码算子/递推链：输出=1.5 + phase * 0.01；输出=0.5；输出=2.5；源码算子/递推链：length = 0.5 * (_length - 1)；length1 = max(log(sqrt(length)) / log(2.0) + 2.0, 0)；pow1 = max(length1 - 2.0, 0.5)；length2 = length1 * sqrt(length)；bet = length2 / (length2 + 1)；beta = 0.45 * (_length - 1) / (0.45 * (_length - 1) + 2.0)；jma[0:_length - 1] = nan；输出=jma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/jma.py#L98)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 3.0, 'phase': 0, 'offset': 0}；只输出'JMA_7_0'；原目录：jma（length=None, phase=None）；追踪：PF01230；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
