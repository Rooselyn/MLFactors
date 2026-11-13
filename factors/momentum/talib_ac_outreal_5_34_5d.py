"""TA-Lib（技术指标及K线形态）

公式：AO−SMA(AO,signal)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_AC.c)；默认参数={'Fast Period': 5.0, 'Slow Period': 34.0, 'Signal Period': 5.0}；完整数值核及辅助调用在实现附录展开。；原目录：AC.outReal（Fast Period=5, Slow Period=34, Signal Period=5）；追踪：PF00646；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_ac_outreal_5_34_5d', 'root_function': 'TA_AC', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Fast Period': 5.0, 'Slow Period': 34.0, 'Signal Period': 5.0}, 'options': [5.0, 34.0, 5.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 37, 'kernel': 'kernel_e95ecc0c429f0559', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInFastPeriod', 'int'], ['optInSlowPeriod', 'int'], ['optInSignalPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_ac_outreal_5_34_5d', {})
class Factor_talib_ac_outreal_5_34_5d(PublicFactor):
    name = 'talib_ac_outreal_5_34_5d'
    description = "AO−SMA(AO,signal)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_AC.c)；默认参数={'Fast Period': 5.0, 'Slow Period': 34.0, 'Signal Period': 5.0}；完整数值核及辅助调用在实现附录展开。；原目录：AC.outReal（Fast Period=5, Slow Period=34, Signal Period=5）；追踪：PF00646；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
