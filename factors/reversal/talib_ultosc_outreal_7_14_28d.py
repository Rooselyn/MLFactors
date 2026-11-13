"""TA-Lib（技术指标及K线形态）

公式：BP=C−min(L,C[-1])；TR=max(H,C[-1])−min(L,C[-1])；100×(4ΣBP_n1/ΣTR_n1+2ΣBP_n2/ΣTR_n2+ΣBP_n3/ΣTR_n3)/7；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ULTOSC.c)；默认参数={'First Period': 7.0, 'Second Period': 14.0, 'Third Period': 28.0}；完整数值核及辅助调用在实现附录展开。；原目录：ULTOSC.outReal（First Period=7, Second Period=14, Third Period=28）；追踪：PF00872；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:ULTOSC.ultosc（参数：short_period, medium_period, long_period）、Pandas TA Classic:uo（fast=7, slow=28）
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
SPEC = {'name': 'talib_ultosc_outreal_7_14_28d', 'root_function': 'TA_ULTOSC', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'First Period': 7.0, 'Second Period': 14.0, 'Third Period': 28.0}, 'options': [7.0, 14.0, 28.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 28, 'kernel': 'kernel_c15c24423676fde2', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod1', 'int'], ['optInTimePeriod2', 'int'], ['optInTimePeriod3', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_ultosc_outreal_7_14_28d', {})
class Factor_talib_ultosc_outreal_7_14_28d(PublicFactor):
    name = 'talib_ultosc_outreal_7_14_28d'
    description = "BP=C−min(L,C[-1])；TR=max(H,C[-1])−min(L,C[-1])；100×(4ΣBP_n1/ΣTR_n1+2ΣBP_n2/ΣTR_n2+ΣBP_n3/ΣTR_n3)/7；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ULTOSC.c)；默认参数={'First Period': 7.0, 'Second Period': 14.0, 'Third Period': 28.0}；完整数值核及辅助调用在实现附录展开。；原目录：ULTOSC.outReal（First Period=7, Second Period=14, Third Period=28）；追踪：PF00872；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:ULTOSC.ultosc（参数：short_period, medium_period, long_period）、Pandas TA Classic:uo（fast=7, slow=28）"
    INPUTS = INPUTS
    SPEC = SPEC
