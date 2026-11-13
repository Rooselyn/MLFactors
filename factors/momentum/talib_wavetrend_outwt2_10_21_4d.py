"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：double *wtBuffer = &local_wtBuffer[0];；wtBuffer = TA_Malloc( sizeof(double)*optInSignalPeriod );；beta1 = (double)(optInChannelPeriod - 1) / (double)(optInChannelPeriod + 1);；beta2 = (double)(optInAveragePeriod - 1) / (double)(optInAveragePeriod + 1);；ap = (inHigh[today] + inLow[today] + inClose[today]) / 3.0;；sumEsa = sumEsa + ap;；esa = sumEsa / optInChannelPeriod;；esa = fma(beta1, esa, k1 * ap);；sumD = sumD + dev;；d = sumD / optInChannelPeriod;；d = fma(beta1, d, k1 * dev);；scaledDev = 0.015 * d;；ci = num / scaledDev;；sumCi = sumCi + ci;；本行取输出outWT2。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_WAVETREND.c)；默认参数={'Channel Period': 10.0, 'Average Period': 21.0, 'Signal Period': 4.0}；完整数值核及辅助调用在实现附录展开。；原目录：WAVETREND.outWT2（Channel Period=10, Average Period=21, Signal Period=4）；追踪：PF00882；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_wavetrend_outwt2_10_21_4d', 'root_function': 'TA_WAVETREND', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Channel Period': 10.0, 'Average Period': 21.0, 'Signal Period': 4.0}, 'options': [10.0, 21.0, 4.0], 'outputs': ['outWT1', 'outWT2'], 'output_index': 1, 'output_label': 'outWT2', 'warmup': 41, 'kernel': 'kernel_c718bf759de11988', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInChannelPeriod', 'int'], ['optInAveragePeriod', 'int'], ['optInSignalPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outWT1', 'double'], ['outWT2', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_wavetrend_outwt2_10_21_4d', {})
class Factor_talib_wavetrend_outwt2_10_21_4d(PublicFactor):
    name = 'talib_wavetrend_outwt2_10_21_4d'
    description = "源码核心递推表达式（完整分支/参数见链接）：double *wtBuffer = &local_wtBuffer[0];；wtBuffer = TA_Malloc( sizeof(double)*optInSignalPeriod );；beta1 = (double)(optInChannelPeriod - 1) / (double)(optInChannelPeriod + 1);；beta2 = (double)(optInAveragePeriod - 1) / (double)(optInAveragePeriod + 1);；ap = (inHigh[today] + inLow[today] + inClose[today]) / 3.0;；sumEsa = sumEsa + ap;；esa = sumEsa / optInChannelPeriod;；esa = fma(beta1, esa, k1 * ap);；sumD = sumD + dev;；d = sumD / optInChannelPeriod;；d = fma(beta1, d, k1 * dev);；scaledDev = 0.015 * d;；ci = num / scaledDev;；sumCi = sumCi + ci;；本行取输出outWT2。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_WAVETREND.c)；默认参数={'Channel Period': 10.0, 'Average Period': 21.0, 'Signal Period': 4.0}；完整数值核及辅助调用在实现附录展开。；原目录：WAVETREND.outWT2（Channel Period=10, Average Period=21, Signal Period=4）；追踪：PF00882；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
