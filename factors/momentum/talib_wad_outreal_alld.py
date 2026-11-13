"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：for( i = startIdx; i <= endIdx; i += 1 )；sum += close - trueExtreme;；outIdx = outIdx + 1;；sp->sum += close - trueExtreme;；sp->cur_outReal = *outReal;；sp = (struct TA_WAD_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；const struct TA_WAD_Stream *sp = stream;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_WAD.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：WAD.outReal（无窗口参数）；追踪：PF00880；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:wad（原函数默认参数/显式周期）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_wad_outreal_alld', 'root_function': 'TA_WAD', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {}, 'options': [], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_c5bb3a078fd6cffb', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_wad_outreal_alld', {})
class Factor_talib_wad_outreal_alld(PublicFactor):
    name = 'talib_wad_outreal_alld'
    description = '源码核心递推表达式（完整分支/参数见链接）：for( i = startIdx; i <= endIdx; i += 1 )；sum += close - trueExtreme;；outIdx = outIdx + 1;；sp->sum += close - trueExtreme;；sp->cur_outReal = *outReal;；sp = (struct TA_WAD_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；const struct TA_WAD_Stream *sp = stream;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_WAD.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：WAD.outReal（无窗口参数）；追踪：PF00880；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:wad（原函数默认参数/显式周期）'
    INPUTS = INPUTS
    SPEC = SPEC
