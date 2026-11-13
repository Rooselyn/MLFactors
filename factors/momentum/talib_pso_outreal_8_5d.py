"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：double *sufHighest = &local_sufHighest[0];；double *preHighest = &local_preHighest[0];；double *sufLowest = &local_sufLowest[0];；double *preLowest = &local_preLowest[0];；emaBeta = (double)(optInEMAPeriod - 1) / (double)(optInEMAPeriod + 1);；warmBars = lookbackEMA + lookbackEMA;；sufHighest = TA_Malloc( sizeof(double)*optInFastK_Period );；preHighest = TA_Malloc( sizeof(double)*optInFastK_Period );；sufLowest = TA_Malloc( sizeof(double)*optInFastK_Period );；preLowest = TA_Malloc( sizeof(double)*optInFastK_Period );；blockNext = blockStart + optInFastK_Period;；nAvail = endIdx + 1 - blockNext;；tmp = inHigh[blockNext + i];；tmp = inLow[blockNext + i];；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PSO.c)；默认参数={'Fast-K Period': 8.0, 'EMA Period': 5.0}；完整数值核及辅助调用在实现附录展开。；原目录：PSO.outReal（Fast-K Period=8, EMA Period=5）；追踪：PF00829；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_pso_outreal_8_5d', 'root_function': 'TA_PSO', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Fast-K Period': 8.0, 'EMA Period': 5.0}, 'options': [8.0, 5.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 15, 'kernel': 'kernel_563c5277f9a43ac3', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInFastK_Period', 'int'], ['optInEMAPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_pso_outreal_8_5d', {})
class Factor_talib_pso_outreal_8_5d(PublicFactor):
    name = 'talib_pso_outreal_8_5d'
    description = "源码核心递推表达式（完整分支/参数见链接）：double *sufHighest = &local_sufHighest[0];；double *preHighest = &local_preHighest[0];；double *sufLowest = &local_sufLowest[0];；double *preLowest = &local_preLowest[0];；emaBeta = (double)(optInEMAPeriod - 1) / (double)(optInEMAPeriod + 1);；warmBars = lookbackEMA + lookbackEMA;；sufHighest = TA_Malloc( sizeof(double)*optInFastK_Period );；preHighest = TA_Malloc( sizeof(double)*optInFastK_Period );；sufLowest = TA_Malloc( sizeof(double)*optInFastK_Period );；preLowest = TA_Malloc( sizeof(double)*optInFastK_Period );；blockNext = blockStart + optInFastK_Period;；nAvail = endIdx + 1 - blockNext;；tmp = inHigh[blockNext + i];；tmp = inLow[blockNext + i];；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PSO.c)；默认参数={'Fast-K Period': 8.0, 'EMA Period': 5.0}；完整数值核及辅助调用在实现附录展开。；原目录：PSO.outReal（Fast-K Period=8, EMA Period=5）；追踪：PF00829；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
