"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：wBeta = (double)(optInTimePeriod - 1) / (double)optInTimePeriod;；invPeriod = 1.0 / (double)optInStdDevPeriod;；today = anchorIdx + nbInitialElementNeeded;；for( j = anchorIdx; j < today; j += 1 )；periodTotal1 += tempReal;；tempReal *= tempReal;；periodTotal2 += tempReal;；barsSinceReseed = 32 * optInStdDevPeriod;；meanValue1 = periodTotal1 * invPeriod;；variance = periodTotal2 * invPeriod - meanValue1 * meanValue1;；trailingIdx += 1;；for( j = windowStart; j <= today; j += 1 )；tempReal += inReal[j];；shift = tempReal * invPeriod;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_RVI.c)；默认参数={'Time Period': 14.0, 'StdDev Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：RVI.outReal（Time Period=14, StdDev Period=10）；追踪：PF00841；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_rvi_outreal_14_10d', 'root_function': 'TA_RVI', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 14.0, 'StdDev Period': 10.0}, 'options': [14.0, 10.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 22, 'kernel': 'kernel_b5142c7e11533bbc', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInStdDevPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_rvi_outreal_14_10d', {})
class Factor_talib_rvi_outreal_14_10d(PublicFactor):
    name = 'talib_rvi_outreal_14_10d'
    description = "源码核心递推表达式（完整分支/参数见链接）：wBeta = (double)(optInTimePeriod - 1) / (double)optInTimePeriod;；invPeriod = 1.0 / (double)optInStdDevPeriod;；today = anchorIdx + nbInitialElementNeeded;；for( j = anchorIdx; j < today; j += 1 )；periodTotal1 += tempReal;；tempReal *= tempReal;；periodTotal2 += tempReal;；barsSinceReseed = 32 * optInStdDevPeriod;；meanValue1 = periodTotal1 * invPeriod;；variance = periodTotal2 * invPeriod - meanValue1 * meanValue1;；trailingIdx += 1;；for( j = windowStart; j <= today; j += 1 )；tempReal += inReal[j];；shift = tempReal * invPeriod;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_RVI.c)；默认参数={'Time Period': 14.0, 'StdDev Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：RVI.outReal（Time Period=14, StdDev Period=10）；追踪：PF00841；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
