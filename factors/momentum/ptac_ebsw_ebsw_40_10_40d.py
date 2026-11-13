"""Pandas TA Classic

公式：源码算子/递推链：alpha1 = (1 - sin(360 / length)) / cos(360 / length)；a1 = exp(-sqrt(2) * pi / bars)；b1 = 2 * a1 * cos(sqrt(2) * 180 / bars)；c3 = -1 * a1 * a1；c1 = 1 - c2 - c3；输出=result；result[length - 1] = 0.0；HP = 0.5 * (1 + alpha1) * (close[i] - lastClose) + alpha1 * lastHP；Filt = c1 * (HP + lastHP) / 2 + c2 * fh1 + c3 * fh0；Wave = (Filt + fh1 + fh0) / 3；Pwr = (Filt * Filt + fh1 * fh1 + fh0 * fh0) / 3；Wave = Wave / sqrt(Pwr) if Pwr > 0 else 0.0；源码算子/递推链：输出=ebsw；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/ebsw.py#L55)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 40, 'bars': 10, 'offset': 0}；只输出'EBSW_40_10'；原目录：ebsw（length=40, bars=10）；追踪：PF01171；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_ebsw_ebsw_40_10_40d', 'root_function': 'f_01b8b4011a_ebsw', 'required_inputs': ['close'], 'parameters': {'length': 40, 'bars': 10, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'EBSW_40_10', 'gate_bars': 1, 'kernel': 'kernel_e259f57cd70b2f14', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_ebsw_ebsw_40_10_40d', {})
class Factor_ptac_ebsw_ebsw_40_10_40d(PublicFactor):
    name = 'ptac_ebsw_ebsw_40_10_40d'
    description = "源码算子/递推链：alpha1 = (1 - sin(360 / length)) / cos(360 / length)；a1 = exp(-sqrt(2) * pi / bars)；b1 = 2 * a1 * cos(sqrt(2) * 180 / bars)；c3 = -1 * a1 * a1；c1 = 1 - c2 - c3；输出=result；result[length - 1] = 0.0；HP = 0.5 * (1 + alpha1) * (close[i] - lastClose) + alpha1 * lastHP；Filt = c1 * (HP + lastHP) / 2 + c2 * fh1 + c3 * fh0；Wave = (Filt + fh1 + fh0) / 3；Pwr = (Filt * Filt + fh1 * fh1 + fh0 * fh0) / 3；Wave = Wave / sqrt(Pwr) if Pwr > 0 else 0.0；源码算子/递推链：输出=ebsw；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/ebsw.py#L55)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 40, 'bars': 10, 'offset': 0}；只输出'EBSW_40_10'；原目录：ebsw（length=40, bars=10）；追踪：PF01171；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
