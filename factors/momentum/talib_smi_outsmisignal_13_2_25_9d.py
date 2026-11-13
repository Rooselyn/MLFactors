"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：betaSlow = (double)(optInSlowPeriod - 1) / (double)(optInSlowPeriod + 1);；betaFast = (double)(optInFastPeriod - 1) / (double)(optInFastPeriod + 1);；betaSignal = (double)(optInSignalPeriod - 1) / (double)(optInSignalPeriod + 1);；today = trailingIdx + (optInTimePeriod - 1);；num = inClose[today] - (highest + lowest) * 0.5;；sumSlowNum = sumSlowNum + num;；sumSlowDen = sumSlowDen + den;；emaSlowNum = sumSlowNum / optInSlowPeriod;；emaSlowDen = sumSlowDen / optInSlowPeriod;；emaSlowNum = fma(betaSlow, emaSlowNum, kSlow * num);；emaSlowDen = fma(betaSlow, emaSlowDen, kSlow * den);；sumFastNum = sumFastNum + emaSlowNum;；sumFastDen = sumFastDen + emaSlowDen;；emaFastNum = sumFastNum / optInFastPeriod;；本行取输出outSMISignal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SMI.c)；默认参数={'Time Period': 13.0, 'Fast Period': 2.0, 'Slow Period': 25.0, 'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：SMI.outSMISignal（Time Period=13, Fast Period=2, Slow Period=25, Signal Period=9）；追踪：PF00848；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_smi_outsmisignal_13_2_25_9d', 'root_function': 'TA_SMI', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 13.0, 'Fast Period': 2.0, 'Slow Period': 25.0, 'Signal Period': 9.0}, 'options': [13.0, 2.0, 25.0, 9.0], 'outputs': ['outSMI', 'outSMISignal'], 'output_index': 1, 'output_label': 'outSMISignal', 'warmup': 45, 'kernel': 'kernel_cee0943908b1e04d', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['optInFastPeriod', 'int'], ['optInSlowPeriod', 'int'], ['optInSignalPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outSMI', 'double'], ['outSMISignal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_smi_outsmisignal_13_2_25_9d', {})
class Factor_talib_smi_outsmisignal_13_2_25_9d(PublicFactor):
    name = 'talib_smi_outsmisignal_13_2_25_9d'
    description = "源码核心递推表达式（完整分支/参数见链接）：betaSlow = (double)(optInSlowPeriod - 1) / (double)(optInSlowPeriod + 1);；betaFast = (double)(optInFastPeriod - 1) / (double)(optInFastPeriod + 1);；betaSignal = (double)(optInSignalPeriod - 1) / (double)(optInSignalPeriod + 1);；today = trailingIdx + (optInTimePeriod - 1);；num = inClose[today] - (highest + lowest) * 0.5;；sumSlowNum = sumSlowNum + num;；sumSlowDen = sumSlowDen + den;；emaSlowNum = sumSlowNum / optInSlowPeriod;；emaSlowDen = sumSlowDen / optInSlowPeriod;；emaSlowNum = fma(betaSlow, emaSlowNum, kSlow * num);；emaSlowDen = fma(betaSlow, emaSlowDen, kSlow * den);；sumFastNum = sumFastNum + emaSlowNum;；sumFastDen = sumFastDen + emaSlowDen;；emaFastNum = sumFastNum / optInFastPeriod;；本行取输出outSMISignal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SMI.c)；默认参数={'Time Period': 13.0, 'Fast Period': 2.0, 'Slow Period': 25.0, 'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：SMI.outSMISignal（Time Period=13, Fast Period=2, Slow Period=25, Signal Period=9）；追踪：PF00848；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
