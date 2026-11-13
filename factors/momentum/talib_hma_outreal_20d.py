"""TA-Lib（技术指标及K线形态）

公式：WMA(2WMA(C,n/2)−WMA(C,n),sqrt(n))；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HMA.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：HMA.outReal（Time Period=20）；追踪：PF00769；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:HMA.hma（参数：period）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_hma_outreal_20d', 'root_function': 'TA_HMA', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 20.0}, 'options': [20.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 22, 'kernel': 'kernel_e03f37890e7b7efe', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_hma_outreal_20d', {})
class Factor_talib_hma_outreal_20d(PublicFactor):
    name = 'talib_hma_outreal_20d'
    description = "WMA(2WMA(C,n/2)−WMA(C,n),sqrt(n))；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HMA.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：HMA.outReal（Time Period=20）；追踪：PF00769；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:HMA.hma（参数：period）"
    INPUTS = INPUTS
    SPEC = SPEC
