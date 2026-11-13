"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：s = sin(3.141592653589793 / (double)optInTimePeriod);；b2p = 2.415 * (2.0 * s * s);；a2p = -b2p + sqrt(fma(b2p, b2p, 2.0 * b2p));；c0 = a2p * a2p;；a1 = 2.0 * om;；a2 = -(om * om);；y = fma(a1, y1, fma(a2, y2, c0 * inReal[today]));；today += 1;；outIdx = outIdx + 1;；y = fma(a1, y1, fma(a2, y2, c0 * (double)inReal[today]));；y = fma(sp->a1, sp->y1, fma(sp->a2, sp->y2, sp->c0 * inReal));；sp->cur_outReal = *outReal;；sp = (struct TA_SWAK_GAUSS_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SWAK_GAUSS.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：SWAK_GAUSS.outReal（Time Period=20）；追踪：PF00862；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_swak_gauss_outreal_20d', 'root_function': 'TA_SWAK_GAUSS', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 20.0}, 'options': [20.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_474bf1d84d36b22a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_swak_gauss_outreal_20d', {})
class Factor_talib_swak_gauss_outreal_20d(PublicFactor):
    name = 'talib_swak_gauss_outreal_20d'
    description = "源码核心递推表达式（完整分支/参数见链接）：s = sin(3.141592653589793 / (double)optInTimePeriod);；b2p = 2.415 * (2.0 * s * s);；a2p = -b2p + sqrt(fma(b2p, b2p, 2.0 * b2p));；c0 = a2p * a2p;；a1 = 2.0 * om;；a2 = -(om * om);；y = fma(a1, y1, fma(a2, y2, c0 * inReal[today]));；today += 1;；outIdx = outIdx + 1;；y = fma(a1, y1, fma(a2, y2, c0 * (double)inReal[today]));；y = fma(sp->a1, sp->y1, fma(sp->a2, sp->y2, sp->c0 * inReal));；sp->cur_outReal = *outReal;；sp = (struct TA_SWAK_GAUSS_Stream *)TA_Malloc( sizeof(*sp) );；sp->outRangeBegIdx = *outBegIdx;；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SWAK_GAUSS.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：SWAK_GAUSS.outReal（Time Period=20）；追踪：PF00862；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
