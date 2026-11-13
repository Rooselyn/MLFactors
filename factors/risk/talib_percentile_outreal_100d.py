"""TA-Lib（技术指标及K线形态）

公式：窗口内指定分位数；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PERCENTILE.c)；默认参数={'Time Period': 100.0, 'Percentile': 50.0}；完整数值核及辅助调用在实现附录展开。；原目录：PERCENTILE.outReal（Time Period=100, Percentile=5.000000e+1）；追踪：PF00824；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_percentile_outreal_100d', 'root_function': 'TA_PERCENTILE', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 100.0, 'Percentile': 50.0}, 'options': [100.0, 50.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 99, 'kernel': 'kernel_b2b7b3c20134a15a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInPercentile', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_percentile_outreal_100d', {})
class Factor_talib_percentile_outreal_100d(PublicFactor):
    name = 'talib_percentile_outreal_100d'
    description = "窗口内指定分位数；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PERCENTILE.c)；默认参数={'Time Period': 100.0, 'Percentile': 50.0}；完整数值核及辅助调用在实现附录展开。；原目录：PERCENTILE.outReal（Time Period=100, Percentile=5.000000e+1）；追踪：PF00824；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
