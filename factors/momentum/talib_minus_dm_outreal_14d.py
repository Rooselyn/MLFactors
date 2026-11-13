"""TA-Lib（技术指标及K线形态）

公式：−DM=max(L[-1]−L,0)且L[-1]−L>H−H[-1]，否则0；按n平滑；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MINUS_DM.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：MINUS_DM.outReal（Time Period=14）；追踪：PF00818；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:dm（length=14, mamode='rma'）、Pandas TA Classic:minus_dm（length=14）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_minus_dm_outreal_14d', 'root_function': 'TA_MINUS_DM', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 13, 'kernel': 'kernel_27f59196360ede62', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_minus_dm_outreal_14d', {})
class Factor_talib_minus_dm_outreal_14d(PublicFactor):
    name = 'talib_minus_dm_outreal_14d'
    description = "−DM=max(L[-1]−L,0)且L[-1]−L>H−H[-1]，否则0；按n平滑；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_MINUS_DM.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：MINUS_DM.outReal（Time Period=14）；追踪：PF00818；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:dm（length=14, mamode='rma'）、Pandas TA Classic:minus_dm（length=14）"
    INPUTS = INPUTS
    SPEC = SPEC
