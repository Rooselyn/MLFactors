"""Pandas TA Classic

公式：源码算子/递推链：thermoL = (low.shift(drift) - low).abs()；thermoH = (high - high.shift(drift)).abs()；thermo_long = thermo < thermo_ma * long；thermo_short = thermo > thermo_ma * short；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/thermo.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'long': 2, 'short': 0.5, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'THERMOma_20_2_0.5'；原目录：thermo（length=20, mamode='ema'）；追踪：PF01308；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ptac_thermo_thermoma_20_2_0_5_20d', 'root_function': 'f_e24250051c_thermo', 'required_inputs': ['high', 'low'], 'parameters': {'length': 20, 'long': 2, 'short': 0.5, 'mamode': 'ema', 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'THERMOma_20_2_0.5', 'gate_bars': 20, 'kernel': 'kernel_6ddb7dfb57151a1a', 'engine': 'ptac', 'minimum': 20}

@register_factor
@fixed_factor('ptac_thermo_thermoma_20_2_0_5_20d', {})
class Factor_ptac_thermo_thermoma_20_2_0_5_20d(PublicFactor):
    name = 'ptac_thermo_thermoma_20_2_0_5_20d'
    description = "源码算子/递推链：thermoL = (low.shift(drift) - low).abs()；thermoH = (high - high.shift(drift)).abs()；thermo_long = thermo < thermo_ma * long；thermo_short = thermo > thermo_ma * short；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/thermo.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'long': 2, 'short': 0.5, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'THERMOma_20_2_0.5'；原目录：thermo（length=20, mamode='ema'）；追踪：PF01308；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
