"""TA-Lib（技术指标及K线形态）

公式：(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；本行取输出outFastK。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STOCHRSI.c)；默认参数={'Time Period': 14.0, 'Fast-K Period': 5.0, 'Fast-D Period': 3.0, 'Fast-D MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：STOCHRSI.outFastK（Time Period=14, Fast-K Period=5, Fast-D Period=3, Fast-D MA=0）；追踪：PF00855；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_stochrsi_outfastk_14_5_3d', 'root_function': 'TA_STOCHRSI', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 14.0, 'Fast-K Period': 5.0, 'Fast-D Period': 3.0, 'Fast-D MA': 0.0}, 'options': [14.0, 5.0, 3.0, 0.0], 'outputs': ['outFastK', 'outFastD'], 'output_index': 0, 'output_label': 'outFastK', 'warmup': 20, 'kernel': 'kernel_070542842119c2ba', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInFastK_Period', 'int'], ['optInFastD_Period', 'int'], ['optInFastD_MAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outFastK', 'double'], ['outFastD', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_stochrsi_outfastk_14_5_3d', {})
class Factor_talib_stochrsi_outfastk_14_5_3d(PublicFactor):
    name = 'talib_stochrsi_outfastk_14_5_3d'
    description = "(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；本行取输出outFastK。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STOCHRSI.c)；默认参数={'Time Period': 14.0, 'Fast-K Period': 5.0, 'Fast-D Period': 3.0, 'Fast-D MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：STOCHRSI.outFastK（Time Period=14, Fast-K Period=5, Fast-D Period=3, Fast-D MA=0）；追踪：PF00855；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
