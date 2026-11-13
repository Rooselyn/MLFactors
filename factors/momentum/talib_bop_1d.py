"""TA-Lib（技术指标及K线形态）

公式：(C−O)/(H−L)；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：BOP.outReal（无窗口参数）；追踪：PF00670；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：FinTA:BOP（无固定窗口）、Tulip Indicators:BOP.bop（参数：none）、Pandas TA Classic:bop（scalar=1）、bta-lib:bop.bop（）、Stockstats:bop（窗口=需要调用方显式指定窗口）
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
SPEC = {'name': 'talib_bop_1d', 'root_function': 'TA_BOP', 'required_inputs': ['inOpen', 'inHigh', 'inLow', 'inClose'], 'parameters': {}, 'options': [], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_faac0ac35f895d3a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_bop_1d', {})
class Factor_talib_bop_1d(PublicFactor):
    name = 'talib_bop_1d'
    description = '(C−O)/(H−L)；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：BOP.outReal（无窗口参数）；追踪：PF00670；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：FinTA:BOP（无固定窗口）、Tulip Indicators:BOP.bop（参数：none）、Pandas TA Classic:bop（scalar=1）、bta-lib:bop.bop（）、Stockstats:bop（窗口=需要调用方显式指定窗口）'
    INPUTS = INPUTS
    SPEC = SPEC
