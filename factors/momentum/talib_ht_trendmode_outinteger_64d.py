"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：double *smoothPrice = &local_smoothPrice[0];；maxIdx_smoothPrice = (int)(sizeof(local_smoothPrice)/sizeof(double))-1;；tempReal = atan(1);；rad2Deg = 45.0 / tempReal;；deg2Rad = 1.0 / rad2Deg;；constDeg2RadBy360 = tempReal * 8.0;；tempReal = inReal[today++];；periodWMASub += tempReal;；periodWMASum += tempReal * 2.0;；periodWMASum += tempReal * 3.0;；periodWMASum += tempReal * 4.0;；trailingWMAValue = inReal[trailingWMAIdx++];；smoothedValue = periodWMASum * 0.1;；for( i = 0; i < 50; i += 1 )；本行取输出outInteger。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HT_TRENDMODE.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：HT_TRENDMODE.outInteger（无窗口参数）；追踪：PF00777；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_ht_trendmode_outinteger_64d', 'root_function': 'TA_HT_TRENDMODE', 'required_inputs': ['inReal'], 'parameters': {}, 'options': [], 'outputs': ['outInteger'], 'output_index': 0, 'output_label': 'outInteger', 'warmup': 63, 'kernel': 'kernel_e77673462dcbcfa7', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outInteger', 'int']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_ht_trendmode_outinteger_64d', {})
class Factor_talib_ht_trendmode_outinteger_64d(PublicFactor):
    name = 'talib_ht_trendmode_outinteger_64d'
    description = '源码核心递推表达式（完整分支/参数见链接）：double *smoothPrice = &local_smoothPrice[0];；maxIdx_smoothPrice = (int)(sizeof(local_smoothPrice)/sizeof(double))-1;；tempReal = atan(1);；rad2Deg = 45.0 / tempReal;；deg2Rad = 1.0 / rad2Deg;；constDeg2RadBy360 = tempReal * 8.0;；tempReal = inReal[today++];；periodWMASub += tempReal;；periodWMASum += tempReal * 2.0;；periodWMASum += tempReal * 3.0;；periodWMASum += tempReal * 4.0;；trailingWMAValue = inReal[trailingWMAIdx++];；smoothedValue = periodWMASum * 0.1;；for( i = 0; i < 50; i += 1 )；本行取输出outInteger。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HT_TRENDMODE.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：HT_TRENDMODE.outInteger（无窗口参数）；追踪：PF00777；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
