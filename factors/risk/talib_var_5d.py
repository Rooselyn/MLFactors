"""TA-Lib（技术指标及K线形态）

公式：mean((C−mean(C,n))²,n)，ddof=0；n=5；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 5.0, 'Deviations': 1.0}；完整数值核及辅助调用在实现附录展开。；原目录：VAR.outReal（Time Period=5, Deviations=1.000000e+0）；追踪：PF00873；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：bta-lib:var.var（period=5, ddof=0）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_var_5d', 'root_function': 'TA_VAR', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 5.0, 'Deviations': 1.0}, 'options': [5.0, 1.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 4, 'kernel': 'kernel_6f63b277a648d395', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInNbDev', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_var_5d', {})
class Factor_talib_var_5d(PublicFactor):
    name = 'talib_var_5d'
    description = "mean((C−mean(C,n))²,n)，ddof=0；n=5；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 5.0, 'Deviations': 1.0}；完整数值核及辅助调用在实现附录展开。；原目录：VAR.outReal（Time Period=5, Deviations=1.000000e+0）；追踪：PF00873；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：bta-lib:var.var（period=5, ddof=0）"
    INPUTS = INPUTS
    SPEC = SPEC
