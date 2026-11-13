"""TA-Lib（技术指标及K线形态）

公式：基础上下轨=(H+L)/2±kATR(n)；按前轨与前收盘递推最终轨道，收盘穿轨改变方向；输出当时可知轨道；本行取输出outTrend。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SUPERTREND.c)；默认参数={'Time Period': 10.0, 'Multiplier': 3.0}；完整数值核及辅助调用在实现附录展开。；原目录：SUPERTREND.outTrend（Time Period=10, Multiplier=3.000000e+0）；追踪：PF00858；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_supertrend_outtrend_10d', 'root_function': 'TA_SUPERTREND', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 10.0, 'Multiplier': 3.0}, 'options': [10.0, 3.0], 'outputs': ['outSupertrend', 'outTrend'], 'output_index': 1, 'output_label': 'outTrend', 'warmup': 10, 'kernel': 'kernel_ef8fa1ea40cf86a7', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['optInMultiplier', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outSupertrend', 'double'], ['outTrend', 'int']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_supertrend_outtrend_10d', {})
class Factor_talib_supertrend_outtrend_10d(PublicFactor):
    name = 'talib_supertrend_outtrend_10d'
    description = "基础上下轨=(H+L)/2±kATR(n)；按前轨与前收盘递推最终轨道，收盘穿轨改变方向；输出当时可知轨道；本行取输出outTrend。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SUPERTREND.c)；默认参数={'Time Period': 10.0, 'Multiplier': 3.0}；完整数值核及辅助调用在实现附录展开。；原目录：SUPERTREND.outTrend（Time Period=10, Multiplier=3.000000e+0）；追踪：PF00858；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
