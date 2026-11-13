"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：root = (int)sqrt((double)optInTimePeriod);；double *slot_sufHigh = &local_slot_sufHigh[0];；double *slot_sufLow = &local_slot_sufLow[0];；double *slot_oldHigh = &local_slot_oldHigh[0];；double *slot_oldLow = &local_slot_oldLow[0];；expScale = -4.6 / 0.6931471805599453;；half = optInTimePeriod / 2;；slot_sufHigh = TA_Malloc( sizeof(double)*half );；slot_sufLow = TA_Malloc( sizeof(double)*half );；slot_oldHigh = TA_Malloc( sizeof(double)*half );；slot_oldLow = TA_Malloc( sizeof(double)*half );；today = startIdx - lookbackTotal + 1;；i += 1;；hi1 = slot_sufHigh[slot_Idx + 1];；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_FRAMA.c)；默认参数={'Time Period': 16.0}；完整数值核及辅助调用在实现附录展开。；原目录：FRAMA.outReal（Time Period=16）；追踪：PF00764；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_frama_outreal_16d', 'root_function': 'TA_FRAMA', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Time Period': 16.0}, 'options': [16.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 16, 'kernel': 'kernel_e4aab440bf5314a7', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_frama_outreal_16d', {})
class Factor_talib_frama_outreal_16d(PublicFactor):
    name = 'talib_frama_outreal_16d'
    description = "源码核心递推表达式（完整分支/参数见链接）：root = (int)sqrt((double)optInTimePeriod);；double *slot_sufHigh = &local_slot_sufHigh[0];；double *slot_sufLow = &local_slot_sufLow[0];；double *slot_oldHigh = &local_slot_oldHigh[0];；double *slot_oldLow = &local_slot_oldLow[0];；expScale = -4.6 / 0.6931471805599453;；half = optInTimePeriod / 2;；slot_sufHigh = TA_Malloc( sizeof(double)*half );；slot_sufLow = TA_Malloc( sizeof(double)*half );；slot_oldHigh = TA_Malloc( sizeof(double)*half );；slot_oldLow = TA_Malloc( sizeof(double)*half );；today = startIdx - lookbackTotal + 1;；i += 1;；hi1 = slot_sufHigh[slot_Idx + 1];；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_FRAMA.c)；默认参数={'Time Period': 16.0}；完整数值核及辅助调用在实现附录展开。；原目录：FRAMA.outReal（Time Period=16）；追踪：PF00764；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
