"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：count4 = (int)ceil(20.0 / limit);；count8 = (int)ceil(38.0 / limit);；rad2Deg = 180.0 / (4.0 * atan(1));；tempReal = inReal[today++];；periodWMASub += tempReal;；periodWMASum += tempReal * 2.0;；periodWMASum += tempReal * 3.0;；periodWMASum += tempReal * 4.0;；trailingWMAValue = inReal[trailingWMAIdx++];；smoothedValue = periodWMASum * 0.1;；periodWMASub += todayValue;；periodWMASum += todayValue * 4.0;；hilbertTempReal = a * smoothedValue;；detrender += hilbertTempReal;；本行取输出outFAMA。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MAMA.c)；默认参数={'Fast Limit': 0.5, 'Slow Limit': 0.05}；完整数值核及辅助调用在实现附录展开。；原目录：MAMA.outFAMA（Fast Limit=5.000000e-1, Slow Limit=5.000000e-2）；追踪：PF00807；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_mama_outfama_33d', 'root_function': 'TA_MAMA', 'required_inputs': ['inReal'], 'parameters': {'Fast Limit': 0.5, 'Slow Limit': 0.05}, 'options': [0.5, 0.05], 'outputs': ['outMAMA', 'outFAMA'], 'output_index': 1, 'output_label': 'outFAMA', 'warmup': 32, 'kernel': 'kernel_9bc25d95d041ea47', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInFastLimit', 'double'], ['optInSlowLimit', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outMAMA', 'double'], ['outFAMA', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_mama_outfama_33d', {})
class Factor_talib_mama_outfama_33d(PublicFactor):
    name = 'talib_mama_outfama_33d'
    description = "源码核心递推表达式（完整分支/参数见链接）：count4 = (int)ceil(20.0 / limit);；count8 = (int)ceil(38.0 / limit);；rad2Deg = 180.0 / (4.0 * atan(1));；tempReal = inReal[today++];；periodWMASub += tempReal;；periodWMASum += tempReal * 2.0;；periodWMASum += tempReal * 3.0;；periodWMASum += tempReal * 4.0;；trailingWMAValue = inReal[trailingWMAIdx++];；smoothedValue = periodWMASum * 0.1;；periodWMASub += todayValue;；periodWMASum += todayValue * 4.0;；hilbertTempReal = a * smoothedValue;；detrender += hilbertTempReal;；本行取输出outFAMA。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MAMA.c)；默认参数={'Fast Limit': 0.5, 'Slow Limit': 0.05}；完整数值核及辅助调用在实现附录展开。；原目录：MAMA.outFAMA（Fast Limit=5.000000e-1, Slow Limit=5.000000e-2）；追踪：PF00807；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
