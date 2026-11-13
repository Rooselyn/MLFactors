"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyDoji_avgPeriod = 10; int ShadowVeryShort_avgPeriod = 10; BodyDojiPeriodTotal = 0; BodyDojiTrailingIdx = startIdx - BodyDoji_avgPeriod; ShadowVeryShortPeriodTotal = 0; ShadowVeryShortTrailingIdx = startIdx - ShadowVeryShort_avgPeriod; i = BodyDojiTrailingIdx; while( i < startIdx ) { BodyDojiPeriodTotal += TA_CANDLERANGE(BodyDoji,i); i += 1; } i = ShadowVeryShortTrailingIdx; while( i < startIdx ) { ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i); i += 1; } outIdx = 0; do { if( fabs(C[i] - O[i]) <= TA_CANDLEAVERAGE(BodyDoji,BodyDojiPeriodTotal,i) && (H[i] - ((C[i] >= O[i]) ? C[i] : O[i])) < TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i) && (((C[i] >= O[i]) ? O[i] : C[i]) - L[i]) > TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i) ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } BodyDojiPeriodTotal += TA_CANDLERANGE(BodyDoji,i) - TA_CANDLERANGE(BodyDoji,BodyDojiTrailingIdx); ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i) - TA_CANDLERANGE(ShadowVeryShort,ShadowVeryShortTrailingIdx); i += 1; BodyDojiTrailingIdx += 1; ShadowVeryShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLDRAGONFLYDOJI.outInteger（无窗口参数）；追踪：PF00689；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdldragonflydoji_11d', 'engine': 'talib', 'root_function': 'TA_CDLDRAGONFLYDOJI', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 10}

@register_factor
@fixed_factor('talib_cdldragonflydoji_11d', {})
class Factor_talib_cdldragonflydoji_11d(PublicFactor):
    name = 'talib_cdldragonflydoji_11d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyDoji_avgPeriod = 10; int ShadowVeryShort_avgPeriod = 10; BodyDojiPeriodTotal = 0; BodyDojiTrailingIdx = startIdx - BodyDoji_avgPeriod; ShadowVeryShortPeriodTotal = 0; ShadowVeryShortTrailingIdx = startIdx - ShadowVeryShort_avgPeriod; i = BodyDojiTrailingIdx; while( i < startIdx ) { BodyDojiPeriodTotal += TA_CANDLERANGE(BodyDoji,i); i += 1; } i = ShadowVeryShortTrailingIdx; while( i < startIdx ) { ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i); i += 1; } outIdx = 0; do { if( fabs(C[i] - O[i]) <= TA_CANDLEAVERAGE(BodyDoji,BodyDojiPeriodTotal,i) && (H[i] - ((C[i] >= O[i]) ? C[i] : O[i])) < TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i) && (((C[i] >= O[i]) ? O[i] : C[i]) - L[i]) > TA_CANDLEAVERAGE(ShadowVeryShort,ShadowVeryShortPeriodTotal,i) ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } BodyDojiPeriodTotal += TA_CANDLERANGE(BodyDoji,i) - TA_CANDLERANGE(BodyDoji,BodyDojiTrailingIdx); ShadowVeryShortPeriodTotal += TA_CANDLERANGE(ShadowVeryShort,i) - TA_CANDLERANGE(ShadowVeryShort,ShadowVeryShortTrailingIdx); i += 1; BodyDojiTrailingIdx += 1; ShadowVeryShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLDRAGONFLYDOJI.outInteger（无窗口参数）；追踪：PF00689；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
