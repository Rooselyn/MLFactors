"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：h = 3.141592653589793 / (double)optInTimePeriod;；a1p = 2.0 * sh * (ch - sh) / (1.0 - 2.0 * sh * sh);；c0 = 1.0 - a1p / 2.0;；y = fma(a1, y1, c0 * (x0 - x1));；today += 1;；outIdx = outIdx + 1;；y = fma(sp->a1, sp->y1, sp->c0 * (x0 - sp->x1));；sp->cur_outReal = *outReal;；sp = (struct TA_SWAK_HP_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；const struct TA_SWAK_HP_Stream *sp = stream;；y = fma(sp->a1, y1, sp->c0 * (x0 - x1));；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SWAK_HP.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：SWAK_HP.outReal（Time Period=20）；追踪：PF00863；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_swak_hp_outreal_20d', 'root_function': 'TA_SWAK_HP', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 20.0}, 'options': [20.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_6e71e7e8d531211c', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_swak_hp_outreal_20d', {})
class Factor_talib_swak_hp_outreal_20d(PublicFactor):
    name = 'talib_swak_hp_outreal_20d'
    description = "源码核心递推表达式（完整分支/参数见链接）：h = 3.141592653589793 / (double)optInTimePeriod;；a1p = 2.0 * sh * (ch - sh) / (1.0 - 2.0 * sh * sh);；c0 = 1.0 - a1p / 2.0;；y = fma(a1, y1, c0 * (x0 - x1));；today += 1;；outIdx = outIdx + 1;；y = fma(sp->a1, sp->y1, sp->c0 * (x0 - sp->x1));；sp->cur_outReal = *outReal;；sp = (struct TA_SWAK_HP_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；sp->outRangeCount = *outNBElement;；sp->cur_outReal = outReal[(*outNBElement - 1) * outStride];；const struct TA_SWAK_HP_Stream *sp = stream;；y = fma(sp->a1, y1, sp->c0 * (x0 - x1));；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SWAK_HP.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：SWAK_HP.outReal（Time Period=20）；追踪：PF00863；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
