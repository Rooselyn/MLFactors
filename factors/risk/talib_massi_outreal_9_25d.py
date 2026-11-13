"""TA-Lib（技术指标及K线形态）

公式：sum(EMA(H−L,fast)/EMA(EMA(H−L,fast),fast),slow)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MASSI.c)；默认参数={'Fast Period': 9.0, 'Slow Period': 25.0}；完整数值核及辅助调用在实现附录展开。；原目录：MASSI.outReal（Fast Period=9, Slow Period=25）；追踪：PF00809；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:massi（fast=9, slow=25）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_massi_outreal_9_25d', 'root_function': 'TA_MASSI', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Fast Period': 9.0, 'Slow Period': 25.0}, 'options': [9.0, 25.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 40, 'kernel': 'kernel_6826310ba2dac77a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInFastPeriod', 'int'], ['optInSlowPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_massi_outreal_9_25d', {})
class Factor_talib_massi_outreal_9_25d(PublicFactor):
    name = 'talib_massi_outreal_9_25d'
    description = "sum(EMA(H−L,fast)/EMA(EMA(H−L,fast),fast),slow)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MASSI.c)；默认参数={'Fast Period': 9.0, 'Slow Period': 25.0}；完整数值核及辅助调用在实现附录展开。；原目录：MASSI.outReal（Fast Period=9, Slow Period=25）；追踪：PF00809；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:massi（fast=9, slow=25）"
    INPUTS = INPUTS
    SPEC = SPEC
