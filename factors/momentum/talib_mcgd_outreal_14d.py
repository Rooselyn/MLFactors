"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：today += 1;；ratio = tempReal / prevMD;；tempMD = prevMD + (tempReal - prevMD) / (period * (ratio * ratio * (ratio * ratio)));；nbMCGD = endIdx - startIdx + 1;；ratio = tempReal / sp->prevMD;；tempMD = sp->prevMD + (tempReal - sp->prevMD) / (sp->period * (ratio * ratio * (ratio * ratio)));；sp->cur_outReal = *outReal;；sp = (struct TA_MCGD_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；const struct TA_MCGD_Stream *sp = stream;；tempMD = prevMD + (tempReal - prevMD) / (sp->period * (ratio * ratio * (ratio * ratio)));；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MCGD.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：MCGD.outReal（Time Period=14）；追踪：PF00811；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_mcgd_outreal_14d', 'root_function': 'TA_MCGD', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 13, 'kernel': 'kernel_45a3612df14f1bc4', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_mcgd_outreal_14d', {})
class Factor_talib_mcgd_outreal_14d(PublicFactor):
    name = 'talib_mcgd_outreal_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：today += 1;；ratio = tempReal / prevMD;；tempMD = prevMD + (tempReal - prevMD) / (period * (ratio * ratio * (ratio * ratio)));；nbMCGD = endIdx - startIdx + 1;；ratio = tempReal / sp->prevMD;；tempMD = sp->prevMD + (tempReal - sp->prevMD) / (sp->period * (ratio * ratio * (ratio * ratio)));；sp->cur_outReal = *outReal;；sp = (struct TA_MCGD_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；const struct TA_MCGD_Stream *sp = stream;；tempMD = prevMD + (tempReal - prevMD) / (sp->period * (ratio * ratio * (ratio * ratio)));；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MCGD.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：MCGD.outReal（Time Period=14）；追踪：PF00811；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
