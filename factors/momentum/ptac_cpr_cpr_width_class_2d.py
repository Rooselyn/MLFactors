"""Pandas TA Classic

公式：经典枢轴默认使用上一交易日H/L/C：P=(H[-1]+L[-1]+C[-1])/3，BC=(H[-1]+L[-1])/2，TC=2P−BC；R1=2P−L[-1]，S1=2P−H[-1]，R2/S2=P±(H[-1]−L[-1])，R3=H[-1]+2(P−L[-1])，S3=L[-1]−2(H[-1]−P)；默认width_analysis/price_position等衍生列及其他method的完整分支见源码；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/cpr.py#L76)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'method': 'classic', 'timeframe': 'daily', 'levels': 'standard', 'width_analysis': True, 'price_position': True, 'virgin_cpr': False, 'offset': 0}；只输出'CPR_WIDTH_CLASS'；原目录：cpr（volume=None, method='classic', timeframe='daily', levels='standard', width_analysis=True, price_position=True, virgin_cpr=False）；追踪：PF01274；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_cpr_cpr_width_class_2d', 'root_function': 'f_895433c927_cpr', 'required_inputs': ['open_', 'high', 'low', 'close', 'volume'], 'parameters': {'method': 'classic', 'timeframe': 'daily', 'levels': 'standard', 'width_analysis': True, 'price_position': True, 'virgin_cpr': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 9, 'output_label': 'CPR_WIDTH_CLASS', 'gate_bars': 1, 'kernel': 'kernel_6a0adc2a696f22d5', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_cpr_cpr_width_class_2d', {})
class Factor_ptac_cpr_cpr_width_class_2d(PublicFactor):
    name = 'ptac_cpr_cpr_width_class_2d'
    description = "经典枢轴默认使用上一交易日H/L/C：P=(H[-1]+L[-1]+C[-1])/3，BC=(H[-1]+L[-1])/2，TC=2P−BC；R1=2P−L[-1]，S1=2P−H[-1]，R2/S2=P±(H[-1]−L[-1])，R3=H[-1]+2(P−L[-1])，S3=L[-1]−2(H[-1]−P)；默认width_analysis/price_position等衍生列及其他method的完整分支见源码；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/cpr.py#L76)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'method': 'classic', 'timeframe': 'daily', 'levels': 'standard', 'width_analysis': True, 'price_position': True, 'virgin_cpr': False, 'offset': 0}；只输出'CPR_WIDTH_CLASS'；原目录：cpr（volume=None, method='classic', timeframe='daily', levels='standard', width_analysis=True, price_position=True, virgin_cpr=False）；追踪：PF01274；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
