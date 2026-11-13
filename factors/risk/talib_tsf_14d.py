"""TA-Lib（技术指标及K线形态）

公式：x=0,…,n−1，回归C=a+bx；输出a+bn；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：TSF.outReal（Time Period=14）；追踪：PF00869；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:tsf（length=14）、bta-lib:tsf.tsf（period=14）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_tsf_14d', 'root_function': 'TA_TSF', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 13, 'kernel': 'kernel_7a1cff05e4e7fe8f', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_tsf_14d', {})
class Factor_talib_tsf_14d(PublicFactor):
    name = 'talib_tsf_14d'
    description = "x=0,…,n−1，回归C=a+bx；输出a+bn；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：TSF.outReal（Time Period=14）；追踪：PF00869；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:tsf（length=14）、bta-lib:tsf.tsf（period=14）"
    INPUTS = INPUTS
    SPEC = SPEC
