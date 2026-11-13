"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyLong_avgPeriod = 10; int BodyShort_avgPeriod = 10; BodyLongPeriodTotal = 0; BodyShortPeriodTotal = 0; BodyLongTrailingIdx = startIdx - BodyLong_avgPeriod; BodyShortTrailingIdx = startIdx - BodyShort_avgPeriod; i = BodyLongTrailingIdx; while( i < startIdx ) { BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i - 1); i += 1; } i = BodyShortTrailingIdx; while( i < startIdx ) { BodyShortPeriodTotal += TA_CANDLERANGE(BodyShort,i); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && ((C[i] >= O[i]) ? 1 : -1) == -1 && fabs(C[i - 1] - O[i - 1]) > TA_CANDLEAVERAGE(BodyLong,BodyLongPeriodTotal,i - 1) && fabs(C[i] - O[i]) <= TA_CANDLEAVERAGE(BodyShort,BodyShortPeriodTotal,i) && O[i] < O[i - 1] && C[i] > C[i - 1] ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i - 1) - TA_CANDLERANGE(BodyLong,BodyLongTrailingIdx - 1); BodyShortPeriodTotal += TA_CANDLERANGE(BodyShort,i) - TA_CANDLERANGE(BodyShort,BodyShortTrailingIdx); i += 1; BodyLongTrailingIdx += 1; BodyShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLHOMINGPIGEON.outInteger（无窗口参数）；追踪：PF00702；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdlhomingpigeon_12d', 'engine': 'talib', 'root_function': 'TA_CDLHOMINGPIGEON', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 11}

@register_factor
@fixed_factor('talib_cdlhomingpigeon_12d', {})
class Factor_talib_cdlhomingpigeon_12d(PublicFactor):
    name = 'talib_cdlhomingpigeon_12d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyLong_avgPeriod = 10; int BodyShort_avgPeriod = 10; BodyLongPeriodTotal = 0; BodyShortPeriodTotal = 0; BodyLongTrailingIdx = startIdx - BodyLong_avgPeriod; BodyShortTrailingIdx = startIdx - BodyShort_avgPeriod; i = BodyLongTrailingIdx; while( i < startIdx ) { BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i - 1); i += 1; } i = BodyShortTrailingIdx; while( i < startIdx ) { BodyShortPeriodTotal += TA_CANDLERANGE(BodyShort,i); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && ((C[i] >= O[i]) ? 1 : -1) == -1 && fabs(C[i - 1] - O[i - 1]) > TA_CANDLEAVERAGE(BodyLong,BodyLongPeriodTotal,i - 1) && fabs(C[i] - O[i]) <= TA_CANDLEAVERAGE(BodyShort,BodyShortPeriodTotal,i) && O[i] < O[i - 1] && C[i] > C[i - 1] ) { outInteger[outIdx++] = 100; } else { outInteger[outIdx++] = 0; } BodyLongPeriodTotal += TA_CANDLERANGE(BodyLong,i - 1) - TA_CANDLERANGE(BodyLong,BodyLongTrailingIdx - 1); BodyShortPeriodTotal += TA_CANDLERANGE(BodyShort,i) - TA_CANDLERANGE(BodyShort,BodyShortTrailingIdx); i += 1; BodyLongTrailingIdx += 1; BodyShortTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLHOMINGPIGEON.outInteger（无窗口参数）；追踪：PF00702；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
