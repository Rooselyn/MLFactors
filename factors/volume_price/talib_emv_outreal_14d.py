"""TA-Lib（技术指标及K线形态）

公式：((H+L)/2−(H[-1]+L[-1])/2)×(H−L)/V；成交量缩放及平滑按来源；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_EMV.c)；默认参数={'Time Period': 14.0, 'Volume Divisor': 10000.0}；完整数值核及辅助调用在实现附录展开。；原目录：EMV.outReal（Time Period=14, Volume Divisor=1.000000e+4）；追踪：PF00755；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'talib_emv_outreal_14d', 'root_function': 'TA_EMV', 'required_inputs': ['inHigh', 'inLow', 'inVolume'], 'parameters': {'Time Period': 14.0, 'Volume Divisor': 10000.0}, 'options': [14.0, 10000.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 14, 'kernel': 'kernel_2ffe164bfce45eda', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inVolume', 'double'], ['optInTimePeriod', 'int'], ['optInVolumeDivisor', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_emv_outreal_14d', {})
class Factor_talib_emv_outreal_14d(PublicFactor):
    name = 'talib_emv_outreal_14d'
    description = "((H+L)/2−(H[-1]+L[-1])/2)×(H−L)/V；成交量缩放及平滑按来源；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_EMV.c)；默认参数={'Time Period': 14.0, 'Volume Divisor': 10000.0}；完整数值核及辅助调用在实现附录展开。；原目录：EMV.outReal（Time Period=14, Volume Divisor=1.000000e+4）；追踪：PF00755；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
