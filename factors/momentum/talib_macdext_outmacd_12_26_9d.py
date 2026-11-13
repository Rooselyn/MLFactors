"""TA-Lib（技术指标及K线形态）

公式：DIF=MA_type_fast(C,fast)−MA_type_slow(C,slow)；Signal=MA_type_signal(DIF,signal)；Hist=DIF−Signal；本行取输出outMACD。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MACDEXT.c)；默认参数={'Fast Period': 12.0, 'Fast MA': 0.0, 'Slow Period': 26.0, 'Slow MA': 0.0, 'Signal Period': 9.0, 'Signal MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：MACDEXT.outMACD（Fast Period=12, Fast MA=0, Slow Period=26, Slow MA=0, Signal Period=9, Signal MA=0）；追踪：PF00800；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_macdext_outmacd_12_26_9d', 'root_function': 'TA_MACDEXT', 'required_inputs': ['inReal'], 'parameters': {'Fast Period': 12.0, 'Fast MA': 0.0, 'Slow Period': 26.0, 'Slow MA': 0.0, 'Signal Period': 9.0, 'Signal MA': 0.0}, 'options': [12.0, 0.0, 26.0, 0.0, 9.0, 0.0], 'outputs': ['outMACD', 'outMACDSignal', 'outMACDHist'], 'output_index': 0, 'output_label': 'outMACD', 'warmup': 33, 'kernel': 'kernel_aafcf097288a670a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInFastPeriod', 'int'], ['optInFastMAType', 'int'], ['optInSlowPeriod', 'int'], ['optInSlowMAType', 'int'], ['optInSignalPeriod', 'int'], ['optInSignalMAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outMACD', 'double'], ['outMACDSignal', 'double'], ['outMACDHist', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_macdext_outmacd_12_26_9d', {})
class Factor_talib_macdext_outmacd_12_26_9d(PublicFactor):
    name = 'talib_macdext_outmacd_12_26_9d'
    description = "DIF=MA_type_fast(C,fast)−MA_type_slow(C,slow)；Signal=MA_type_signal(DIF,signal)；Hist=DIF−Signal；本行取输出outMACD。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MACDEXT.c)；默认参数={'Fast Period': 12.0, 'Fast MA': 0.0, 'Slow Period': 26.0, 'Slow MA': 0.0, 'Signal Period': 9.0, 'Signal MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：MACDEXT.outMACD（Fast Period=12, Fast MA=0, Slow Period=26, Slow MA=0, Signal Period=9, Signal MA=0）；追踪：PF00800；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
