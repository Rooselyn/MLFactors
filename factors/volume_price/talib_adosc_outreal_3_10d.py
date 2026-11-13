"""TA-Lib（技术指标及K线形态）

公式：EMA(AD,fast)−EMA(AD,slow)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ADOSC.c)；默认参数={'Fast Period': 3.0, 'Slow Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：ADOSC.outReal（Fast Period=3, Slow Period=10）；追踪：PF00651；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:ADOSC.adosc（参数：short_period, long_period）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'talib_adosc_outreal_3_10d', 'root_function': 'TA_ADOSC', 'required_inputs': ['inHigh', 'inLow', 'inClose', 'inVolume'], 'parameters': {'Fast Period': 3.0, 'Slow Period': 10.0}, 'options': [3.0, 10.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 9, 'kernel': 'kernel_6cc0b73607e4db59', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['inVolume', 'double'], ['optInFastPeriod', 'int'], ['optInSlowPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_adosc_outreal_3_10d', {})
class Factor_talib_adosc_outreal_3_10d(PublicFactor):
    name = 'talib_adosc_outreal_3_10d'
    description = "EMA(AD,fast)−EMA(AD,slow)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ADOSC.c)；默认参数={'Fast Period': 3.0, 'Slow Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：ADOSC.outReal（Fast Period=3, Slow Period=10）；追踪：PF00651；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:ADOSC.adosc（参数：short_period, long_period）"
    INPUTS = INPUTS
    SPEC = SPEC
