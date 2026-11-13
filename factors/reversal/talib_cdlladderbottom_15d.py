"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int ShadowVeryShort_avgPeriod = 10; ShadowVeryShortPeriodTotal = 0; ShadowVeryShortTrailingIdx = startIdx - ShadowVeryShort_avgPeriod; i = ShadowVeryShortTrailingIdx; while( i < startIdx ) { ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i - 1); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 4] >= O[i - 4]) ? 1 : -1) == -1 && ((C[i - 3] >= O[i - 3]) ? 1 : -1) == -1 && ((C[i - 2] >= O[i - 2]) ? 1 : -1) == -1 && O[i - 4] > O[i - 3] && O[i - 3] > O[i - 2] && C[i - 4] > C[i - 3] && C[i - 3] > C[i - 2] && ((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && (H[i - 1] - ((C[i - 1] >= O[i - 1]) ? C[i - 1] : O[i - 1])) > TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i - 1) && ((C[i] >= O[i]) ? 1 : -1) == 1 && O[i] > O[i - 1] && C[i] > H[i - 1] ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i - 1) - TA_CANDLERANGE(ShadowVeryShort,ShadowVeryShortTrailingIdx - 1); i += 1; ShadowVeryShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLLADDERBOTTOM.outInteger（无窗口参数）；追踪：PF00708；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdlladderbottom_15d', 'engine': 'talib', 'root_function': 'TA_CDLLADDERBOTTOM', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 14}

@register_factor
@fixed_factor('talib_cdlladderbottom_15d', {})
class Factor_talib_cdlladderbottom_15d(PublicFactor):
    name = 'talib_cdlladderbottom_15d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int ShadowVeryShort_avgPeriod = 10; ShadowVeryShortPeriodTotal = 0; ShadowVeryShortTrailingIdx = startIdx - ShadowVeryShort_avgPeriod; i = ShadowVeryShortTrailingIdx; while( i < startIdx ) { ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i - 1); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 4] >= O[i - 4]) ? 1 : -1) == -1 && ((C[i - 3] >= O[i - 3]) ? 1 : -1) == -1 && ((C[i - 2] >= O[i - 2]) ? 1 : -1) == -1 && O[i - 4] > O[i - 3] && O[i - 3] > O[i - 2] && C[i - 4] > C[i - 3] && C[i - 3] > C[i - 2] && ((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && (H[i - 1] - ((C[i - 1] >= O[i - 1]) ? C[i - 1] : O[i - 1])) > TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i - 1) && ((C[i] >= O[i]) ? 1 : -1) == 1 && O[i] > O[i - 1] && C[i] > H[i - 1] ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i - 1) - TA_CANDLERANGE(ShadowVeryShort,ShadowVeryShortTrailingIdx - 1); i += 1; ShadowVeryShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLLADDERBOTTOM.outInteger（无窗口参数）；追踪：PF00708；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
