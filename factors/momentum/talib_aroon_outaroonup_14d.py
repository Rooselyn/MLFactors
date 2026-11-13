"""TA-Lib（技术指标及K线形态）

公式：Up=100×最近窗口最高价位置/(n)，Down=100×最近窗口最低价位置/(n)；索引约定按来源；本行取输出outAroonUp。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_AROON.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：AROON.outAroonUp（Time Period=14）；追踪：PF00659；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:AROON.aroon_up（参数：period）、Pandas TA Classic:aroon（length=14, scalar=100）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_aroon_outaroonup_14d', 'root_function': 'TA_AROON', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outAroonDown', 'outAroonUp'], 'output_index': 1, 'output_label': 'outAroonUp', 'warmup': 14, 'kernel': 'kernel_62cd572db0ff3db7', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outAroonDown', 'double'], ['outAroonUp', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_aroon_outaroonup_14d', {})
class Factor_talib_aroon_outaroonup_14d(PublicFactor):
    name = 'talib_aroon_outaroonup_14d'
    description = "Up=100×最近窗口最高价位置/(n)，Down=100×最近窗口最低价位置/(n)；索引约定按来源；本行取输出outAroonUp。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_AROON.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：AROON.outAroonUp（Time Period=14）；追踪：PF00659；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:AROON.aroon_up（参数：period）、Pandas TA Classic:aroon（length=14, scalar=100）"
    INPUTS = INPUTS
    SPEC = SPEC
