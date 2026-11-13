"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int Near_avgPeriod = 5; NearPeriodTotal[3] = 0; NearPeriodTotal[2] = 0; NearTrailingIdx = startIdx - Near_avgPeriod; i = NearTrailingIdx; while( i < startIdx ) { NearPeriodTotal[3] = NearPeriodTotal[3] + TA_CANDLERANGE(Near,i - 3); NearPeriodTotal[2] = NearPeriodTotal[2] + TA_CANDLERANGE(Near,i - 2); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 3] >= O[i - 3]) ? 1 : -1) == ((C[i - 2] >= O[i - 2]) ? 1 : -1) && ((C[i - 2] >= O[i - 2]) ? 1 : -1) == ((C[i - 1] >= O[i - 1]) ? 1 : -1) && ((C[i] >= O[i]) ? 1 : -1) == -((C[i - 1] >= O[i - 1]) ? 1 : -1) && O[i - 2] >= min(O[i - 3],C[i - 3]) - TA_CANDLEAVERAGE(Near,NearPeriodTotal[3],i - 3) && O[i - 2] <= max(O[i - 3],C[i - 3]) + TA_CANDLEAVERAGE(Near,NearPeriodTotal[3],i - 3) && O[i - 1] >= min(O[i - 2],C[i - 2]) - TA_CANDLEAVERAGE(Near,NearPeriodTotal[2],i - 2) && O[i - 1] <= max(O[i - 2],C[i - 2]) + TA_CANDLEAVERAGE(Near,NearPeriodTotal[2],i - 2) && ((((C[i - 1] >= O[i - 1]) ? 1 : -1) == 1 && C[i - 1] > C[i - 2] && C[i - 2] > C[i - 3] && O[i] > C[i - 1] && C[i] < O[i - 3]) || (((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && C[i - 1] < C[i - 2] && C[i - 2] < C[i - 3] && O[i] < C[i - 1] && C[i] > O[i - 3])) ) { outInteger[outIdx++] = ((C[i - 1] >= O[i - 1]) ? 1 : -1) * 100; } else { outInteger[outIdx++] = 0; } for( totIdx = 3; totIdx >= 2; totIdx -= 1 ) { NearPeriodTotal[totIdx] = NearPeriodTotal[totIdx] + (TA_CANDLERANGE(Near,i - totIdx) - TA_CANDLERANGE(Near,NearTrailingIdx - totIdx)); } i += 1; NearTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDL3LINESTRIKE.outInteger（无窗口参数）；追踪：PF00675；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdl3linestrike_9d', 'engine': 'talib', 'root_function': 'TA_CDL3LINESTRIKE', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 8}

@register_factor
@fixed_factor('talib_cdl3linestrike_9d', {})
class Factor_talib_cdl3linestrike_9d(PublicFactor):
    name = 'talib_cdl3linestrike_9d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：int Near_avgPeriod = 5; NearPeriodTotal[3] = 0; NearPeriodTotal[2] = 0; NearTrailingIdx = startIdx - Near_avgPeriod; i = NearTrailingIdx; while( i < startIdx ) { NearPeriodTotal[3] = NearPeriodTotal[3] + TA_CANDLERANGE(Near,i - 3); NearPeriodTotal[2] = NearPeriodTotal[2] + TA_CANDLERANGE(Near,i - 2); i += 1; } i = startIdx; outIdx = 0; do { if( ((C[i - 3] >= O[i - 3]) ? 1 : -1) == ((C[i - 2] >= O[i - 2]) ? 1 : -1) && ((C[i - 2] >= O[i - 2]) ? 1 : -1) == ((C[i - 1] >= O[i - 1]) ? 1 : -1) && ((C[i] >= O[i]) ? 1 : -1) == -((C[i - 1] >= O[i - 1]) ? 1 : -1) && O[i - 2] >= min(O[i - 3],C[i - 3]) - TA_CANDLEAVERAGE(Near,NearPeriodTotal[3],i - 3) && O[i - 2] <= max(O[i - 3],C[i - 3]) + TA_CANDLEAVERAGE(Near,NearPeriodTotal[3],i - 3) && O[i - 1] >= min(O[i - 2],C[i - 2]) - TA_CANDLEAVERAGE(Near,NearPeriodTotal[2],i - 2) && O[i - 1] <= max(O[i - 2],C[i - 2]) + TA_CANDLEAVERAGE(Near,NearPeriodTotal[2],i - 2) && ((((C[i - 1] >= O[i - 1]) ? 1 : -1) == 1 && C[i - 1] > C[i - 2] && C[i - 2] > C[i - 3] && O[i] > C[i - 1] && C[i] < O[i - 3]) || (((C[i - 1] >= O[i - 1]) ? 1 : -1) == -1 && C[i - 1] < C[i - 2] && C[i - 2] < C[i - 3] && O[i] < C[i - 1] && C[i] > O[i - 3])) ) { outInteger[outIdx++] = ((C[i - 1] >= O[i - 1]) ? 1 : -1) * 100; } else { outInteger[outIdx++] = 0; } for( totIdx = 3; totIdx >= 2; totIdx -= 1 ) { NearPeriodTotal[totIdx] = NearPeriodTotal[totIdx] + (TA_CANDLERANGE(Near,i - totIdx) - TA_CANDLERANGE(Near,NearTrailingIdx - totIdx)); } i += 1; NearTrailingIdx += 1; } while( i <= endIdx );；；原目录：CDL3LINESTRIKE.outInteger（无窗口参数）；追踪：PF00675；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
