"""TA-Lib（技术指标及K线形态）

公式：mean(C−O,n)；n=10；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：QSTICK.outReal（Time Period=10）；追踪：PF00833；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:qstick（length=10）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_qstick_10d', 'root_function': 'TA_QSTICK', 'required_inputs': ['inOpen', 'inClose'], 'parameters': {'Time Period': 10.0}, 'options': [10.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 9, 'kernel': 'kernel_87fea2a3fc708b7b', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_qstick_10d', {})
class Factor_talib_qstick_10d(PublicFactor):
    name = 'talib_qstick_10d'
    description = "mean(C−O,n)；n=10；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：QSTICK.outReal（Time Period=10）；追踪：PF00833；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:qstick（length=10）"
    INPUTS = INPUTS
    SPEC = SPEC
