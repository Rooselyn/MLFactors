"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：double *dsBuffer = &local_dsBuffer[0];；dsBuffer = TA_Malloc( sizeof(double)*optInSignalPeriod );；beta1 = (double)(optInFirstPeriod - 1) / (double)(optInFirstPeriod + 1);；beta2 = (double)(optInSecondPeriod - 1) / (double)(optInSecondPeriod + 1);；invPeriod = 1.0 / (double)optInTimePeriod;；rsiBar = today + optInTimePeriod;；today = today + 1;；prevGain += gainDelta;；prevLoss += gainDelta - tempValue2;；prevLoss *= invPeriod;；prevGain *= invPeriod;；tempValue1 = prevGain + prevLoss;；rsiValue = 100.0 * (prevGain / tempValue1);；sum1 = sum1 + rsiValue;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_DOSC.c)；默认参数={'Time Period': 14.0, 'First Smoothing Period': 5.0, 'Second Smoothing Period': 3.0, 'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：DOSC.outReal（Time Period=14, First Smoothing Period=5, Second Smoothing Period=3, Signal Period=9）；追踪：PF00750；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_dosc_outreal_14_5_3_9d', 'root_function': 'TA_DOSC', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 14.0, 'First Smoothing Period': 5.0, 'Second Smoothing Period': 3.0, 'Signal Period': 9.0}, 'options': [14.0, 5.0, 3.0, 9.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 28, 'kernel': 'kernel_eee7ce7e644f16e0', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInFirstPeriod', 'int'], ['optInSecondPeriod', 'int'], ['optInSignalPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_dosc_outreal_14_5_3_9d', {})
class Factor_talib_dosc_outreal_14_5_3_9d(PublicFactor):
    name = 'talib_dosc_outreal_14_5_3_9d'
    description = "源码核心递推表达式（完整分支/参数见链接）：double *dsBuffer = &local_dsBuffer[0];；dsBuffer = TA_Malloc( sizeof(double)*optInSignalPeriod );；beta1 = (double)(optInFirstPeriod - 1) / (double)(optInFirstPeriod + 1);；beta2 = (double)(optInSecondPeriod - 1) / (double)(optInSecondPeriod + 1);；invPeriod = 1.0 / (double)optInTimePeriod;；rsiBar = today + optInTimePeriod;；today = today + 1;；prevGain += gainDelta;；prevLoss += gainDelta - tempValue2;；prevLoss *= invPeriod;；prevGain *= invPeriod;；tempValue1 = prevGain + prevLoss;；rsiValue = 100.0 * (prevGain / tempValue1);；sum1 = sum1 + rsiValue;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_DOSC.c)；默认参数={'Time Period': 14.0, 'First Smoothing Period': 5.0, 'Second Smoothing Period': 3.0, 'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：DOSC.outReal（Time Period=14, First Smoothing Period=5, Second Smoothing Period=3, Signal Period=9）；追踪：PF00750；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
