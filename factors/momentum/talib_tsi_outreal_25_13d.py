"""TA-Lib（技术指标及K线形态）

公式：100×EMA(EMA(ΔC,slow),fast)/EMA(EMA(abs(ΔC),slow),fast)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_TSI.c)；默认参数={'First Smoothing Period': 25.0, 'Second Smoothing Period': 13.0}；完整数值核及辅助调用在实现附录展开。；原目录：TSI.outReal（First Smoothing Period=25, Second Smoothing Period=13）；追踪：PF00870；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:tsi（fast=13, slow=25, signal=13, scalar=100, mamode='ema'）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_tsi_outreal_25_13d', 'root_function': 'TA_TSI', 'required_inputs': ['inReal'], 'parameters': {'First Smoothing Period': 25.0, 'Second Smoothing Period': 13.0}, 'options': [25.0, 13.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 37, 'kernel': 'kernel_66035461463a705c', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInFirstPeriod', 'int'], ['optInSecondPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_tsi_outreal_25_13d', {})
class Factor_talib_tsi_outreal_25_13d(PublicFactor):
    name = 'talib_tsi_outreal_25_13d'
    description = "100×EMA(EMA(ΔC,slow),fast)/EMA(EMA(abs(ΔC),slow),fast)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_TSI.c)；默认参数={'First Smoothing Period': 25.0, 'Second Smoothing Period': 13.0}；完整数值核及辅助调用在实现附录展开。；原目录：TSI.outReal（First Smoothing Period=25, Second Smoothing Period=13）；追踪：PF00870；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:tsi（fast=13, slow=25, signal=13, scalar=100, mamode='ema'）"
    INPUTS = INPUTS
    SPEC = SPEC
