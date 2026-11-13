"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：double *emaRing = &local_emaRing[0];；lookbackTotal = TA_EMA_Lookback(optInTimePeriod) + TA_ROCP_Lookback(optInROCPeriod);；emaRing = TA_Malloc( sizeof(double)*optInROCPeriod );；emaBeta = (double)(optInTimePeriod - 1) / (double)(optInTimePeriod + 1);；tempReal += inHigh[today] - inLow[today];；today += 1;；prevEMA = tempReal / optInTimePeriod;；prevEMA = fma(emaBeta, prevEMA, optInK_1 * tempReal);；tempReal += (double)inHigh[today] - (double)inLow[today];；prevEMA = fma(sp->emaBeta, prevEMA, sp->optInK_1 * tempReal);；sp->emaRing_Idx = sp->emaRing_Idx + 1;；sp->cur_outReal = *outReal;；sp = (struct TA_CVI_Stream *)TA_Malloc( sizeof(*sp) );；sp->cbSize_emaRing = maxIdx_emaRing + 1;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CVI.c)；默认参数={'Time Period': 10.0, 'ROC Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：CVI.outReal（Time Period=10, ROC Period=10）；追踪：PF00745；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:cvi（length=10）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_cvi_outreal_10_10d', 'root_function': 'TA_CVI', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Time Period': 10.0, 'ROC Period': 10.0}, 'options': [10.0, 10.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 19, 'kernel': 'kernel_5de017330476a1b1', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInTimePeriod', 'int'], ['optInROCPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_cvi_outreal_10_10d', {})
class Factor_talib_cvi_outreal_10_10d(PublicFactor):
    name = 'talib_cvi_outreal_10_10d'
    description = "源码核心递推表达式（完整分支/参数见链接）：double *emaRing = &local_emaRing[0];；lookbackTotal = TA_EMA_Lookback(optInTimePeriod) + TA_ROCP_Lookback(optInROCPeriod);；emaRing = TA_Malloc( sizeof(double)*optInROCPeriod );；emaBeta = (double)(optInTimePeriod - 1) / (double)(optInTimePeriod + 1);；tempReal += inHigh[today] - inLow[today];；today += 1;；prevEMA = tempReal / optInTimePeriod;；prevEMA = fma(emaBeta, prevEMA, optInK_1 * tempReal);；tempReal += (double)inHigh[today] - (double)inLow[today];；prevEMA = fma(sp->emaBeta, prevEMA, sp->optInK_1 * tempReal);；sp->emaRing_Idx = sp->emaRing_Idx + 1;；sp->cur_outReal = *outReal;；sp = (struct TA_CVI_Stream *)TA_Malloc( sizeof(*sp) );；sp->cbSize_emaRing = maxIdx_emaRing + 1;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_CVI.c)；默认参数={'Time Period': 10.0, 'ROC Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：CVI.outReal（Time Period=10, ROC Period=10）；追踪：PF00745；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:cvi（length=10）"
    INPUTS = INPUTS
    SPEC = SPEC
