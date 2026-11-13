"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：for( i = startIdx; i <= endIdx; i += 1 )；n += 0.5 * body;；n += 0.25 * prevBody;；r = max(up - 0.5 * dn,dn - 0.5 * up);；r += 0.25 * fabs(prevBody);；swing = 50.0 * (n / r) * (k / optInLimitMove);；outIdx += 1;；n += 0.25 * sp->prevBody;；r += 0.25 * fabs(sp->prevBody);；swing = 50.0 * (n / r) * (k / sp->optInLimitMove);；sp->cur_outReal = *outReal;；sp = (struct TA_SI_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SI.c)；默认参数={'Limit Move': 3.0}；完整数值核及辅助调用在实现附录展开。；原目录：SI.outReal（Limit Move=3.000000e+0）；追踪：PF00846；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_si_outreal_2d', 'root_function': 'TA_SI', 'required_inputs': ['inOpen', 'inHigh', 'inLow', 'inClose'], 'parameters': {'Limit Move': 3.0}, 'options': [3.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 1, 'kernel': 'kernel_c0601cc188d9887c', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInLimitMove', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_si_outreal_2d', {})
class Factor_talib_si_outreal_2d(PublicFactor):
    name = 'talib_si_outreal_2d'
    description = "源码核心递推表达式（完整分支/参数见链接）：for( i = startIdx; i <= endIdx; i += 1 )；n += 0.5 * body;；n += 0.25 * prevBody;；r = max(up - 0.5 * dn,dn - 0.5 * up);；r += 0.25 * fabs(prevBody);；swing = 50.0 * (n / r) * (k / optInLimitMove);；outIdx += 1;；n += 0.25 * sp->prevBody;；r += 0.25 * fabs(sp->prevBody);；swing = 50.0 * (n / r) * (k / sp->optInLimitMove);；sp->cur_outReal = *outReal;；sp = (struct TA_SI_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SI.c)；默认参数={'Limit Move': 3.0}；完整数值核及辅助调用在实现附录展开。；原目录：SI.outReal（Limit Move=3.000000e+0）；追踪：PF00846；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
