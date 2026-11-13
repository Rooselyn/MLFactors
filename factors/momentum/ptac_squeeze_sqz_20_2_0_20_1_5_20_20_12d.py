"""Pandas TA Classic

公式：源码算子/递推链：输出=[c.split('_')[0][n - 1:n] for c in df.columns]；源码算子/递推链：输出=sma(momo, length=mom_smooth)；highest_high = high.rolling(kc_length).max()；lowest_low = low.rolling(kc_length).min()；avg_ = 0.25 * (highest_high + lowest_low) + 0.5 * kch_b；输出=linreg(close - avg_, length=kc_length)；输出=ema(momo, length=mom_smooth)；源码算子/递推链：pos_inc *= squeeze_s；pos_dec *= squeeze_s；neg_dec *= squeeze_s；neg_inc *= squeeze_s；sqz_inc = squeeze_s * increasing(squeeze_s)；sqz_dec = squeeze_s * decreasing(squeeze_s)；源码算子/递推链：_props += f'_{bb_length}_{bb_std}_{kc_length}_{kc_scalar}'；_props += '_LB' if lazybear else ''；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/squeeze.py#L94)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'bb_length': 20, 'bb_std': 2.0, 'kc_length': 20, 'kc_scalar': 1.5, 'mom_length': 12, 'mom_smooth': 6, 'use_tr': True, 'mamode': 'sma', 'offset': 0}；只输出'SQZ_20_2.0_20_1.5'；原目录：squeeze（mamode='sma'）；追踪：PF01209；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_squeeze_sqz_20_2_0_20_1_5_20_20_12d', 'root_function': 'f_b7c0fc37eb_squeeze', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'bb_length': 20, 'bb_std': 2.0, 'kc_length': 20, 'kc_scalar': 1.5, 'mom_length': 12, 'mom_smooth': 6, 'use_tr': True, 'mamode': 'sma', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'SQZ_20_2.0_20_1.5', 'gate_bars': 1, 'kernel': 'kernel_f7e3bdda8f731cec', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_squeeze_sqz_20_2_0_20_1_5_20_20_12d', {})
class Factor_ptac_squeeze_sqz_20_2_0_20_1_5_20_20_12d(PublicFactor):
    name = 'ptac_squeeze_sqz_20_2_0_20_1_5_20_20_12d'
    description = "源码算子/递推链：输出=[c.split('_')[0][n - 1:n] for c in df.columns]；源码算子/递推链：输出=sma(momo, length=mom_smooth)；highest_high = high.rolling(kc_length).max()；lowest_low = low.rolling(kc_length).min()；avg_ = 0.25 * (highest_high + lowest_low) + 0.5 * kch_b；输出=linreg(close - avg_, length=kc_length)；输出=ema(momo, length=mom_smooth)；源码算子/递推链：pos_inc *= squeeze_s；pos_dec *= squeeze_s；neg_dec *= squeeze_s；neg_inc *= squeeze_s；sqz_inc = squeeze_s * increasing(squeeze_s)；sqz_dec = squeeze_s * decreasing(squeeze_s)；源码算子/递推链：_props += f'_{bb_length}_{bb_std}_{kc_length}_{kc_scalar}'；_props += '_LB' if lazybear else ''；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/squeeze.py#L94)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'bb_length': 20, 'bb_std': 2.0, 'kc_length': 20, 'kc_scalar': 1.5, 'mom_length': 12, 'mom_smooth': 6, 'use_tr': True, 'mamode': 'sma', 'offset': 0}；只输出'SQZ_20_2.0_20_1.5'；原目录：squeeze（mamode='sma'）；追踪：PF01209；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
