"""TA-Lib（技术指标及K线形态）

公式：Middle=EMA(TP,n)或EMA(C,n)；Upper/Lower=Middle±k×ATR(atr_n)，具体价格口径按来源；本行取输出outRealUpperBand。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_KC.c)；默认参数={'Time Period': 20.0, 'ATR Period': 10.0, 'Deviations': 2.0}；完整数值核及辅助调用在实现附录展开。；原目录：KC.outRealUpperBand（Time Period=20, ATR Period=10, Deviations=2.000000e+0）；追踪：PF00781；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_kc_outrealupperband_20_10d', 'root_function': 'TA_KC', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 20.0, 'ATR Period': 10.0, 'Deviations': 2.0}, 'options': [20.0, 10.0, 2.0], 'outputs': ['outRealUpperBand', 'outRealMiddleBand', 'outRealLowerBand'], 'output_index': 0, 'output_label': 'outRealUpperBand', 'warmup': 19, 'kernel': 'kernel_3b97270d585660f4', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['optInATRPeriod', 'int'], ['optInNbDev', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outRealUpperBand', 'double'], ['outRealMiddleBand', 'double'], ['outRealLowerBand', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_kc_outrealupperband_20_10d', {})
class Factor_talib_kc_outrealupperband_20_10d(PublicFactor):
    name = 'talib_kc_outrealupperband_20_10d'
    description = "Middle=EMA(TP,n)或EMA(C,n)；Upper/Lower=Middle±k×ATR(atr_n)，具体价格口径按来源；本行取输出outRealUpperBand。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_KC.c)；默认参数={'Time Period': 20.0, 'ATR Period': 10.0, 'Deviations': 2.0}；完整数值核及辅助调用在实现附录展开。；原目录：KC.outRealUpperBand（Time Period=20, ATR Period=10, Deviations=2.000000e+0）；追踪：PF00781；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
