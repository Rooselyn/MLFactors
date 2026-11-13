"""TA-Lib（技术指标及K线形态）

公式：DIF=EMA(C,12)−EMA(C,26)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；本行取输出outMACDSignal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MACDFIX.c)；默认参数={'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：MACDFIX.outMACDSignal（Signal Period=9）；追踪：PF00804；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_macdfix_outmacdsignal_9d', 'root_function': 'TA_MACDFIX', 'required_inputs': ['inReal'], 'parameters': {'Signal Period': 9.0}, 'options': [9.0], 'outputs': ['outMACD', 'outMACDSignal', 'outMACDHist'], 'output_index': 1, 'output_label': 'outMACDSignal', 'warmup': 33, 'kernel': 'kernel_71940294151fbbe5', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInSignalPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outMACD', 'double'], ['outMACDSignal', 'double'], ['outMACDHist', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_macdfix_outmacdsignal_9d', {})
class Factor_talib_macdfix_outmacdsignal_9d(PublicFactor):
    name = 'talib_macdfix_outmacdsignal_9d'
    description = "DIF=EMA(C,12)−EMA(C,26)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；本行取输出outMACDSignal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MACDFIX.c)；默认参数={'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：MACDFIX.outMACDSignal（Signal Period=9）；追踪：PF00804；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
