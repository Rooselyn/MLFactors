"""TA-Lib（技术指标及K线形态）

公式：RS=log(H/O)log(H/C)+log(L/O)log(L/C)，按窗口聚合及开平方；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ROGERSSATCHELL.c)；默认参数={'Time Period': 10.0, 'Annualization': 252.0}；完整数值核及辅助调用在实现附录展开。；原目录：ROGERSSATCHELL.outReal（Time Period=10, Annualization=2.520000e+2）；追踪：PF00839；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_rogerssatchell_outreal_10d', 'root_function': 'TA_ROGERSSATCHELL', 'required_inputs': ['inOpen', 'inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 10.0, 'Annualization': 252.0}, 'options': [10.0, 252.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 9, 'kernel': 'kernel_7ee26e0c07f1f2fd', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['optInAnnualization', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_rogerssatchell_outreal_10d', {})
class Factor_talib_rogerssatchell_outreal_10d(PublicFactor):
    name = 'talib_rogerssatchell_outreal_10d'
    description = "RS=log(H/O)log(H/C)+log(L/O)log(L/C)，按窗口聚合及开平方；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ROGERSSATCHELL.c)；默认参数={'Time Period': 10.0, 'Annualization': 252.0}；完整数值核及辅助调用在实现附录展开。；原目录：ROGERSSATCHELL.outReal（Time Period=10, Annualization=2.520000e+2）；追踪：PF00839；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
