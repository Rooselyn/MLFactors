"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：retValue = max(retValue,TA_RSI_Lookback(optInStreakPeriod) + 1);；retValue = max(retValue,TA_PERCENTRANK_Lookback(optInRankPeriod) + TA_ROCP_Lookback(1));；today = anchorIdx + 1;；streak = (streak > 0.0) ? streak + 1.0 : 1.0;；today += 1;；retCode = TA_RSI(anchorIdx + TA_RSI_Lookback(optInTimePeriod),endIdx,inReal,optInTimePeriod,&tempBegIdx,&rsiNb,tempRSI);；offsetRSI = rsiNb - *outNBElement;；offsetStreak = streakNb - *outNBElement;；for( i = 0; i < (int)*outNBElement; i += 1 )；retCode = TA_S_RSI(anchorIdx + TA_RSI_Lookback(optInTimePeriod),endIdx,inReal,optInTimePeriod,&tempBegIdx,&rsiNb,tempRSI);；sp->streak = (sp->streak > 0.0) ? sp->streak + 1.0 : 1.0;；cur_outReal = (cur_tempRSI + cur_tempStreakRSI + cur_outReal) / 3.0;；sc_outReal = (double *)TA_Malloc( sizeof(double) * (size_t)historyLen );；subRc = TA_RSI_OpenAndFillInternal( &sub0, tempStreak, (0), (outIdx - 1) + 1, optInStreakPeriod, &tempBegIdx, &streakNb, tempStreakRSI );；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CRSI.c)；默认参数={'Time Period': 3.0, 'Streak Period': 2.0, 'Rank Period': 100.0}；完整数值核及辅助调用在实现附录展开。；原目录：CRSI.outReal（Time Period=3, Streak Period=2, Rank Period=100）；追踪：PF00743；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_crsi_outreal_3_2_100d', 'root_function': 'TA_CRSI', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 3.0, 'Streak Period': 2.0, 'Rank Period': 100.0}, 'options': [3.0, 2.0, 100.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 101, 'kernel': 'kernel_d6b5f44baf3115db', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInStreakPeriod', 'int'], ['optInRankPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_crsi_outreal_3_2_100d', {})
class Factor_talib_crsi_outreal_3_2_100d(PublicFactor):
    name = 'talib_crsi_outreal_3_2_100d'
    description = "源码核心递推表达式（完整分支/参数见链接）：retValue = max(retValue,TA_RSI_Lookback(optInStreakPeriod) + 1);；retValue = max(retValue,TA_PERCENTRANK_Lookback(optInRankPeriod) + TA_ROCP_Lookback(1));；today = anchorIdx + 1;；streak = (streak > 0.0) ? streak + 1.0 : 1.0;；today += 1;；retCode = TA_RSI(anchorIdx + TA_RSI_Lookback(optInTimePeriod),endIdx,inReal,optInTimePeriod,&tempBegIdx,&rsiNb,tempRSI);；offsetRSI = rsiNb - *outNBElement;；offsetStreak = streakNb - *outNBElement;；for( i = 0; i < (int)*outNBElement; i += 1 )；retCode = TA_S_RSI(anchorIdx + TA_RSI_Lookback(optInTimePeriod),endIdx,inReal,optInTimePeriod,&tempBegIdx,&rsiNb,tempRSI);；sp->streak = (sp->streak > 0.0) ? sp->streak + 1.0 : 1.0;；cur_outReal = (cur_tempRSI + cur_tempStreakRSI + cur_outReal) / 3.0;；sc_outReal = (double *)TA_Malloc( sizeof(double) * (size_t)historyLen );；subRc = TA_RSI_OpenAndFillInternal( &sub0, tempStreak, (0), (outIdx - 1) + 1, optInStreakPeriod, &tempBegIdx, &streakNb, tempStreakRSI );；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CRSI.c)；默认参数={'Time Period': 3.0, 'Streak Period': 2.0, 'Rank Period': 100.0}；完整数值核及辅助调用在实现附录展开。；原目录：CRSI.outReal（Time Period=3, Streak Period=2, Rank Period=100）；追踪：PF00743；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
