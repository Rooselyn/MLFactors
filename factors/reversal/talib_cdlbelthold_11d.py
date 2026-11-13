"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyLong_avgPeriod = 10; int ShadowVeryShort_avgPeriod = 10; BodyLongPeriodTotal = 0; BodyLongTrailingIdx = startIdx - BodyLong_avgPeriod; ShadowVeryShortPeriodTotal = 0; ShadowVeryShortTrailingIdx = startIdx - ShadowVeryShort_avgPeriod; i = BodyLongTrailingIdx; while( i < startIdx ) { BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i); i += 1; } i = ShadowVeryShortTrailingIdx; while( i < startIdx ) { ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i); i += 1; } outIdx = 0; do { if( fabs(C[i] - O[i]) > TA_CANDLEAVERAGE(BodyLong,BodyLongPeriodTotal,i) && ((((C[i] >= O[i]) ? 1 : -1) == 1 && (((C[i] >= O[i]) ? O[i] : C[i]) - L[i]) < TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i)) || (((C[i] >= O[i]) ? 1 : -1) == -1 && (H[i] - ((C[i] >= O[i]) ? C[i] : O[i])) < TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i))) ) { outInteger[outIdx++] = ((C[i] >= O[i]) ? 1 : -1) * 100; } else { outInteger[outIdx++] = 0; } BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i) - TA_CANDLERANGE(BodyLong,BodyLongTrailingIdx); ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i) - TA_CANDLERANGE(ShadowVeryShort,ShadowVeryShortTrailingIdx); i += 1; BodyLongTrailingIdx += 1; ShadowVeryShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLBELTHOLD.outInteger（无窗口参数）；追踪：PF00681；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdlbelthold_11d', 'engine': 'talib', 'root_function': 'TA_CDLBELTHOLD', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 10}

@register_factor
@fixed_factor('talib_cdlbelthold_11d', {})
class Factor_talib_cdlbelthold_11d(PublicFactor):
    name = 'talib_cdlbelthold_11d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyLong_avgPeriod = 10; int ShadowVeryShort_avgPeriod = 10; BodyLongPeriodTotal = 0; BodyLongTrailingIdx = startIdx - BodyLong_avgPeriod; ShadowVeryShortPeriodTotal = 0; ShadowVeryShortTrailingIdx = startIdx - ShadowVeryShort_avgPeriod; i = BodyLongTrailingIdx; while( i < startIdx ) { BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i); i += 1; } i = ShadowVeryShortTrailingIdx; while( i < startIdx ) { ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i); i += 1; } outIdx = 0; do { if( fabs(C[i] - O[i]) > TA_CANDLEAVERAGE(BodyLong,BodyLongPeriodTotal,i) && ((((C[i] >= O[i]) ? 1 : -1) == 1 && (((C[i] >= O[i]) ? O[i] : C[i]) - L[i]) < TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i)) || (((C[i] >= O[i]) ? 1 : -1) == -1 && (H[i] - ((C[i] >= O[i]) ? C[i] : O[i])) < TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i))) ) { outInteger[outIdx++] = ((C[i] >= O[i]) ? 1 : -1) * 100; } else { outInteger[outIdx++] = 0; } BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i) - TA_CANDLERANGE(BodyLong,BodyLongTrailingIdx); ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i) - TA_CANDLERANGE(ShadowVeryShort,ShadowVeryShortTrailingIdx); i += 1; BodyLongTrailingIdx += 1; ShadowVeryShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLBELTHOLD.outInteger（无窗口参数）；追踪：PF00681；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
