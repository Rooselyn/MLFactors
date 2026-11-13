"""Pandas TA Classic

公式：源码算子/递推链：输出=amatdf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/amat.py#L15)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 8, 'slow': 21, 'lookback': 2, 'mamode': 'ema', 'offset': 0}；只输出'AMATe_LR_8_21_2'；原目录：amat（fast=8, slow=21, mamode='ema'）；追踪：PF01270；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_amat_amate_lr_8_21_2_8_21d', 'root_function': 'f_1d70cd2588_amat', 'required_inputs': ['close'], 'parameters': {'fast': 8, 'slow': 21, 'lookback': 2, 'mamode': 'ema', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'AMATe_LR_8_21_2', 'gate_bars': 21, 'kernel': 'kernel_3175b23ebeec2636', 'engine': 'ptac', 'minimum': 21}

@register_factor
@fixed_factor('ptac_amat_amate_lr_8_21_2_8_21d', {})
class Factor_ptac_amat_amate_lr_8_21_2_8_21d(PublicFactor):
    name = 'ptac_amat_amate_lr_8_21_2_8_21d'
    description = "源码算子/递推链：输出=amatdf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/amat.py#L15)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 8, 'slow': 21, 'lookback': 2, 'mamode': 'ema', 'offset': 0}；只输出'AMATe_LR_8_21_2'；原目录：amat（fast=8, slow=21, mamode='ema'）；追踪：PF01270；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
