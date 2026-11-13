"""TA-Lib（技术指标及K线形态）

公式：ΣC[t−n+1+i]exp(−(i−offset(n−1))²/(2(n/sigma)²))/Σ权重；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ALMA.c)；默认参数={'Time Period': 9.0, 'Sigma': 6.0, 'Offset': 0.85}；完整数值核及辅助调用在实现附录展开。；原目录：ALMA.outReal（Time Period=9, Sigma=6.000000e+0, Offset=8.500000e-1）；追踪：PF00655；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_alma_outreal_9d', 'root_function': 'TA_ALMA', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 9.0, 'Sigma': 6.0, 'Offset': 0.85}, 'options': [9.0, 6.0, 0.85], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 8, 'kernel': 'kernel_3716eee0b9eee917', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInSigma', 'double'], ['optInOffset', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_alma_outreal_9d', {})
class Factor_talib_alma_outreal_9d(PublicFactor):
    name = 'talib_alma_outreal_9d'
    description = "ΣC[t−n+1+i]exp(−(i−offset(n−1))²/(2(n/sigma)²))/Σ权重；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ALMA.c)；默认参数={'Time Period': 9.0, 'Sigma': 6.0, 'Offset': 0.85}；完整数值核及辅助调用在实现附录展开。；原目录：ALMA.outReal（Time Period=9, Sigma=6.000000e+0, Offset=8.500000e-1）；追踪：PF00655；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
