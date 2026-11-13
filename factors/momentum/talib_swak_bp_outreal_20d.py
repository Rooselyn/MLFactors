"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：count4 = (int)ceil((double)(11 * optInTimePeriod) / (6.0 * optInDelta));；count8 = (int)ceil((double)(20 * optInTimePeriod) / (6.0 * optInDelta));；w = 2.0 * 3.141592653589793 / (double)optInTimePeriod;；t = 4.0 * 3.141592653589793 * optInDelta / (double)optInTimePeriod;；abp = (1.0 - sin(t)) / cos(t);；c0 = (1.0 - abp) / 2.0;；a1 = beta * (1.0 + abp);；y = fma(a1, y1, fma(a2, y2, c0 * (x0 - x2)));；today += 1;；outIdx = outIdx + 1;；y = fma(sp->a1, sp->y1, fma(sp->a2, sp->y2, sp->c0 * (x0 - sp->x2)));；sp->cur_outReal = *outReal;；sp = (struct TA_SWAK_BP_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SWAK_BP.c)；默认参数={'Time Period': 20.0, 'Delta': 0.1}；完整数值核及辅助调用在实现附录展开。；原目录：SWAK_BP.outReal（Time Period=20, Delta=1.000000e-1）；追踪：PF00860；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_swak_bp_outreal_20d', 'root_function': 'TA_SWAK_BP', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 20.0, 'Delta': 0.1}, 'options': [20.0, 0.1], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_903d8953f5ccc8f8', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInDelta', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_swak_bp_outreal_20d', {})
class Factor_talib_swak_bp_outreal_20d(PublicFactor):
    name = 'talib_swak_bp_outreal_20d'
    description = "源码核心递推表达式（完整分支/参数见链接）：count4 = (int)ceil((double)(11 * optInTimePeriod) / (6.0 * optInDelta));；count8 = (int)ceil((double)(20 * optInTimePeriod) / (6.0 * optInDelta));；w = 2.0 * 3.141592653589793 / (double)optInTimePeriod;；t = 4.0 * 3.141592653589793 * optInDelta / (double)optInTimePeriod;；abp = (1.0 - sin(t)) / cos(t);；c0 = (1.0 - abp) / 2.0;；a1 = beta * (1.0 + abp);；y = fma(a1, y1, fma(a2, y2, c0 * (x0 - x2)));；today += 1;；outIdx = outIdx + 1;；y = fma(sp->a1, sp->y1, fma(sp->a2, sp->y2, sp->c0 * (x0 - sp->x2)));；sp->cur_outReal = *outReal;；sp = (struct TA_SWAK_BP_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SWAK_BP.c)；默认参数={'Time Period': 20.0, 'Delta': 0.1}；完整数值核及辅助调用在实现附录展开。；原目录：SWAK_BP.outReal（Time Period=20, Delta=1.000000e-1）；追踪：PF00860；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
