"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyDoji_avgPeriod = 10; BodyPeriodTotal = 0; BodyTrailingIdx = startIdx - 2 - BodyDoji_avgPeriod; i = BodyTrailingIdx; while( i < startIdx - 2 ) { BodyPeriodTotal += TA_CANDLERANGE(BodyDoji,i); i += 1; } i = startIdx; outIdx = 0; do { if( fabs(C[i - 2] - O[i - 2]) <= TA_CANDLEAVERAGE(BodyDoji,BodyPeriodTotal,i - 2) && fabs(C[i - 1] - O[i - 1]) <= TA_CANDLEAVERAGE(BodyDoji,BodyPeriodTotal,i - 2) && fabs(C[i] - O[i]) <= TA_CANDLEAVERAGE(BodyDoji,BodyPeriodTotal,i - 2) ) { outInteger[outIdx] = 0; if( ((min(O[i - 1],C[i - 1]) > max(O[i - 2],C[i - 2])) ? 1 : 0) && max(O[i],C[i]) < max(O[i - 1],C[i - 1]) ) { outInteger[outIdx] = -100; } if( ((max(O[i - 1],C[i - 1]) < min(O[i - 2],C[i - 2])) ? 1 : 0) && min(O[i],C[i]) > min(O[i - 1],C[i - 1]) ) { outInteger[outIdx] = 100; } outIdx += 1; } else { outInteger[outIdx++] = 0; } BodyPeriodTotal += TA_CANDLERANGE(BodyDoji,i - 2) - TA_CANDLERANGE(BodyDoji,BodyTrailingIdx); i += 1; BodyTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLTRISTAR.outInteger（无窗口参数）；追踪：PF00729；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdltristar_13d', 'engine': 'talib', 'root_function': 'TA_CDLTRISTAR', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 12}

@register_factor
@fixed_factor('talib_cdltristar_13d', {})
class Factor_talib_cdltristar_13d(PublicFactor):
    name = 'talib_cdltristar_13d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int BodyDoji_avgPeriod = 10; BodyPeriodTotal = 0; BodyTrailingIdx = startIdx - 2 - BodyDoji_avgPeriod; i = BodyTrailingIdx; while( i < startIdx - 2 ) { BodyPeriodTotal += TA_CANDLERANGE(BodyDoji,i); i += 1; } i = startIdx; outIdx = 0; do { if( fabs(C[i - 2] - O[i - 2]) <= TA_CANDLEAVERAGE(BodyDoji,BodyPeriodTotal,i - 2) && fabs(C[i - 1] - O[i - 1]) <= TA_CANDLEAVERAGE(BodyDoji,BodyPeriodTotal,i - 2) && fabs(C[i] - O[i]) <= TA_CANDLEAVERAGE(BodyDoji,BodyPeriodTotal,i - 2) ) { outInteger[outIdx] = 0; if( ((min(O[i - 1],C[i - 1]) > max(O[i - 2],C[i - 2])) ? 1 : 0) && max(O[i],C[i]) < max(O[i - 1],C[i - 1]) ) { outInteger[outIdx] = -100; } if( ((max(O[i - 1],C[i - 1]) < min(O[i - 2],C[i - 2])) ? 1 : 0) && min(O[i],C[i]) > min(O[i - 1],C[i - 1]) ) { outInteger[outIdx] = 100; } outIdx += 1; } else { outInteger[outIdx++] = 0; } BodyPeriodTotal += TA_CANDLERANGE(BodyDoji,i - 2) - TA_CANDLERANGE(BodyDoji,BodyTrailingIdx); i += 1; BodyTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLTRISTAR.outInteger（无窗口参数）；追踪：PF00729；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
