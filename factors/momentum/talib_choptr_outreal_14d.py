"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：sumTR += trueHigh - trueLow;；outIdx += 1;；today += 1;；tempHT = sp->win_i_inHigh[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；tempLT = sp->win_i_inLow[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；prevClose = sp->win_i_inClose[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；sp->cur_outReal = *outReal;；sp->winPos_i = sp->winPos_i + 1;；sp = (struct TA_CHOPTR_Stream *)TA_Malloc( sizeof(*sp) );；sp->winCap_i = (int)(optInTimePeriod + 1);；sp->win_i_inHigh = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；sp->win_i_inLow = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；sp->win_i_inClose = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；sp->outRangeBegIdx = *outBegIdx;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CHOPTR.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：CHOPTR.outReal（Time Period=14）；追踪：PF00735；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_choptr_outreal_14d', 'root_function': 'TA_CHOPTR', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 14, 'kernel': 'kernel_e6eaae962fdde53f', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_choptr_outreal_14d', {})
class Factor_talib_choptr_outreal_14d(PublicFactor):
    name = 'talib_choptr_outreal_14d'
    description = "源码核心递推表达式（完整分支/参数见链接）：sumTR += trueHigh - trueLow;；outIdx += 1;；today += 1;；tempHT = sp->win_i_inHigh[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；tempLT = sp->win_i_inLow[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；prevClose = sp->win_i_inClose[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；sp->cur_outReal = *outReal;；sp->winPos_i = sp->winPos_i + 1;；sp = (struct TA_CHOPTR_Stream *)TA_Malloc( sizeof(*sp) );；sp->winCap_i = (int)(optInTimePeriod + 1);；sp->win_i_inHigh = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；sp->win_i_inLow = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；sp->win_i_inClose = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；sp->outRangeBegIdx = *outBegIdx;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CHOPTR.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：CHOPTR.outReal（Time Period=14）；追踪：PF00735；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
