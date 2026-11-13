"""TA-Lib（技术指标及K线形态）

公式：SAR_t=SAR_{t−1}+AF×(EP−SAR_{t−1})；新极值提高AF，穿越前轨反转并重置EP/AF；上下界限制按源码；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SAR.c)；默认参数={'Acceleration Factor': 0.02, 'AF Maximum': 0.2}；完整数值核及辅助调用在实现附录展开。；原目录：SAR.outReal（Acceleration Factor=2.000000e-2, AF Maximum=2.000000e-1）；追踪：PF00844；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_sar_outreal_alld', 'root_function': 'TA_SAR', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Acceleration Factor': 0.02, 'AF Maximum': 0.2}, 'options': [0.02, 0.2], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 1, 'kernel': 'kernel_69ac9d7b1810ecc9', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInAcceleration', 'double'], ['optInMaximum', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_sar_outreal_alld', {})
class Factor_talib_sar_outreal_alld(PublicFactor):
    name = 'talib_sar_outreal_alld'
    description = "SAR_t=SAR_{t−1}+AF×(EP−SAR_{t−1})；新极值提高AF，穿越前轨反转并重置EP/AF；上下界限制按源码；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SAR.c)；默认参数={'Acceleration Factor': 0.02, 'AF Maximum': 0.2}；完整数值核及辅助调用在实现附录展开。；原目录：SAR.outReal（Acceleration Factor=2.000000e-2, AF Maximum=2.000000e-1）；追踪：PF00844；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
