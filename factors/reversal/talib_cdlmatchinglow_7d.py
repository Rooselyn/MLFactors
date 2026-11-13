"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int Equal_avgPeriod = 5; EqualPeriodTotal = 0; EqualTrailingIdx = startIdx - Equal_avgPeriod; i = EqualTrailingIdx; while( i < startIdx ) { EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && ((C[i] >= O[i]) ? 1 : -1) == -1 && C[i] <= C[i - 1] + TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) && C[i] >= C[i - 1] - TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1) - TA_CANDLERANGE(Equal,EqualTrailingIdx - 1); i += 1; EqualTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLMATCHINGLOW.outInteger（无窗口参数）；追踪：PF00712；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdlmatchinglow_7d', 'engine': 'talib', 'root_function': 'TA_CDLMATCHINGLOW', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 6}

@register_factor
@fixed_factor('talib_cdlmatchinglow_7d', {})
class Factor_talib_cdlmatchinglow_7d(PublicFactor):
    name = 'talib_cdlmatchinglow_7d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int Equal_avgPeriod = 5; EqualPeriodTotal = 0; EqualTrailingIdx = startIdx - Equal_avgPeriod; i = EqualTrailingIdx; while( i < startIdx ) { EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && ((C[i] >= O[i]) ? 1 : -1) == -1 && C[i] <= C[i - 1] + TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) && C[i] >= C[i - 1] - TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1) - TA_CANDLERANGE(Equal,EqualTrailingIdx - 1); i += 1; EqualTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLMATCHINGLOW.outInteger（无窗口参数）；追踪：PF00712；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
