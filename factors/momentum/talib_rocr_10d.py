"""TA-Lib（技术指标及K线形态）

公式：C/C[-n]；n=10；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：ROCR.outReal（Time Period=10）；追踪：PF00837；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:rocr（length=10）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_rocr_10d', 'root_function': 'TA_ROCR', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 10.0}, 'options': [10.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 10, 'kernel': 'kernel_7785faee304b6256', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_rocr_10d', {})
class Factor_talib_rocr_10d(PublicFactor):
    name = 'talib_rocr_10d'
    description = "C/C[-n]；n=10；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：ROCR.outReal（Time Period=10）；追踪：PF00837；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:rocr（length=10）"
    INPUTS = INPUTS
    SPEC = SPEC
