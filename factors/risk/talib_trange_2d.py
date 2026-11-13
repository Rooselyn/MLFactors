"""TA-Lib（技术指标及K线形态）

公式：max(H−L,abs(H−C[-1]),abs(L−C[-1]))；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：TRANGE.outReal（无窗口参数）；追踪：PF00866；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：FinTA:TR（无固定窗口）、Tulip Indicators:TR.tr（参数：none）、Pandas TA Classic:true_range（drift=None）、bta-lib:truerange.tr（）、PyTI:true_range.true_range（period等由调用方指定）、Stockstats:tr（窗口=需要调用方显式指定窗口）
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
SPEC = {'name': 'talib_trange_2d', 'root_function': 'TA_TRANGE', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {}, 'options': [], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 1, 'kernel': 'kernel_c5a666aa49913cf4', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_trange_2d', {})
class Factor_talib_trange_2d(PublicFactor):
    name = 'talib_trange_2d'
    description = 'max(H−L,abs(H−C[-1]),abs(L−C[-1]))；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：TRANGE.outReal（无窗口参数）；追踪：PF00866；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：FinTA:TR（无固定窗口）、Tulip Indicators:TR.tr（参数：none）、Pandas TA Classic:true_range（drift=None）、bta-lib:truerange.tr（）、PyTI:true_range.true_range（period等由调用方指定）、Stockstats:tr（窗口=需要调用方显式指定窗口）'
    INPUTS = INPUTS
    SPEC = SPEC
