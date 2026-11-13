"""Pandas TA Classic

公式：源码算子/递推链：_length = max(length, _VINTER_LENGTH) + 1；inter = log(typical).diff().to_numpy(dtype=float)；cutoff = coef * vinter * close.to_numpy(dtype=float)；vave = volume.rolling(length).mean().shift(1)；vc = minimum(volume.to_numpy(dtype=float), vave.to_numpy(dtype=float) * vcoef)；mf = typical.diff().to_numpy(dtype=float)；vcp = where(mf > cutoff, vc, where(mf < -cutoff, -vc, 0.0))；vfi = degenerate_div(vcp.rolling(length).sum(), vave)；输出=vfi；输出=None；vinter[_VINTER_LENGTH - 1:] = lib.stride_tricks.sliding_window_view(inter, _VINTER_LENGTH).std(axis=1)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/vfi.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 130, 'coef': 0.2, 'vcoef': 2.5, 'mamode': 'ema', 'offset': 0}；只输出'VFI_130'；原目录：vfi（length=130, mamode='ema'）；追踪：PF01323；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_vfi_vfi_130_130d', 'root_function': 'f_739b2dea6d_vfi', 'required_inputs': ['high', 'low', 'close', 'volume'], 'parameters': {'length': 130, 'coef': 0.2, 'vcoef': 2.5, 'mamode': 'ema', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'VFI_130', 'gate_bars': 1, 'kernel': 'kernel_4a5fa844310784d8', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_vfi_vfi_130_130d', {})
class Factor_ptac_vfi_vfi_130_130d(PublicFactor):
    name = 'ptac_vfi_vfi_130_130d'
    description = "源码算子/递推链：_length = max(length, _VINTER_LENGTH) + 1；inter = log(typical).diff().to_numpy(dtype=float)；cutoff = coef * vinter * close.to_numpy(dtype=float)；vave = volume.rolling(length).mean().shift(1)；vc = minimum(volume.to_numpy(dtype=float), vave.to_numpy(dtype=float) * vcoef)；mf = typical.diff().to_numpy(dtype=float)；vcp = where(mf > cutoff, vc, where(mf < -cutoff, -vc, 0.0))；vfi = degenerate_div(vcp.rolling(length).sum(), vave)；输出=vfi；输出=None；vinter[_VINTER_LENGTH - 1:] = lib.stride_tricks.sliding_window_view(inter, _VINTER_LENGTH).std(axis=1)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/vfi.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 130, 'coef': 0.2, 'vcoef': 2.5, 'mamode': 'ema', 'offset': 0}；只输出'VFI_130'；原目录：vfi（length=130, mamode='ema'）；追踪：PF01323；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
