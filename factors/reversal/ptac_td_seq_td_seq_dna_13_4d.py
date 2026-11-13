"""Pandas TA Classic

公式：源码算子/递推链：输出=out；count = count + 1 if td_bool[i] else 0；源码算子/递推链：输出=df；输出=None；td_bool = series.diff(4) > 0 if direction == 'up' else series.diff(4) < 0；输出=td_num；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/td_seq.py#L31)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'asint': False, 'offset': 0}；只输出'TD_SEQ_DNa'；原目录：td_seq（asint=None）；追踪：PF01215；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_td_seq_td_seq_dna_13_4d', 'root_function': 'f_651beb96d7_td_seq', 'required_inputs': ['close'], 'parameters': {'asint': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'TD_SEQ_DNa', 'gate_bars': 1, 'kernel': 'kernel_0731468b7784b6b0', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_td_seq_td_seq_dna_13_4d', {})
class Factor_ptac_td_seq_td_seq_dna_13_4d(PublicFactor):
    name = 'ptac_td_seq_td_seq_dna_13_4d'
    description = "源码算子/递推链：输出=out；count = count + 1 if td_bool[i] else 0；源码算子/递推链：输出=df；输出=None；td_bool = series.diff(4) > 0 if direction == 'up' else series.diff(4) < 0；输出=td_num；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/td_seq.py#L31)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'asint': False, 'offset': 0}；只输出'TD_SEQ_DNa'；原目录：td_seq（asint=None）；追踪：PF01215；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
