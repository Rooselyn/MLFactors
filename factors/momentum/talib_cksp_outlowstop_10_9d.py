"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：double *hhBuf = &local_hhBuf[0];；double *llBuf = &local_llBuf[0];；double *hsBuf = &local_hsBuf[0];；double *lsBuf = &local_lsBuf[0];；hhBuf = TA_Malloc( sizeof(double)*optInTimePeriod );；llBuf = TA_Malloc( sizeof(double)*optInTimePeriod );；hsBuf = TA_Malloc( sizeof(double)*optInStopPeriod );；lsBuf = TA_Malloc( sizeof(double)*optInStopPeriod );；wBeta = (double)(optInTimePeriod - 1) / (double)optInTimePeriod;；today = startIdx - lookbackTotal + 1;；periodTotal += greatest;；today += 1;；prevATR = periodTotal / optInTimePeriod;；prevATR = fma(wBeta, prevATR, wAlpha * greatest);；本行取输出outLowStop。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CKSP.c)；默认参数={'Time Period': 10.0, 'Multiplier': 1.0, 'Stop Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：CKSP.outLowStop（Time Period=10, Multiplier=1.000000e+0, Stop Period=9）；追踪：PF00737；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:cksp（mamode='sma'）
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
SPEC = {'name': 'talib_cksp_outlowstop_10_9d', 'root_function': 'TA_CKSP', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 10.0, 'Multiplier': 1.0, 'Stop Period': 9.0}, 'options': [10.0, 1.0, 9.0], 'outputs': ['outHighStop', 'outLowStop'], 'output_index': 1, 'output_label': 'outLowStop', 'warmup': 18, 'kernel': 'kernel_631e3d5f6246ee8c', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['optInMultiplier', 'double'], ['optInStopPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outHighStop', 'double'], ['outLowStop', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_cksp_outlowstop_10_9d', {})
class Factor_talib_cksp_outlowstop_10_9d(PublicFactor):
    name = 'talib_cksp_outlowstop_10_9d'
    description = "源码核心递推表达式（完整分支/参数见链接）：double *hhBuf = &local_hhBuf[0];；double *llBuf = &local_llBuf[0];；double *hsBuf = &local_hsBuf[0];；double *lsBuf = &local_lsBuf[0];；hhBuf = TA_Malloc( sizeof(double)*optInTimePeriod );；llBuf = TA_Malloc( sizeof(double)*optInTimePeriod );；hsBuf = TA_Malloc( sizeof(double)*optInStopPeriod );；lsBuf = TA_Malloc( sizeof(double)*optInStopPeriod );；wBeta = (double)(optInTimePeriod - 1) / (double)optInTimePeriod;；today = startIdx - lookbackTotal + 1;；periodTotal += greatest;；today += 1;；prevATR = periodTotal / optInTimePeriod;；prevATR = fma(wBeta, prevATR, wAlpha * greatest);；本行取输出outLowStop。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CKSP.c)；默认参数={'Time Period': 10.0, 'Multiplier': 1.0, 'Stop Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：CKSP.outLowStop（Time Period=10, Multiplier=1.000000e+0, Stop Period=9）；追踪：PF00737；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:cksp（mamode='sma'）"
    INPUTS = INPUTS
    SPEC = SPEC
