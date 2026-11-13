"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：rad2Deg = 180.0 / (4.0 * atan(1));；tempReal = inReal[today++];；periodWMASub += tempReal;；periodWMASum += tempReal * 2.0;；periodWMASum += tempReal * 3.0;；periodWMASum += tempReal * 4.0;；trailingWMAValue = inReal[trailingWMAIdx++];；smoothedValue = periodWMASum * 0.1;；periodWMASub += todayValue;；periodWMASum += todayValue * 4.0;；hilbertTempReal = a * smoothedValue;；detrender += hilbertTempReal;；prev_detrender_Even = b * prev_detrender_input_Even;；detrender += prev_detrender_Even;；本行取输出outQuadrature。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HT_PHASOR.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：HT_PHASOR.outQuadrature（无窗口参数）；追踪：PF00773；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_ht_phasor_outquadrature_33d', 'root_function': 'TA_HT_PHASOR', 'required_inputs': ['inReal'], 'parameters': {}, 'options': [], 'outputs': ['outInPhase', 'outQuadrature'], 'output_index': 1, 'output_label': 'outQuadrature', 'warmup': 32, 'kernel': 'kernel_107dad32a430ce8d', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInPhase', 'double'], ['outQuadrature', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_ht_phasor_outquadrature_33d', {})
class Factor_talib_ht_phasor_outquadrature_33d(PublicFactor):
    name = 'talib_ht_phasor_outquadrature_33d'
    description = '源码核心递推表达式（完整分支/参数见链接）：rad2Deg = 180.0 / (4.0 * atan(1));；tempReal = inReal[today++];；periodWMASub += tempReal;；periodWMASum += tempReal * 2.0;；periodWMASum += tempReal * 3.0;；periodWMASum += tempReal * 4.0;；trailingWMAValue = inReal[trailingWMAIdx++];；smoothedValue = periodWMASum * 0.1;；periodWMASub += todayValue;；periodWMASum += todayValue * 4.0;；hilbertTempReal = a * smoothedValue;；detrender += hilbertTempReal;；prev_detrender_Even = b * prev_detrender_input_Even;；detrender += prev_detrender_Even;；本行取输出outQuadrature。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HT_PHASOR.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：HT_PHASOR.outQuadrature（无窗口参数）；追踪：PF00773；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
