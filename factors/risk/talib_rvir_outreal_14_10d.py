"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：for( i = 0; i < *outNBElement; i += 1 )；cur_outReal = 0.5 * (cur_tempHigh + cur_outReal);；sc_outReal = (double *)TA_Malloc( sizeof(double) * (size_t)historyLen );；subRc = TA_RVI_OpenAndFillInternal( &sub0, inHigh, (startIdx), (endIdx) + 1, optInTimePeriod, optInStdDevPeriod, &tempBegIdx, &tempNbElement, tempHigh );；subRc = TA_RVI_OpenAndFillInternal( &sub1, inLow, (startIdx), (endIdx) + 1, optInTimePeriod, optInStdDevPeriod, &dummyBegIdx, &dummyNBElement, sc_outReal );；for( i = 0; i < dummyNBElement; i += 1 )；sp = (struct TA_RVIR_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；stream->cur_outReal = *outReal;；const struct TA_RVIR_Stream *sp = stream;；TA_RetCode subRc = TA_RVI_Peek( (const TA_RVI_Stream *)sp->sub0, inHigh, &cur_tempHigh );；TA_RetCode subRc = TA_RVI_Peek( (const TA_RVI_Stream *)sp->sub1, inLow, &cur_outReal );；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_RVIR.c)；默认参数={'Time Period': 14.0, 'StdDev Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：RVIR.outReal（Time Period=14, StdDev Period=10）；追踪：PF00842；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_rvir_outreal_14_10d', 'root_function': 'TA_RVIR', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Time Period': 14.0, 'StdDev Period': 10.0}, 'options': [14.0, 10.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 22, 'kernel': 'kernel_e726bf121eb7494c', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInTimePeriod', 'int'], ['optInStdDevPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_rvir_outreal_14_10d', {})
class Factor_talib_rvir_outreal_14_10d(PublicFactor):
    name = 'talib_rvir_outreal_14_10d'
    description = "源码核心递推表达式（完整分支/参数见链接）：for( i = 0; i < *outNBElement; i += 1 )；cur_outReal = 0.5 * (cur_tempHigh + cur_outReal);；sc_outReal = (double *)TA_Malloc( sizeof(double) * (size_t)historyLen );；subRc = TA_RVI_OpenAndFillInternal( &sub0, inHigh, (startIdx), (endIdx) + 1, optInTimePeriod, optInStdDevPeriod, &tempBegIdx, &tempNbElement, tempHigh );；subRc = TA_RVI_OpenAndFillInternal( &sub1, inLow, (startIdx), (endIdx) + 1, optInTimePeriod, optInStdDevPeriod, &dummyBegIdx, &dummyNBElement, sc_outReal );；for( i = 0; i < dummyNBElement; i += 1 )；sp = (struct TA_RVIR_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；stream->cur_outReal = *outReal;；const struct TA_RVIR_Stream *sp = stream;；TA_RetCode subRc = TA_RVI_Peek( (const TA_RVI_Stream *)sp->sub0, inHigh, &cur_tempHigh );；TA_RetCode subRc = TA_RVI_Peek( (const TA_RVI_Stream *)sp->sub1, inLow, &cur_outReal );；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_RVIR.c)；默认参数={'Time Period': 14.0, 'StdDev Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：RVIR.outReal（Time Period=14, StdDev Period=10）；追踪：PF00842；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
