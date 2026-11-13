"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：tempReal = inHigh[i] + inLow[i];；tempReal = 4 * (inHigh[i] - inLow[i]) / tempReal;；periodTotalUpper += inHigh[i] * (1 + tempReal);；periodTotalLower += inLow[i] * (1 - tempReal);；periodTotalUpper += inHigh[i];；periodTotalLower += inLow[i];；periodTotalMiddle += inClose[i];；i = i + 1;；tempReal = inHigh[trailingIdx] + inLow[trailingIdx];；tempReal = 4 * (inHigh[trailingIdx] - inLow[trailingIdx]) / tempReal;；periodTotalUpper -= inHigh[trailingIdx] * (1 + tempReal);；periodTotalLower -= inLow[trailingIdx] * (1 - tempReal);；trailingIdx = trailingIdx + 1;；outIdx = outIdx + 1;；本行取输出outRealUpperBand。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ACCBANDS.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：ACCBANDS.outRealUpperBand（Time Period=20）；追踪：PF00647；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:accbands（length=20, mamode='sma'）
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
SPEC = {'name': 'talib_accbands_outrealupperband_20d', 'root_function': 'TA_ACCBANDS', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 20.0}, 'options': [20.0], 'outputs': ['outRealUpperBand', 'outRealMiddleBand', 'outRealLowerBand'], 'output_index': 0, 'output_label': 'outRealUpperBand', 'warmup': 19, 'kernel': 'kernel_4a62159180cf1f78', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outRealUpperBand', 'double'], ['outRealMiddleBand', 'double'], ['outRealLowerBand', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_accbands_outrealupperband_20d', {})
class Factor_talib_accbands_outrealupperband_20d(PublicFactor):
    name = 'talib_accbands_outrealupperband_20d'
    description = "源码核心递推表达式（完整分支/参数见链接）：tempReal = inHigh[i] + inLow[i];；tempReal = 4 * (inHigh[i] - inLow[i]) / tempReal;；periodTotalUpper += inHigh[i] * (1 + tempReal);；periodTotalLower += inLow[i] * (1 - tempReal);；periodTotalUpper += inHigh[i];；periodTotalLower += inLow[i];；periodTotalMiddle += inClose[i];；i = i + 1;；tempReal = inHigh[trailingIdx] + inLow[trailingIdx];；tempReal = 4 * (inHigh[trailingIdx] - inLow[trailingIdx]) / tempReal;；periodTotalUpper -= inHigh[trailingIdx] * (1 + tempReal);；periodTotalLower -= inLow[trailingIdx] * (1 - tempReal);；trailingIdx = trailingIdx + 1;；outIdx = outIdx + 1;；本行取输出outRealUpperBand。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ACCBANDS.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：ACCBANDS.outRealUpperBand（Time Period=20）；追踪：PF00647；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:accbands（length=20, mamode='sma'）"
    INPUTS = INPUTS
    SPEC = SPEC
