"""Pandas TA Classic

公式：源码算子/递推链：_props += f'_{bb_length}_{bb_std}_{kc_length}_{kc_scalar_wide}_{kc_scalar_normal}_{kc_scalar_narrow}'；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/squeeze_pro.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'bb_length': 20, 'bb_std': 2.0, 'kc_length': 20, 'kc_scalar_wide': 2, 'kc_scalar_normal': 1.5, 'kc_scalar_narrow': 1, 'mom_length': 12, 'mom_smooth': 6, 'use_tr': True, 'mamode': 'sma', 'offset': 0}；只输出'SQZPRO_OFF'；原目录：squeeze_pro（mamode='sma'）；追踪：PF01210；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_squeeze_pro_sqzpro_off_20_20_12d', 'root_function': 'f_bc73cb0e13_squeeze_pro', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'bb_length': 20, 'bb_std': 2.0, 'kc_length': 20, 'kc_scalar_wide': 2, 'kc_scalar_normal': 1.5, 'kc_scalar_narrow': 1, 'mom_length': 12, 'mom_smooth': 6, 'use_tr': True, 'mamode': 'sma', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 4, 'output_label': 'SQZPRO_OFF', 'gate_bars': 1, 'kernel': 'kernel_50f52931b7cafe07', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_squeeze_pro_sqzpro_off_20_20_12d', {})
class Factor_ptac_squeeze_pro_sqzpro_off_20_20_12d(PublicFactor):
    name = 'ptac_squeeze_pro_sqzpro_off_20_20_12d'
    description = "源码算子/递推链：_props += f'_{bb_length}_{bb_std}_{kc_length}_{kc_scalar_wide}_{kc_scalar_normal}_{kc_scalar_narrow}'；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/squeeze_pro.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'bb_length': 20, 'bb_std': 2.0, 'kc_length': 20, 'kc_scalar_wide': 2, 'kc_scalar_normal': 1.5, 'kc_scalar_narrow': 1, 'mom_length': 12, 'mom_smooth': 6, 'use_tr': True, 'mamode': 'sma', 'offset': 0}；只输出'SQZPRO_OFF'；原目录：squeeze_pro（mamode='sma'）；追踪：PF01210；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
