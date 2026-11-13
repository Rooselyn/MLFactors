"""TA-Lib（技术指标及K线形态）

公式：SAR递推，但多空初始AF、步长、上限、反转偏移分别参数化；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SAREXT.c)；默认参数={'Start Value': 0.0, 'Offset on Reverse': 0.0, 'AF Init Long': 0.02, 'AF Long': 0.02, 'AF Max Long': 0.2, 'AF Init Short': 0.02, 'AF Short': 0.02, 'AF Max Short': 0.2}；完整数值核及辅助调用在实现附录展开。；原目录：SAREXT.outReal（Start Value=0.000000e+0, Offset on Reverse=0.000000e+0, AF Init Long=2.000000e-2, AF Long=2.000000e-2, AF Max Long=2.000000e-1, AF Init Short=2.000000e-2, AF Short=2.000000e-2, AF Max Short=2.000000e-1）；追踪：PF00845；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:sarext（startvalue=None, offsetonreverse=None, accelerationinitlong=None, accelerationlong=None, accelerationmaxlong=None, accelerationinitshort=None, accelerationshort=None, accelerationmaxshort=None）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_sarext_outreal_alld', 'root_function': 'TA_SAREXT', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Start Value': 0.0, 'Offset on Reverse': 0.0, 'AF Init Long': 0.02, 'AF Long': 0.02, 'AF Max Long': 0.2, 'AF Init Short': 0.02, 'AF Short': 0.02, 'AF Max Short': 0.2}, 'options': [0.0, 0.0, 0.02, 0.02, 0.2, 0.02, 0.02, 0.2], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 1, 'kernel': 'kernel_9ffc2b4f5efe92f7', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInStartValue', 'double'], ['optInOffsetOnReverse', 'double'], ['optInAccelerationInitLong', 'double'], ['optInAccelerationLong', 'double'], ['optInAccelerationMaxLong', 'double'], ['optInAccelerationInitShort', 'double'], ['optInAccelerationShort', 'double'], ['optInAccelerationMaxShort', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_sarext_outreal_alld', {})
class Factor_talib_sarext_outreal_alld(PublicFactor):
    name = 'talib_sarext_outreal_alld'
    description = "SAR递推，但多空初始AF、步长、上限、反转偏移分别参数化；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_SAREXT.c)；默认参数={'Start Value': 0.0, 'Offset on Reverse': 0.0, 'AF Init Long': 0.02, 'AF Long': 0.02, 'AF Max Long': 0.2, 'AF Init Short': 0.02, 'AF Short': 0.02, 'AF Max Short': 0.2}；完整数值核及辅助调用在实现附录展开。；原目录：SAREXT.outReal（Start Value=0.000000e+0, Offset on Reverse=0.000000e+0, AF Init Long=2.000000e-2, AF Long=2.000000e-2, AF Max Long=2.000000e-1, AF Init Short=2.000000e-2, AF Short=2.000000e-2, AF Max Short=2.000000e-1）；追踪：PF00845；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:sarext（startvalue=None, offsetonreverse=None, accelerationinitlong=None, accelerationlong=None, accelerationmaxlong=None, accelerationinitshort=None, accelerationshort=None, accelerationmaxshort=None）"
    INPUTS = INPUTS
    SPEC = SPEC
