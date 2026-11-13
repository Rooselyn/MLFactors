"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int Equal_avgPeriod = 5; int Near_avgPeriod = 5; NearPeriodTotal = 0; EqualPeriodTotal = 0; NearTrailingIdx = startIdx - Near_avgPeriod; EqualTrailingIdx = startIdx - Equal_avgPeriod; i = NearTrailingIdx; while( i < startIdx ) { NearPeriodTotal += TA_CANDLERANGE(Near,i - 1); i += 1; } i = EqualTrailingIdx; while( i < startIdx ) { EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1); i += 1; } i = startIdx; outIdx = 0; do { if( ((((min(O[i - 1],C[i - 1]) > max(O[i - 2],C[i - 2])) ? 1 : 0) && ((min(O[i],C[i]) > max(O[i - 2],C[i - 2])) ? 1 : 0)) || (((max(O[i - 1],C[i - 1]) < min(O[i - 2],C[i - 2])) ? 1 : 0) && ((max(O[i],C[i]) < min(O[i - 2],C[i - 2])) ? 1 : 0))) && ((C[i - 1] >= O[i - 1]) ? 1 : -1) == 1 && ((C[i] >= O[i]) ? 1 : -1) == 1 && fabs(C[i] - O[i]) >= fabs(C[i - 1] - O[i - 1]) - TA_CANDLEAVERAGE(Near,NearPeriodTotal,i - 1) && fabs(C[i] - O[i]) <= fabs(C[i - 1] - O[i - 1]) + TA_CANDLEAVERAGE(Near,NearPeriodTotal,i - 1) && O[i] >= O[i - 1] - TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) && O[i] <= O[i - 1] + TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) ) { outInteger[outIdx++] = ((min(O[i - 1],C[i - 1]) > max(O[i - 2],C[i - 2])) ? 1 : 0) ? 100 : -100; } else { outInteger[outIdx++] = 0; } NearPeriodTotal += TA_CANDLERANGE(Near,i - 1) - TA_CANDLERANGE(Near,NearTrailingIdx - 1); EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1) - TA_CANDLERANGE(Equal,EqualTrailingIdx - 1); i += 1; NearTrailingIdx += 1; EqualTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLGAPSIDESIDEWHITE.outInteger（无窗口参数）；追踪：PF00693；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdlgapsidesidewhite_8d', 'engine': 'talib', 'root_function': 'TA_CDLGAPSIDESIDEWHITE', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 7}

@register_factor
@fixed_factor('talib_cdlgapsidesidewhite_8d', {})
class Factor_talib_cdlgapsidesidewhite_8d(PublicFactor):
    name = 'talib_cdlgapsidesidewhite_8d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int Equal_avgPeriod = 5; int Near_avgPeriod = 5; NearPeriodTotal = 0; EqualPeriodTotal = 0; NearTrailingIdx = startIdx - Near_avgPeriod; EqualTrailingIdx = startIdx - Equal_avgPeriod; i = NearTrailingIdx; while( i < startIdx ) { NearPeriodTotal += TA_CANDLERANGE(Near,i - 1); i += 1; } i = EqualTrailingIdx; while( i < startIdx ) { EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1); i += 1; } i = startIdx; outIdx = 0; do { if( ((((min(O[i - 1],C[i - 1]) > max(O[i - 2],C[i - 2])) ? 1 : 0) && ((min(O[i],C[i]) > max(O[i - 2],C[i - 2])) ? 1 : 0)) || (((max(O[i - 1],C[i - 1]) < min(O[i - 2],C[i - 2])) ? 1 : 0) && ((max(O[i],C[i]) < min(O[i - 2],C[i - 2])) ? 1 : 0))) && ((C[i - 1] >= O[i - 1]) ? 1 : -1) == 1 && ((C[i] >= O[i]) ? 1 : -1) == 1 && fabs(C[i] - O[i]) >= fabs(C[i - 1] - O[i - 1]) - TA_CANDLEAVERAGE(Near,NearPeriodTotal,i - 1) && fabs(C[i] - O[i]) <= fabs(C[i - 1] - O[i - 1]) + TA_CANDLEAVERAGE(Near,NearPeriodTotal,i - 1) && O[i] >= O[i - 1] - TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) && O[i] <= O[i - 1] + TA_CANDLEAVERAGE(Equal,EqualPeriodTotal,i - 1) ) { outInteger[outIdx++] = ((min(O[i - 1],C[i - 1]) > max(O[i - 2],C[i - 2])) ? 1 : 0) ? 100 : -100; } else { outInteger[outIdx++] = 0; } NearPeriodTotal += TA_CANDLERANGE(Near,i - 1) - TA_CANDLERANGE(Near,NearTrailingIdx - 1); EqualPeriodTotal += TA_CANDLERANGE(Equal,i - 1) - TA_CANDLERANGE(Equal,EqualTrailingIdx - 1); i += 1; NearTrailingIdx += 1; EqualTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDLGAPSIDESIDEWHITE.outInteger（无窗口参数）；追踪：PF00693；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
