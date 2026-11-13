"""TA-Lib（技术指标及K线形态）

公式：完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：cd = 0; patternResult = 0; i = startIdx - 3; while( i < startIdx ) { if( H[i - 1] < H[i - 2] && L[i - 1] > L[i - 2] && ((H[i] < H[i - 1] && L[i] < L[i - 1]) || (H[i] > H[i - 1] && L[i] > L[i - 1])) ) { patternResult = 100 * ((H[i] < H[i - 1]) ? 1 : -1); savedHigh = H[i - 1]; savedLow = L[i - 1]; cd = 4; } else if( cd > 0 && ((patternResult > 0 && C[i] > savedHigh) || (patternResult < 0 && C[i] < savedLow)) ) { cd = 0; } if( cd > 0 ) { cd -= 1; } i += 1; } i = startIdx; outIdx = 0; do { if( H[i - 1] < H[i - 2] && L[i - 1] > L[i - 2] && ((H[i] < H[i - 1] && L[i] < L[i - 1]) || (H[i] > H[i - 1] && L[i] > L[i - 1])) ) { patternResult = 100 * ((H[i] < H[i - 1]) ? 1 : -1); savedHigh = H[i - 1]; savedLow = L[i - 1]; cd = 4; outInteger[outIdx++] = patternResult; } else if( cd > 0 && ((patternResult > 0 && C[i] > savedHigh) || (patternResult < 0 && C[i] < savedLow)) ) { outInteger[outIdx++] = patternResult + 100 * ((patternResult > 0) ? 1 : -1); cd = 0; } else { outInteger[outIdx++] = 0; } if( cd > 0 ) { cd -= 1; } i += 1; } while( i <= endIdx );；；原目录：CDLHIKKAKE.outInteger（无窗口参数）；追踪：PF00700；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_cdlhikkake_6d', 'engine': 'talib', 'root_function': 'TA_CDLHIKKAKE', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'options': [], 'output_index': 0, 'warmup': 5}

@register_factor
@fixed_factor('talib_cdlhikkake_6d', {})
class Factor_talib_cdlhikkake_6d(PublicFactor):
    name = 'talib_cdlhikkake_6d'
    description = '完整逐日判定/状态递推（C语法用于明确逻辑；i为当日，非调用C库）：cd = 0; patternResult = 0; i = startIdx - 3; while( i < startIdx ) { if( H[i - 1] < H[i - 2] && L[i - 1] > L[i - 2] && ((H[i] < H[i - 1] && L[i] < L[i - 1]) || (H[i] > H[i - 1] && L[i] > L[i - 1])) ) { patternResult = 100 * ((H[i] < H[i - 1]) ? 1 : -1); savedHigh = H[i - 1]; savedLow = L[i - 1]; cd = 4; } else if( cd > 0 && ((patternResult > 0 && C[i] > savedHigh) || (patternResult < 0 && C[i] < savedLow)) ) { cd = 0; } if( cd > 0 ) { cd -= 1; } i += 1; } i = startIdx; outIdx = 0; do { if( H[i - 1] < H[i - 2] && L[i - 1] > L[i - 2] && ((H[i] < H[i - 1] && L[i] < L[i - 1]) || (H[i] > H[i - 1] && L[i] > L[i - 1])) ) { patternResult = 100 * ((H[i] < H[i - 1]) ? 1 : -1); savedHigh = H[i - 1]; savedLow = L[i - 1]; cd = 4; outInteger[outIdx++] = patternResult; } else if( cd > 0 && ((patternResult > 0 && C[i] > savedHigh) || (patternResult < 0 && C[i] < savedLow)) ) { outInteger[outIdx++] = patternResult + 100 * ((patternResult > 0) ? 1 : -1); cd = 0; } else { outInteger[outIdx++] = 0; } if( cd > 0 ) { cd -= 1; } i += 1; } while( i <= endIdx );；；原目录：CDLHIKKAKE.outInteger（无窗口参数）；追踪：PF00700；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
