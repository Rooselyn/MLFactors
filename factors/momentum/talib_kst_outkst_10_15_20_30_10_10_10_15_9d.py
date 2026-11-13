"""TA-Lib（技术指标及K线形态）

公式：Σ_{i=1}^4 i×SMA(ROC(C,roc_i),sma_i)；Signal=SMA(KST,signal)；本行取输出outKST。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_KST.c)；默认参数={'ROC-1 Period': 10.0, 'ROC-2 Period': 15.0, 'ROC-3 Period': 20.0, 'ROC-4 Period': 30.0, 'SMA-1 Period': 10.0, 'SMA-2 Period': 10.0, 'SMA-3 Period': 10.0, 'SMA-4 Period': 15.0, 'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：KST.outKST（ROC-1 Period=10, ROC-2 Period=15, ROC-3 Period=20, ROC-4 Period=30, SMA-1 Period=10, SMA-2 Period=10, SMA-3 Period=10, SMA-4 Period=15, Signal Period=9）；追踪：PF00787；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：TA-Lib（技术指标及K线形态）:KSTEXT.outKST（ROC-1 Period=10, ROC-2 Period=15, ROC-3 Period=20, ROC-4 Period=30, MA-1 Period=10, MA-2 Period=10, MA-3 Period=10, MA-4 Period=15, Signal Period=9, ROC MA=0, Signal MA=0）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_kst_outkst_10_15_20_30_10_10_10_15_9d', 'root_function': 'TA_KST', 'required_inputs': ['inReal'], 'parameters': {'ROC-1 Period': 10.0, 'ROC-2 Period': 15.0, 'ROC-3 Period': 20.0, 'ROC-4 Period': 30.0, 'SMA-1 Period': 10.0, 'SMA-2 Period': 10.0, 'SMA-3 Period': 10.0, 'SMA-4 Period': 15.0, 'Signal Period': 9.0}, 'options': [10.0, 15.0, 20.0, 30.0, 10.0, 10.0, 10.0, 15.0, 9.0], 'outputs': ['outKST', 'outKSTSignal'], 'output_index': 0, 'output_label': 'outKST', 'warmup': 52, 'kernel': 'kernel_0b47fbb704355a33', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInROC1Period', 'int'], ['optInROC2Period', 'int'], ['optInROC3Period', 'int'], ['optInROC4Period', 'int'], ['optInSMA1Period', 'int'], ['optInSMA2Period', 'int'], ['optInSMA3Period', 'int'], ['optInSMA4Period', 'int'], ['optInSignalPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outKST', 'double'], ['outKSTSignal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_kst_outkst_10_15_20_30_10_10_10_15_9d', {})
class Factor_talib_kst_outkst_10_15_20_30_10_10_10_15_9d(PublicFactor):
    name = 'talib_kst_outkst_10_15_20_30_10_10_10_15_9d'
    description = "Σ_{i=1}^4 i×SMA(ROC(C,roc_i),sma_i)；Signal=SMA(KST,signal)；本行取输出outKST。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_KST.c)；默认参数={'ROC-1 Period': 10.0, 'ROC-2 Period': 15.0, 'ROC-3 Period': 20.0, 'ROC-4 Period': 30.0, 'SMA-1 Period': 10.0, 'SMA-2 Period': 10.0, 'SMA-3 Period': 10.0, 'SMA-4 Period': 15.0, 'Signal Period': 9.0}；完整数值核及辅助调用在实现附录展开。；原目录：KST.outKST（ROC-1 Period=10, ROC-2 Period=15, ROC-3 Period=20, ROC-4 Period=30, SMA-1 Period=10, SMA-2 Period=10, SMA-3 Period=10, SMA-4 Period=15, Signal Period=9）；追踪：PF00787；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：TA-Lib（技术指标及K线形态）:KSTEXT.outKST（ROC-1 Period=10, ROC-2 Period=15, ROC-3 Period=20, ROC-4 Period=30, MA-1 Period=10, MA-2 Period=10, MA-3 Period=10, MA-4 Period=15, Signal Period=9, ROC MA=0, Signal MA=0）"
    INPUTS = INPUTS
    SPEC = SPEC
