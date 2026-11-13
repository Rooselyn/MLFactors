"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：double *lineRing = &local_lineRing[0];；double *lineSufHi = &local_lineSufHi[0];；double *lineSufLo = &local_lineSufLo[0];；double *pfRing = &local_pfRing[0];；double *pfSufHi = &local_pfSufHi[0];；double *pfSufLo = &local_pfSufLo[0];；fastBeta = (double)(optInFastPeriod - 1) / (double)(optInFastPeriod + 1);；slowBeta = (double)(optInSlowPeriod - 1) / (double)(optInSlowPeriod + 1);；lineRing = TA_Malloc( sizeof(double)*optInCyclePeriod );；lineSufHi = TA_Malloc( sizeof(double)*optInCyclePeriod );；lineSufLo = TA_Malloc( sizeof(double)*optInCyclePeriod );；pfRing = TA_Malloc( sizeof(double)*optInCyclePeriod );；pfSufHi = TA_Malloc( sizeof(double)*optInCyclePeriod );；pfSufLo = TA_Malloc( sizeof(double)*optInCyclePeriod );；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STC.c)；默认参数={'Fast Period': 23.0, 'Slow Period': 50.0, 'Cycle Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：STC.outReal（Fast Period=23, Slow Period=50, Cycle Period=10）；追踪：PF00849；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_stc_outreal_23_50_10d', 'root_function': 'TA_STC', 'required_inputs': ['inReal'], 'parameters': {'Fast Period': 23.0, 'Slow Period': 50.0, 'Cycle Period': 10.0}, 'options': [23.0, 50.0, 10.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 67, 'kernel': 'kernel_56ced573b3162f6a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInFastPeriod', 'int'], ['optInSlowPeriod', 'int'], ['optInCyclePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_stc_outreal_23_50_10d', {})
class Factor_talib_stc_outreal_23_50_10d(PublicFactor):
    name = 'talib_stc_outreal_23_50_10d'
    description = "源码核心递推表达式（完整分支/参数见链接）：double *lineRing = &local_lineRing[0];；double *lineSufHi = &local_lineSufHi[0];；double *lineSufLo = &local_lineSufLo[0];；double *pfRing = &local_pfRing[0];；double *pfSufHi = &local_pfSufHi[0];；double *pfSufLo = &local_pfSufLo[0];；fastBeta = (double)(optInFastPeriod - 1) / (double)(optInFastPeriod + 1);；slowBeta = (double)(optInSlowPeriod - 1) / (double)(optInSlowPeriod + 1);；lineRing = TA_Malloc( sizeof(double)*optInCyclePeriod );；lineSufHi = TA_Malloc( sizeof(double)*optInCyclePeriod );；lineSufLo = TA_Malloc( sizeof(double)*optInCyclePeriod );；pfRing = TA_Malloc( sizeof(double)*optInCyclePeriod );；pfSufHi = TA_Malloc( sizeof(double)*optInCyclePeriod );；pfSufLo = TA_Malloc( sizeof(double)*optInCyclePeriod );；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STC.c)；默认参数={'Fast Period': 23.0, 'Slow Period': 50.0, 'Cycle Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：STC.outReal（Fast Period=23, Slow Period=50, Cycle Period=10）；追踪：PF00849；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
